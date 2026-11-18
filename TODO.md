# Mind2Machine — Project To-Do List

Source: `plan for project.txt`. Check items off as completed.

## Phase 1 — Project Setup
- [x] Create GitHub repository
- [x] Add `.gitignore`
- [x] Add `README.md`
- [ ] Set up React + Vite (frontend/)
- [ ] Set up FastAPI (backend/)
- [ ] Install PostgreSQL locally
- [ ] Connect backend to PostgreSQL
- [ ] Configure environment variables (`.env`, `.env.example`)

## Phase 2 — AI Integration
- [x] Choose an eligible small model (Groq `openai/gpt-oss-20b` as primary; switched to Gemini `gemini-3.8-flash` for the live demo after Groq's free-tier daily quota (200k tokens) proved too tight under repeated testing - both are supported, `create_model_service()` auto-picks Gemini whenever a real `GEMINI_API_KEY` is set, Groq otherwise)
- [x] Test API access
- [ ] Test rate limits
- [x] Test response speed (~1.4s per call observed)
- [x] Implement structured JSON extraction
- [x] Implement actual token tracking (no estimates)

## Phase 3 — Core Planning Engine
- [x] Build message reader (message_service.py — parses sender/date/message blocks, preserves original text, fingerprints for dedup)
- [x] Build fact extraction (reading_agent.py via ModelService)
- [x] Build constraint storage (all 14 tables created in PostgreSQL: events, messages, extracted_facts, constraints, decisions, venues, schedules, food_plans, judges, judge_assignments, budget_items, plans, model_traces, validation_results)
- [x] Build conflict detection (conflict_detector.py) — explicit approval, authority, feasibility, budget overrun covered; recency/consistency/supersession still TODO
- [x] Build five planning modules (venue, schedule, food, judging, budget agents)
- [x] Build validation engine (validation_engine.py) — all six checks implemented

## Phase 4 — Budget and Scheduling
- [x] Implement all calculations in Python (not the LLM)
- [x] Implement venue selection logic (capacity + generator + cost) — verified: selects Hall B, matches plan's sample result
- [x] Implement food calculations (headcount × price + delivery) — verified: Basic lunch, Rs. 144,000
- [x] Implement judge assignment (teams/judge cap, honorarium, late-arrival reassignment note) — verified: 17 required vs 20 confirmed, Rs. 100,000 honorarium
- [x] Implement schedule validation (milestones, prayer break, duration-consistency flag) — verified: flags the 4hr-vs-6.5hr inconsistency
- [x] Implement budget validation (≤ Rs. 650,000) — verified end-to-end: Rs. 524,000 committed, Rs. 126,000 remaining, matches plan's sample pack exactly

## Phase 5 — Update Engine
- [x] Implement message deduplication (fingerprint-based, message_service.diff_new_messages)
- [x] Implement incremental updates (update_engine.py) — verified: printing correction gives Rs. 529,000/Rs. 121,000, matching the plan's worked example exactly
- [x] Implement dependency detection (dependency_engine.py — keyword-based affected-area prediction, verified 3/3 correct on practice messages)
- [ ] Implement plan versioning (preserve previous plan versions) — update engine mutates in place; no DB-backed version history yet
- [x] Enforce 5-model-call / 1-minute update limits (checked in update_engine.py; 3 calls / 5.5s observed on real data)

## Phase 6 — Dashboard (React)
- [x] Sidebar + Overview page (wired to /api/dashboard, verified via curl)
- [x] Message Center page (wired to /api/messages, verified via curl) — upload/add-message UI not built yet, only read view
- [x] Venue Planning page (wired to /api/plan/current)
- [x] Schedule Planning page (wired to /api/plan/current)
- [x] Food Planning page (wired to /api/plan/current)
- [x] Judging Management page (wired to /api/plan/current)
- [x] Budget Management page (wired to /api/budget, verified via curl)
- [x] AI Agent Trace page (wired to /api/trace)
- [x] Validation & Rejections page (wired to /api/validation)
- [x] Plan History page (wired to /api/plan/history)
- [ ] Change-prediction panel UI (backend produces predictions in update_engine.py; not yet surfaced in the dashboard)

Note: could not get a persistent local dev server running in this sandboxed shell to do a live browser visual check (background processes get killed between tool calls here). Backend endpoints were verified correct via curl; frontend build passes TypeScript checks. Recommend running `npm run dev` + `uvicorn backend.main:app --reload` yourself and clicking through once.

## Phase 7 — Integration & Testing
- [x] Connect all frontend pages to FastAPI endpoints
- [ ] Test original 8 sample messages → complete valid plan
- [x] Test unseen-style messages (4 invented messages, new senders/phrasing never in the sample pack — extraction stayed correct, including appropriate low confidence 0.6 on an unverified rumor)
- [x] Test Roman Urdu message (both the real msg 4 and a synthetic "sirf 140 students... pehle 150 bataye the" — both extracted correctly)
- [x] Test wrong/conflicting messages → correct rejection + explanation (DJ request, insufficient food boxes)
- [x] Test update limits and timeouts (3 calls / 5.5s on real practice pack, well under 5-call/60s cap)
- [x] Test insufficient food quantity (177 people, 100 boxes → reject) — verified, correctly rejected
- [x] Test venue capacity too small → reject (synthetic test: all options below required capacity → selected=None, all rejected with reasons)
- [x] Test budget exceeding limit → reject/revise (synthetic test: confirmed Rs.200k request against Rs.650k cap with Rs.500k already committed → rejected)
- [x] Test late judge arrival → reassignment (reassignment note generated by judging_agent)
- [x] Test stale/old quotation does not override newer fact — **found and fixed a real bug**: venue/food agents picked cheapest-ever quote regardless of date, so a stale cheap quote could beat a newer correct one. Now dedupes by venue/package name, latest message wins (synthetic tests confirm; real sample pack numbers unchanged — it happened to not expose the bug there)
- [x] Test unauthorized budget change is not silently approved (DJ request correctly held pending; also synthetic test with an unauthorized sender confirming spend)
- [ ] Test multiple changes in one message update all affected areas
- [ ] Test missing model API key / timeout / malformed response (error handling) — not yet implemented; a Groq API failure currently propagates as an unhandled exception
- [ ] Test database connection failure handling — not yet implemented; relies on SQLAlchemy's default exception behavior
- [x] Test duplicate message handling (fingerprint-based dedup verified in message_service tests)
- [x] Verify trace completeness (every call_number/model/area/tokens/duration field populated and persisted correctly)

Known limitation: when a message gives a per-unit cost + separate quantity (e.g. "Rs 3,000 each" x 5), budget_agent currently records only the unit cost if that fact were ever accepted as a line item, not cost×quantity. Not yet hit by any real test message (the one example found was correctly held pending anyway), but worth fixing if an unseen message exercises it.

## Phase 8 — Final Submission
- [x] Verify single-command execution (`python run.py`) for initial run and updates — ran live 4 times total, consistent correct result each time (3 clean passes after fixing the bugs below)
- [x] Verify final plan + trace export (JSON) — final_plan.json, execution_trace.json, report.json all written correctly; no CSV export built (plan allows JSON or CSV)
- [x] Run full end-to-end test (< 2 minutes) — 25-40s per run, even with rate-limit retries
- [x] Push final code — pushed through this point
- [ ] Record final commit hash — do this right before your actual submission, not now (code will keep changing)
- [ ] Confirm git status is clean at code freeze (1:25 PM) — do this right before submission

## Final Submission Tracker (13/17)
- [x] GitHub repository created and code pushed
- [x] PostgreSQL connection tested
- [x] Model access verified (Groq `openai/gpt-oss-20b`, free tier) — small-model *eligibility bonus* still needs organizers to confirm Groq/this model is on their approved list
- [x] Original message pack processed successfully
- [x] All five planning areas generated
- [x] Six validation checks passing — verified consistently across 3 repeated live runs, not just once
- [x] Wrong message correctly rejected with explanation (DJ request, insufficient food boxes)
- [x] Incremental update tested (printing correction → Rs. 529,000/Rs. 121,000, matches plan exactly)
- [x] Update finishes within 1 minute and 5 model calls
- [ ] Full run finishes within 2 minutes - true on Groq (~25-40s observed); **on Gemini it took 2m37s** on an 11-message run, over the brief's 2-minute guideline. Team decision: prioritize Gemini's reliability over this limit for the live demo given Groq's quota was exhausted. If judges enforce the 2-minute limit strictly, switch back to Groq (remove/empty `GEMINI_API_KEY` in `.env`) once its quota has refilled.
- [x] Actual (not estimated) token counts recorded
- [x] Final plan saved
- [x] Complete trace saved
- [ ] Dashboard working — built and wired to real API, but not yet visually confirmed in an actual browser (see Phase 6 note)
- [ ] All team members understand the architecture — only your team can confirm this
- [ ] Final commit hash recorded — do at actual submission time
- [ ] Git status clean at code freeze — do at actual submission time

## Bugs found and fixed by running live repeatedly (not caught by a single run)
These only showed up because the pipeline was re-run against the real API multiple times, since a small model's output isn't perfectly consistent run to run:
1. Groq's free-tier rate limit (8000 TPM) crashed the whole run with an unhandled exception — fixed with retry/backoff in model_service.py.
2. The model occasionally used a synonym key (`number_of_judges` instead of `judges_confirmed`), silently zeroing judge capacity — fixed with a key-alias fallback plus a stricter prompt.
3. The model occasionally set `budget_all_in` to the expense amount itself on an ordinary line item (not just the real ceiling statement), which got excluded from spend by a truthy check — fixed with a strict `is True` check plus a clearer prompt explanation.
4. `is_confirmed_decision` was never actually defined in the prompt, so a stated correction ("the bill came in at Rs 15,000") was sometimes misread as an unapproved request — fixed by defining the field explicitly.

**Takeaway for your team**: this is a free small model, not a deterministic function - the same message can occasionally extract slightly differently between runs. The fixes above closed the specific failure modes found, but if you see a run produce a different number than expected, re-run it before assuming the number is wrong, and check `outputs/execution_trace.json` for what the model actually returned on that call.
