import json
import time
from dataclasses import dataclass
from typing import Literal

from groq import APIConnectionError, APITimeoutError, Groq, RateLimitError

Area = Literal["reading", "venue", "schedule", "food", "judging", "budget"]

MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 3


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
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = Groq(api_key=api_key)
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
            except (RateLimitError, APITimeoutError, APIConnectionError) as exc:
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
