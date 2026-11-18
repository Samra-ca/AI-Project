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
- [x] Choose an eligible small model (Groq `openai/gpt-oss-20b`, free tier)
- [x] Test API access
- [ ] Test rate limits
- [x] Test response speed (~1.4s per call observed)
- [x] Implement structured JSON extraction
- [x] Implement actual token tracking (no estimates)

## Phase 3 — Core Planning Engine
- [x] Build message reader (message_service.py — parses sender/date/message blocks, preserves original text, fingerprints for dedup)
- [x] Build fact extraction (reading_agent.py via ModelService)
- [x] Build constraint storage (all 14 tables created in PostgreSQL: events, messages, extracted_facts, constraints, decisions, venues, schedules, food_plans, judges, judge_assignments, budget_items, plans, model_traces, validation_results)
- [ ] Build conflict detection (conflict_detector.py) — authority, recency, approval, feasibility, capacity, budget, completeness, consistency
- [ ] Build five planning modules (venue, schedule, food, judging, budget agents)
- [ ] Build validation engine (validation_engine.py)

## Phase 4 — Budget and Scheduling
- [ ] Implement all calculations in Python (not the LLM)
- [ ] Implement venue selection logic (capacity + generator + cost)
- [ ] Implement food calculations (headcount × price + delivery)
- [ ] Implement judge assignment (teams/judge cap, honorarium, late-arrival reassignment)
- [ ] Implement schedule validation (milestones, prayer break, duration-consistency flag)
- [ ] Implement budget validation (≤ Rs. 650,000)

## Phase 5 — Update Engine
- [ ] Implement message deduplication
- [ ] Implement incremental updates (update_engine.py)
- [ ] Implement dependency detection (affected-areas prediction)
- [ ] Implement plan versioning (preserve previous plan versions)
- [ ] Enforce 5-model-call / 1-minute update limits

## Phase 6 — Dashboard (React)
- [ ] Sidebar + Overview page
- [ ] Message Center page (upload .txt, add message, status)
- [ ] Venue Planning page
- [ ] Schedule Planning page
- [ ] Food Planning page
- [ ] Judging Management page
- [ ] Budget Management page
- [ ] AI Agent Trace page
- [ ] Validation & Rejections page
- [ ] Plan History page
- [ ] Change-prediction panel (expected vs actual model calls)

## Phase 7 — Integration & Testing
- [ ] Connect all frontend pages to FastAPI endpoints
- [ ] Test original 8 sample messages → complete valid plan
- [ ] Test unseen-style messages
- [ ] Test Roman Urdu message
- [ ] Test wrong/conflicting messages → correct rejection + explanation
- [ ] Test update limits and timeouts
- [ ] Test insufficient food quantity (177 people, 100 boxes → reject)
- [ ] Test venue capacity too small → reject
- [ ] Test budget exceeding limit → reject/revise
- [ ] Test late judge arrival → reassignment
- [ ] Test stale/old quotation does not override newer fact
- [ ] Test unauthorized budget change is not silently approved
- [ ] Test multiple changes in one message update all affected areas
- [ ] Test missing model API key / timeout / malformed response (error handling)
- [ ] Test database connection failure handling
- [ ] Test duplicate message handling
- [ ] Verify trace completeness

## Phase 8 — Final Submission
- [ ] Verify single-command execution (`python run.py`) for initial run and updates
- [ ] Verify final plan + trace export (JSON/CSV)
- [ ] Run full end-to-end test (< 2 minutes)
- [ ] Push final code
- [ ] Record final commit hash
- [ ] Confirm git status is clean at code freeze (1:25 PM)

## Final Submission Tracker (0/17)
- [ ] GitHub repository created and code pushed
- [ ] PostgreSQL connection tested
- [ ] Model access and small-model eligibility verified
- [ ] Original message pack processed successfully
- [ ] All five planning areas generated
- [ ] Six validation checks passing (correct figures, within budget, venue fits, schedule valid, enough judges, all five areas covered)
- [ ] Wrong message correctly rejected with explanation
- [ ] Incremental update tested
- [ ] Update finishes within 1 minute and 5 model calls
- [ ] Full run finishes within 2 minutes
- [ ] Actual (not estimated) token counts recorded
- [ ] Final plan saved
- [ ] Complete trace saved
- [ ] Dashboard working
- [ ] All team members understand the architecture
- [ ] Final commit hash recorded
- [ ] Git status clean at code freeze
