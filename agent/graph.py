from typing import TypedDict
from langgraph.graph import StateGraph, END
from RAG.retrieve import generate, sen_collection
from agent.tools import check_loan_application_status
import re
from agent import memory
from agent.schema import AgentResponse

class AgentState(TypedDict):
    query: str
    intent: str
    result: dict
    history:list
    response: str
def classify(state):
    check=state["query"].lower()
    policy=["status","application"]
    if(policy[0] in check or policy[1] in check):
        return{"intent":"record"}
    else:
        return{"intent":"policy"}
def policy(state):
    return {"result":generate(state["query"],sen_collection)}
def record(state):
    match = re.search(r"\d+", state["query"])
    if(match!=None):
        number=match.group()
        return {"result":check_loan_application_status(number)}
    else:
        return{"result":None} 
def format_response(state):
    result=state["result"]
    intent=state["intent"]
    text=""
    if(result==None):
        return{"response": "Sorry, we could not find any record"}
    if(intent=="policy"):
        text="You can find your answer below:\n"+"\n".join(state["result"]["content"])
    else:
        text=f"The status of the record is {result['status']}, the outstanding loan amount is {result['loan_amount_inr']} and escalation required: "
        if(result["escalation_score"]>=0.5):
            text+="Yes"
        else:
            text+="No"
    return {"response": text}
def route(state):
    if state["intent"] == "record":
        return "record"
    return "policy"
graph = StateGraph(AgentState)
graph.set_entry_point("classify")
graph.add_node("classify", classify)
graph.add_node("policy", policy)
graph.add_node("record", record)
graph.add_node("format_response", format_response)
graph.add_edge("policy", "format_response")
graph.add_edge("record", "format_response")
graph.add_edge("format_response", END)
graph.add_conditional_edges("classify", route)
app = graph.compile()
def chat(query, conversation_id):
    history=memory.load_fun(conversation_id)
    result=app.invoke({"query":query,
                       "history":history})
    validated = AgentResponse(**result)
    history.append({"query":result["query"],
                    "intent":result["intent"],
                    "response":result["response"]
                    })
    memory.save_fun(conversation_id,history)
    return history
if __name__ == "__main__":
    print("=== Conv 4: Policy Query ===")
    print(chat("What is the annual fee for the credit card?", "conv_4"))
    
    print("\n=== Conv 5: Record Query ===")
    print(chat("What is the status of application 33?", "conv_5"))
    
    print("\n=== Test 1: Missing Field Error ===")
    try:
        # Intentionally missing 'response'
        AgentResponse(query="Test query", intent="policy")
    except Exception as e:
        print("Validation failed as expected:")
        print(e)
        
    print("\n=== Test 2: Invalid Field Type Error ===")
    try:
        # Intentionally passing integer for string 'response'
        AgentResponse(query="Test query", intent="policy", response=123)
    except Exception as e:
        print("Validation failed as expected:")
        print(e)
    