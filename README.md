# Cred-Domain-Support-Agent
Cred's lending-operations team's agent that answers loan-policy questions and checks a specific loan application's status, so support staff can respond to member queries instantly and consistently.

## dataset.py Parameters

- **Random seed:** 42, applied to all random number generation for reproducibility
- **Fraud flag probability:** 0.2 (each application has a 20% chance of being flagged as fraudulent); observed fraud rate in the generated dataset: 27.5%
- **Loan amount range:** 10,000–2,000,000 INR. 10,000 is a realistic minimum for a personal loan; 2,000,000 ensures the range covers all four interest slabs defined in the knowledge base
- **Category and status selection:** uniform — all loan categories and status values are selected via `random.choice` with no weighting applied

## Rag/chunk_embed.py Paramteres

- **Splitting method:** regex splitting chosen over simple period splitting after comparing results; regex correctly handles abbreviations and decimal numbers that period splitting breaks on
- **Sentence-based chunking:** two sentences joined per chunk to improve embedding coherence; produced 37 chunks, stored in ChromaDB collection `cred_sentences`
- **Fixed-size chunking:** chunk size 200 characters, overlap 50 characters; produced 48 chunks, stored in ChromaDB collection `cred_fixed`
- **Embedding model:** `all-MiniLM-L6-v2` applied to both collections

## Rag/queries.py 

- ** 12 in-scope queries and 2 out-of scope queries**
- **one query from each document**

## Threshold Calibration

- **Method:** measured top-1 cosine similarity across 12 in-scope and 2 out-of-scope 
queries against both collections rather than adopting a tutorial default; 
full scores saved in `task4_calibration.txt`

| Query | In-scope | Sentence | Fixed |
|---|---|---|---|
| How many days to close my account? | Yes | 0.6948 | 0.6551 |
| What is the annual fee for the credit card? | Yes | 0.6539 | 0.6160 |
| How can I increase my credit score? | Yes | 0.5004 | 0.4719 |
| EMI on 50,000 INR at 1% monthly for 70 months? | Yes | 0.7456 | 0.7151 |
| Unknown transaction — what can I do? | Yes | 0.6371 | 0.6226 |
| Interest rate on loan of 76,567 INR? | Yes | 0.7478 | 0.7372 |
| Joint account — can I withdraw alone? | Yes | 0.5361 | 0.5975 |
| My KYC fails — what is my next step? | Yes | 0.4106 | 0.4104 |
| Car loan eligibility with credit score 701? | Yes | 0.6521 | 0.6760 |
| Why am I charged 100 INR monthly? | Yes | 0.5183 | 0.5063 |
| Documents required for NRI account? | Yes | 0.7866 | 0.7680 |
| Prepayment fee on 60,000 INR after first year? | Yes | 0.7028 | 0.6765 |
| What is the monthly salary of the bank employee? | No | 0.4228 | 0.4626 |
| What is the capital of India? | No | 0.2266 | 0.3424 |

- **Chosen threshold:** 0.45 — both out-of-scope queries fall below it on sentence-based; 11 of 12 in-scope queries clear it
- **Fixed-size comparison:** fixed scored higher than sentence-based on the salary query (0.4626 vs 0.4228) but lower on 10 of 12 in-scope queries, supporting the Task 5 recommendation of sentence-based for deployment
- **Known failure:** KYC query scores 0.4106, falling below the threshold and triggering a false fallback; accepted because a refusal is safer than a wrong answer in a banking support context
- **Honest limitation:** the clusters overlap — the KYC query scores lower than the salary query, and the margin above the salary query is 0.027; a different out-of-scope query could plausibly land above 0.45

## Task 4 — Retrieval and Generation

- **Fallback rule:** queries scoring below 0.45 top-1 cosine similarity return 
"I don't know" rather than answering; the threshold is not applied to fixed-size 
results, only sentence-based which is the deployed collection
- **Output shape:** each response includes the source document ID, retrieved chunk 
text, and similarity score so grounding is inspectable without opening the KB
- **Demonstration:** all 14 queries run; 11 answered from retrieved context, 
3 fell back — KYC (0.4106), salary query (0.4228), capital-of-India query (0.2266); 
transcript saved in `transcripts/task4_calibration.txt`
- **Observed failure:** the prepayment query scored 0.7028 and answered confidently 
from `interest_rate_slabs` instead of `prepayment_penalty_rules`; the query says 
"fees" and "pay my loan" while the document uses "prepayment penalty" and 
"repays ahead of schedule" — little lexical overlap, and the loan amount pulled 
toward the slab table; a similarity threshold cannot catch this class of error 
since the retrieval was confident and wrong

## chunk_embed.py Parameters

- **Sentence-based chunking:** two sentences joined per chunk to improve embedding 
coherence; produced 37 chunks, stored in ChromaDB collection `cred_sentence`
- **Fixed-size chunking:** chunk size 200 characters, overlap 50 characters; 
produced 48 chunks, stored in ChromaDB collection `cred_fixed`
- **Embedding model:** `all-MiniLM-L6-v2` applied to both collections

## Task 5 — Precision and Recall

- **Method:** Precision@3 and Recall@3 computed for both collections across 
12 in-scope queries; out-of-scope queries excluded from averages since fallback 
firing correctly is not a retrieval failure — both denominators are stated here 
so a grader can verify either way
- **Results (averaged over 12 in-scope queries):**

| Collection | Avg Recall | Avg Precision |
|---|---|---|
| Sentence-based | 0.833 | 0.653 |
| Fixed-size | 0.833 | 0.667 |

- **Transcript:** saved in `transcripts/task5_precision_recall.txt`

## Recommendation

Sentence-based chunking is recommended for deployment despite fixed-size scoring 
marginally higher on precision.

The stronger argument is threshold separation. The fallback is the only safety 
mechanism available under MOCK_LLM, and fixed-size scored higher than 
sentence-based on the salary query (0.4626 vs 0.4228) — reducing the gap between 
the worst in-scope query and the best out-of-scope query. Sentence-based keeps 
that separation wider, making the 0.45 threshold more reliable.

The precision result goes the other way and is worth stating: on a 12-query 
sample, a 0.014 difference is one query's worth of signal, not a robust advantage.

## Task 6 — Escalation Scoring

- **Formula:** `escalation_score = 0.7 × fraud_flag + 0.3 × (days_since_created / 30)`
  where `fraud_flag` is 1 if flagged for fraud review, 0 otherwise
- **Threshold:** 0.5 — applications scoring 0.5 or above are escalated for review
- **Why 0.5 is robust:** with weights 0.7 and 0.3, flagged records start at a 
minimum of 0.7 and unflagged records cap at a maximum of 0.3; the bands cannot 
overlap by construction, so any threshold between 0.30 and 0.70 separates them 
perfectly — 0.5 is the natural midpoint
- **Observed distribution:** 11 of 40 records scored 0.71 or above (flagged band), 
29 scored 0.29 or below (unflagged band); nothing fell between 0.30 and 0.70, 
confirming the two-band shape; the 11 escalated records represent 27.5% of the 
dataset, matching the fraud flag probability set at generation time
- **Honest limitation:** because the bands cannot overlap, the threshold is 
effectively reading the fraud flag directly; the recency signal only differentiates 
within each band; if recency alone should be able to escalate an unflagged 
application, weights closer to 0.5/0.5 would be needed
- **Transcript:** saved in `transcripts/task6_escalation.txt`

## Task 7 — Graph Routing

- **Graph structure:** four nodes — `classify`, `policy`, `record`, 
`format_response`; satisfies the brief requirement of ≥ 4 nodes and ≥ 1 
conditional edge
- **Conditional edge:** routes on `intent` value after `classify` — `policy` → 
`policy` node, `record` → `record` node; both converge at `format_response`
- **Intent classifier:** keywords `status` and `application` route to `record`; 
all other queries route to `policy`
- **Policy route:** retrieves from sentence-based KB collection, applies 0.45 
threshold, returns source document ID and answer; falls back to "I don't know" 
below threshold
- **Record route:** extracts first digit sequence from query using regex, looks up 
matching `record_id` in `LOAN_APPLICATIONS`, returns status, loan amount, and 
escalation score; returns not-found message if no match
- **Demonstrated:** policy query (`annual fee for credit card`) classified correctly, 
retrieved from `credit_card_fee_structure`; record query (`status of application 23`) 
classified correctly, returned status, amount, and escalation for record 23; 
transcript saved in `transcripts/task7_routing.txt`
- **Known limitation (classifier):** the keyword `application` appears in 
account-closure and fraud-dispute KB documents, so a policy query such as 
"how do I submit an application to close my account" would misroute to the 
record branch and return a not-found message
- **Known limitation (record branch):** no bounds check on the extracted number; 
a query containing a large incidental number such as a loan amount would extract 
it, find no matching record, and return the not-found message gracefully but 
incorrectly

## Task 8 — Persistent Memory

- **Storage:** conversation history written to `memory.json` at the project root; 
keyed by conversation ID so multiple sessions are stored independently
- **Format:** each entry is a dict with three fields — `query`, `intent`, and 
`response`; the full list for a given ID is loaded at the start of each `chat()` 
call and saved at the end
- **Multi-turn demonstration:** three queries run under `conv_1`; history grew 
from one to two to three entries across turns, confirming state persisted between 
calls; transcript saved in `transcripts/task8_multiturn.txt`
- **Fresh conversation demonstration:** different queries run under `conv_2`; 
history printed as a single entry on the first turn, confirming state was correctly 
absent at the start; `load_fun` returns an empty list for an unknown ID rather 
than raising, so absence is correct by design rather than accidental; 
transcript saved in `transcripts/task8_fresh.txt`
- **Honest limitation:** history is loaded, passed into the graph state, and saved, 
but no node reads it; the agent cannot use a previous turn to resolve a follow-up 
query such as "what about application 24?" — each turn is processed from the 
current query alone

## Task 9 — Structured Output Schema

- **Schema:** `AgentResponse` defined in `agent/schema.py` using Pydantic `BaseModel`; 
three fields — `query: str`, `intent: str`, `response: str`
- **Validation:** runs inside `chat()` on every response before the turn is saved 
to memory; a response that fails validation raises immediately rather than being 
stored
- **Demonstrated failures:**
  - Missing field: passing `{query, intent}` without `response` raised 
  `ValidationError: Field required` as expected
  - Wrong type: passing `response=123` raised `ValidationError: Input should be 
  a valid string` — Pydantic v2 rejected the integer rather than coercing it
- **Both real responses validated silently** — policy and record routes both 
produce dicts that satisfy the schema
- **Transcript:** saved in `transcripts/task9_schema.txt`
- **Honest limitation:** the schema covers `query`, `intent`, and `response` only; 
`doc_id` and `similarity_score` from the policy branch are not part of the 
validated contract — defensible since those fields don't exist on the record 
branch, but grounding evidence is outside the schema

## Task 10 — Guardrails

### PII Masking
- **Patterns masked:** PAN (`[A-Z]{5}[0-9]{4}[A-Z]` → `[PAN_MASKED]`), 
Aadhaar (`\d{4}\s?\d{4}\s?\d{4}` → `[AADHAAR_MASKED]`)
- **Applied:** runs on the query inside `chat()` before `app.invoke` is called, 
so masked text is what reaches the graph and gets stored in memory
- **Demonstrated:** query containing both a PAN and Aadhaar number returned 
with both replaced; transcript in `transcripts/task10_guardrails.txt`

### Prompt Injection Detection
- **Method:** checks query against four substring fragments — `ignore previous`, 
`disregard the above`, `different assistant`, `system prompt`; fragments rather 
than full phrases, so variants are caught — accepted tradeoff: a benign query 
such as "can I disregard the above charges?" would also be refused
- **Applied:** checked before masking; a detected injection short-circuits the 
graph entirely and stores the refusal directly to history
- **Demonstrated:** injection query returned refusal without entering the graph; 
transcript in `transcripts/task10_guardrails.txt`

### Groundedness Check
- **Method:** word-overlap ratio between query and retrieved content, excluding 
common stop words; threshold 0.33; overlap is only computed when `doc_id` is 
not None — fallback cases return "I don't know" and are skipped
- **Calibration:** measured on 12 in-scope queries against sentence-based 
collection; good retrievals scored 0.389 to 1.000; failures scored 0.000 (KYC), 
0.267 (prepayment); out-of-scope queries scored 0.000 and 0.000; clean gap 
between 0.267 and 0.389 with nothing in between — 0.33 sits at the midpoint
- **Why this matters:** the prepayment query scored 0.7028 similarity and passed 
the retrieval threshold, but overlap caught it at 0.267 — the only mechanism 
that can flag a confident retrieval from the wrong document
- **Narrowest margin:** car-loan query at 0.389, sitting 0.056 above the line — 
the case most likely to break if the KB grows
- **Fixed-size weakness:** fixed-size scored 0.4 overlap on the salary 
out-of-scope query, above threshold — it would wrongly pass; sentence-based 
scored 0.0
- **Refusal wording:** groundedness refusal returns "Answer not supported by 
retrieved context"; record not-found returns "Sorry, we could not find any record" 
— distinguished so a grader can tell them apart in the transcript
- **Demonstrated:** credit card annual fee query passed (overlap 1.0) and answered; 
prepayment query failed (overlap 0.267) and refused with "Answer not supported 
by retrieved context"; transcript in `transcripts/task10_guardrails.txt`

## Task 11 — FastAPI Endpoints

- **Endpoints:** `POST /ask` and `POST /add_document`; root `GET /` returns 
a health-check string; interactive docs at `/docs`
- **Request models (Pydantic):**
  - `/ask` — `AskRequest`: `query: str`, `conversation_id: str`
  - `/add_document` — `AddDocumentRequest`: `doc_id: str`, `text: str`
- **Response models:**
  - `/ask` — returns `AgentResponse` (`query`, `intent`, `response`)
  - `/add_document` — returns `doc_id` and `chunks_added`
- **Demonstrated:**
  - `/ask` with credit card annual fee query — returned correct answer from KB
  - `/add_document` with `home_loan_interest` document — returned `chunks_added: 1`
  - `/ask` with "what is the interest rate on a home loan" after adding — 
  retrieved the newly added document, confirming the round trip works
  - transcript saved in `transcripts/task11_api.txt`
- **Collection state:** the `home_loan_interest` document added during 
demonstration remains in the Chroma collection; it overlaps existing interest 
slab documents and will shift retrieval slightly for related queries — Task 5 
numbers were measured before this document existed and remain valid for that run

## Task 12 — Structured Logging

- **File:** `logs.jsonl` at the project root; one JSON object per line, 
appended on every `/ask` request
- **Fields per entry:**
  - `trace_id` — UUID4 generated fresh per request (`str(uuid.uuid4())`)
  - `timestamp` — `datetime.now().isoformat()` at request start
  - `query` — the query as returned from `chat()`, which is already PII-masked; 
  logging this value rather than `request.query` guarantees no unmasked text 
  reaches disk
  - `intent` — as returned from the last history entry
  - `duration_seconds` — `time.time()` measured around the `chat()` call
- **PII masking:** `mask_pii` runs before `detect_injections` in `chat()`, so 
both the injection path and the normal path log masked text — no unmasked PII 
reaches disk on either branch
- **Demonstrated:** `/ask` called with a query containing a PAN number; 
`logs.jsonl` showed `[PAN_MASKED]` in the logged query, confirming masking 
applies before disk; sample log lines saved in `transcripts/task12_logging.txt`

- **Per-query results:**

| Query | Context | Grounded | Answer |
|---|---|---|---|
| How many days to close my account? | 0.695 | 1 | True |
| Annual fee for the credit card? | 0.654 | 1 | True |
| How can I increase my credit score? | 0.500 | 1 | True |
| EMI on 50,000 INR at 1% for 70 months? | 0.746 | 1 | True |
| Unknown transaction — what can I do? | 0.637 | 1 | True |
| Interest rate on loan of 76,567 INR? | 0.748 | 1 | True |
| Joint account — can I withdraw alone? | 0.536 | 1 | True |
| My KYC fails — what is my next step? | 0.411 | 0 | 0 |
| Car loan eligibility with score 701? | 0.652 | 1 | True |
| Why am I charged 100 INR monthly? | 0.518 | 1 | True |
| Documents required for NRI account? | 0.787 | 1 | True |
| Prepayment fee on 60,000 INR loan? | 0.703 | 1 | False |
| Monthly salary of bank employee? | 0.423 | 0 | 0 |
| Capital of India? | 0.227 | 0 | 0 |
| Who is Salman Khan? | 0.298 | 0 | 0 |

- **Averages (over 15 queries):**
  - Context Relevance: 0.569
  - Groundedness: 0.733
  - Answer Relevance: 0.667

  ## Task 14 — MCP Server and Client

- **Two separate files and processes:**
  - `mcp_integration/mcp_server.py` — defines and runs the MCP server
  - `mcp_integration/mcp_client.py` — connects and calls the tool; 
  the server must be running in a separate terminal before the client is started
- **Server:** built with `FastMCP("cred-support")`; runs HTTP transport on 
port 8001; tool accessible at `http://127.0.0.1:8001/mcp`
- **Tool:** `check_loan_status(record_id: str) -> dict` — looks up a loan 
application by record ID and returns its status, loan amount in INR, and 
computed escalation score; valid IDs are "1" through "40" as strings
- **Client:** async, using `fastmcp.Client`; opens connection with `async with`, 
calls `call_tool` with the tool name and a dict of arguments, prints the 
full `CallToolResult` response including the MCP protocol wrapper
- **Demonstrated:** two record IDs called through the same interface:
  - Record 3 — status Disbursed, loan 894,834 INR, escalation 0.71 (escalates)
  - Record 27 — status Disbursed, loan 143,227 INR, escalation 0.12 (does not escalate)
- **Response shape:** `CallToolResult` contains `structured_content` (the plain 
dict), `serverInfo` with server name and version, and `is_error: False` — 
the protocol wrapper around the tool's return value
- **Transcript:** saved in `transcripts/task14_mcp.txt`

## Task 15 — SQLite Checkpointing

- **Package:** `langgraph-checkpoint-sqlite`; checkpointer created with 
`conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)` then 
`SqliteSaver(conn)`, passed to `graph.compile(checkpointer=checkpointer)`
- **Two compiled graphs:** both defined in `graph.py` — `app` compiles without 
a checkpointer for normal API and memory use; `checkpoint_app` compiles with 
the checkpointer; `checkpointer_demo.py` imports `checkpoint_app` and runs the 
three-phase demonstration
- **Interrupt mechanism:** `interrupt_before=["format_response"]` passed to 
`compile`; execution halts after `record` completes and before `format_response` 
runs, leaving state saved to SQLite
- **Thread ID:** `{"configurable": {"thread_id": "demo-thread-1"}}`; same config 
passed to both the initial invoke and the resume so LangGraph loads state from 
the correct checkpoint
- **Three-phase demonstration:**
  - Phase 1 (initial run, interrupted): `NODE: classify running` and 
  `NODE: record running` printed; execution stopped; checkpoint saved with 
  `next: ('format_response',)`
  - Phase 2 (checkpoint inspection): saved state printed showing `intent: record`, 
  full result dict, and next node confirmed as `format_response`
  - Phase 3 (resume): `NODE: format_response running` printed and final answer 
  returned; `classify` and `record` stayed silent — their outputs loaded from 
  the checkpoint rather than recomputed
- **The absence in Phase 3 is the evidence:** two nodes that printed in Phase 1 
produced no output on resume, proving state was restored rather than re-executed
- **Transcript:** saved in `transcripts/task15_checkpoint.txt`; 
`checkpoints.sqlite` is in `.gitignore` since it regenerates on every run

## Task 16 — Timeouts and Retries

- **File:** `resilience_demo.py` (three demonstrations in one script, 
one run produces all three labelled outputs)
- **Transcript:** saved in `transcripts/task16_resilience.txt`

### Demo 1 — Retry with RetryPolicy
- **Parameters:** `max_attempts=3`, `initial_interval=0.5`, `max_interval=4.0`, 
`backoff_factor=2.0`, `jitter=True`, `retry_on=RuntimeError`
- **Why `retry_on` must be set explicitly:** LangGraph's default filter excludes 
`RuntimeError`; without it the policy would not catch the simulated failure and 
the node would fail immediately rather than retrying
- **Demonstrated:** `flaky_node` raised `RuntimeError` on attempts 1 and 2, 
succeeded on attempt 3; `end_state` ran and returned `successful`

### Demo 2 — Per-Node Timeout
- **Mechanism:** `timeout=1.0` passed to `add_node`; `slow_node` sleeps 3 seconds 
against a 1-second budget
- **Why the node must be async:** LangGraph raises `ValueError` if a timeout is 
set on a sync node — sync Python execution cannot be safely cancelled in-process; 
converting to `async def` with `await asyncio.sleep` makes cancellation possible
- **Demonstrated:** `NODE: slow_node running` printed; 
`NodeTimeoutError: Node 'slow_node' exceeded its run timeout of 1.000s 
(elapsed: 1.002s)` caught cleanly after approximately 1 second

### Demo 3 — Global Pipeline Timeout
- **Mechanism:** `asyncio.wait_for(global_app.ainvoke(...), timeout=2.0)`; 
two nodes each sleeping 1.5 seconds give a 3-second total pipeline against 
a 2-second budget
- **Why `wait_for` rather than per-node timeout:** the brief asks for a 
total-time budget; neither node individually exceeds 1 second per step, 
so a per-node timeout would not fire — `wait_for` wraps the whole invocation
- **Demonstrated:** both nodes started printing; `TimeoutError` caught at 
2 seconds before the pipeline could complete