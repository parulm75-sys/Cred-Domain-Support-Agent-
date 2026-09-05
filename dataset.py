import random
from collections import Counter
random.seed(42)
LOAN_APPLICATIONS=[]
for i in range(1,41):
    data={
        "record_id":str(i),
        "category":random.choice(["Personal Loan","Home Loan","Auto Loan","Education Loan","Business Loan"]),
        "status" : random.choice(["Submitted","Under Review","Approved","Rejected","Disbursed"]),
        # the minimum range is chosen 10000 because less than that, someone will not apply for the loan while maximum 20 lks is because beacuase it covers all interest slabs
        "loan_amount_inr": random.randint(10000,2000000),
        "days_since_created":random.randint(0,30),
        "flagged_for_fraud_review":random.choices([True, False], weights=[0.2, 0.8])[0]
    }
    LOAN_APPLICATIONS.append(data)
count=Counter(record["category"] for record in LOAN_APPLICATIONS)
