# Cred-Domain-Support-Agent
Cred's lending-operations team's agent that answers loan-policy questions and checks a specific loan application's status, so support staff can respond to member queries instantly and consistently.

## dataset.py Parameters

- **Random seed:** 42, applied to all random number generation for reproducibility
- **Fraud flag probability:** 0.2 (each application has a 20% chance of being flagged as fraudulent); observed fraud rate in the generated dataset: 27.5%
- **Loan amount range:** 10,000–2,000,000 INR. 10,000 is a realistic minimum for a personal loan; 2,000,000 ensures the range covers all four interest slabs defined in the knowledge base
- **Category and status selection:** uniform — all loan categories and status values are selected via `random.choice` with no weighting applied