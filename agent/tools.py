from dataset import LOAN_APPLICATIONS
def check_loan_application_status(record_id: str) -> dict:
    for app  in LOAN_APPLICATIONS:
        if (app["record_id"]==record_id):
            score=escalation_score(app["flagged_for_fraud_review"],app["days_since_created"])
            return {
                "status": app["status"],
                "loan_amount_inr": app["loan_amount_inr"],
                "escalation_score": score
            }
    return None
def escalation_score(flag: bool,days: int):
    return 0.7*flag +0.3*(days/30)
if __name__=="__main__":
    for loan in LOAN_APPLICATIONS:
        print(check_loan_application_status(loan["record_id"]))
