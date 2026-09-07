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
def overlap(query,response):
    common_words=["what","is","a","my","the","how"]
    words=re.findall(r"[a-z]+", query.lower())
    check=re.findall(r"[a-z]+", response.lower())
    count=0
    sum=0
    for w in words:
        if w not in common_words:
            if w in check:
                count+=1
            sum+=1
    if  sum!=0 and count/sum>=0.33:
        return True
    else:
        return False

if __name__=="__main__":
    print(mask_pii("my PAN is ABCDE1234F and aadhaar 1234 5678 9012"))