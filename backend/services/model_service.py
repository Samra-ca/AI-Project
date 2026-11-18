import json
import os
import time
from dataclasses import dataclass
from typing import Literal

Area = Literal["reading", "venue", "schedule", "food", "judging", "budget"]

MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 3

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


@dataclass
class TraceEntry:
    call_number: int
    model_name: str
    area: Area
    input: str
    output: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    duration_ms: int
    reason: str


class ModelService:
    """Wraps the small-LLM provider call and records every call with its
    actual provider-reported token usage, matching the required trace format.
    Supports Groq or Gemini (via Gemini's OpenAI-compatible endpoint) -
    whichever provider is configured.
    """

    def __init__(self, api_key: str, model_name: str, provider: str = "groq") -> None:
        self._provider = provider
        if provider == "gemini":
            from openai import (
                APIConnectionError,
                APITimeoutError,
                OpenAI,
                RateLimitError,
            )

            self._client = OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)
            self._retry_exceptions = (RateLimitError, APITimeoutError, APIConnectionError)
        else:
            from groq import APIConnectionError, APITimeoutError, Groq, RateLimitError

            self._client = Groq(api_key=api_key)
            self._retry_exceptions = (RateLimitError, APITimeoutError, APIConnectionError)

        self._model_name = model_name
        self._trace: list[TraceEntry] = []

    def call_json(
        self, area: Area, system_prompt: str, user_input: str, reason: str
    ) -> dict:
        start = time.perf_counter()
        response = self._call_with_retry(system_prompt, user_input)
        duration_ms = int((time.perf_counter() - start) * 1000)

        output_text = response.choices[0].message.content or "{}"
        usage = response.usage

        self._trace.append(
            TraceEntry(
                call_number=len(self._trace) + 1,
                model_name=self._model_name,
                area=area,
                input=user_input,
                output=output_text,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                duration_ms=duration_ms,
                reason=reason,
            )
        )
        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            return {"facts": [], "parse_error": "Model response was not valid JSON."}

    def _call_with_retry(self, system_prompt: str, user_input: str):
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return self._client.chat.completions.create(
                    model=self._model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0,
                )
            except self._retry_exceptions as exc:
                last_error = exc
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
        raise last_error  # noqa: B904

    @property
    def trace(self) -> list[TraceEntry]:
        return list(self._trace)

    def summary(self) -> dict:
        by_area: dict[str, int] = {}
        for entry in self._trace:
            by_area[entry.area] = by_area.get(entry.area, 0) + 1
        return {
            "total_calls": len(self._trace),
            "calls_by_area": by_area,
            "total_input_tokens": sum(e.input_tokens for e in self._trace),
            "total_output_tokens": sum(e.output_tokens for e in self._trace),
            "total_tokens": sum(e.total_tokens for e in self._trace),
        }


def create_model_service() -> ModelService:
    """Picks the provider automatically: prefers Gemini whenever a real
    (non-placeholder) GEMINI_API_KEY is configured, otherwise falls back to
    Groq. This is the single place that decides which provider is used, so
    every call site (run.py, main.py, tests) stays in sync without needing
    to be edited individually.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    is_placeholder = gemini_key.lower().startswith("yahan_")
    if gemini_key and not is_placeholder:
        return ModelService(
            api_key=gemini_key,
            model_name=os.environ.get("GEMINI_MODEL_NAME", "gemini-3.8-flash"),
            provider="gemini",
        )
    return ModelService(
        api_key=os.environ["GROQ_API_KEY"],
        model_name=os.environ.get("MODEL_NAME", "openai/gpt-oss-20b"),
        provider="groq",
    )
