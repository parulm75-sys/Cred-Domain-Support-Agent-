from pydantic import BaseModel

class AgentResponse(BaseModel):
    query: str
    intent: str
    response: str
class AskRequest(BaseModel):
    query: str
    conversation_id: str