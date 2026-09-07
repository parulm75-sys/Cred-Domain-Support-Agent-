from agent.schema import AgentResponse,AskRequest
from pydantic import BaseModel
from agent.graph import chat
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def root():
    return {"status": "ok"}
@app.post("/ask", response_model=AgentResponse)
def ask(request: AskRequest):
    return chat(request.query,request.conversation_id)[-1]