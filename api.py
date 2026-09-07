from agent.schema import AgentResponse,AskRequest,AddDocumentRequest
from pydantic import BaseModel
from agent.graph import chat
from fastapi import FastAPI
from RAG.chunk_embed import embed_doc,add_sen_collection
from agent.logging_setup import log_request
import time
import uuid
app = FastAPI()
@app.get("/")
def root():
    return {"status": "ok"}
@app.post("/ask", response_model=AgentResponse)
def ask(request: AskRequest):
    trace_id=str(uuid.uuid4())
    start=time.time()
    response=chat(request.query,request.conversation_id)[-1]
    duration=time.time()-start
    log_request(trace_id, response["query"], response["intent"], duration)
    return response
@app.post("/add_document")
def add_document(request: AddDocumentRequest):
    lists=embed_doc({request.doc_id:request.text})
    add_sen_collection(lists[0], lists[1], lists[2])
    return {"doc_id": request.doc_id, "chunks_added": len(lists[1])}