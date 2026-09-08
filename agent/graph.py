from typing import TypedDict
from langgraph.graph import StateGraph, END
from RAG.retrieve import generate, sen_collection
from agent.tools import check_loan_application_status
import re
from agent import memory
from agent.schema import AgentResponse
from agent.guardrails import mask_pii,detect_injections,overlap
from langgraph.pregel import RetryPolicy
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(conn)
class AgentState(TypedDict):
    query: str
    intent: str
    result: dict
    history:list
    response: str
def classify(state):
    print("NODE: classify running")
    check=state["query"].lower()
    policy=["status","application"]
    if(policy[0] in check or policy[1] in check):
        return{"intent":"record"}
    else:
        return{"intent":"policy"}
def policy(state):
    print("NODE: policy running")
    return {"result":generate(state["query"],sen_collection)}
def record(state):
    print("NODE: record running")
    match = re.search(r"\d+", state["query"])
    if(match!=None):
        number=match.group()
        return {"result":check_loan_application_status(number)}
    else:
        return{"result":None} 
def format_response(state):
    print("NODE: format_response running")
    result=state["result"]
    intent=state["intent"]
    text=""
    if(result==None):
        return{"response": "Sorry, we could not find any record"}
    if(intent=="policy"):
        if(overlap(state["query"]," ".join(result["content"]))):
            text="You can find your answer below:\n"+"\n".join(state["result"]["content"])
        else:
             return{"response": "Answer not supported by retrieved context"}
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
checkpoint_app = graph.compile(checkpointer=checkpointer, interrupt_before=["format_response"])
def chat(query, conversation_id):
    history=memory.load_fun(conversation_id)
    query=mask_pii(query)
    if(detect_injections(query)):
        history.append({"query":query,
                        "intent": "injection Detected",
                        "response":"Sorry, I cannot further assist with any of your query"
                        })
    else:
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
    print(chat("What is the annual fee for the credit card?", "conv_9"))
    print(chat("What is the fees, I am looking at if I want to pay my 60000 INR loan after the first year?", "conv_8"))
    
    