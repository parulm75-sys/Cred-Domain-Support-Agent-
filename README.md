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