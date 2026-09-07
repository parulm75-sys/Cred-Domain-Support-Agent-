from agent.schema import AgentResponse,AskRequest,AddDocumentRequest
from pydantic import BaseModel
from agent.graph import chat
from fastapi import FastAPI
from RAG.chunk_embed import embed_doc,add_sen_collection

app = FastAPI()
@app.get("/")
def root():
    return {"status": "ok"}
@app.post("/ask", response_model=AgentResponse)
def ask(request: AskRequest):
    return chat(request.query,request.conversation_id)[-1]
@app.post("/add_document")
def add_document(request: AddDocumentRequest):
    lists=embed_doc({request.doc_id:request.text})
    add_sen_collection(lists[0], lists[1], lists[2])
    return {"doc_id": request.doc_id, "chunks_added": len(lists[1])}