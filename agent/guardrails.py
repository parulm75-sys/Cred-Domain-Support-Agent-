import re
def mask_pii(query):
    text = re.sub(r"[A-Z]{5}[0-9]{4}[A-Z]", "[PAN_MASKED]", query)
    text = re.sub(r"\d{4}\s?\d{4}\s?\d{4}", "[AADHAAR_MASKED]", text)
    return text
def detect_injections(query):
    injection=["ignore previous", "disregard the above", "different assistant", "system prompt"]
    check=query.lower()
    for i in injection:
        if i in check:
            return True
    return False
if __name__=="__main__":
    print(mask_pii("my PAN is ABCDE1234F and aadhaar 1234 5678 9012"))