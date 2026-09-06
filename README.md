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