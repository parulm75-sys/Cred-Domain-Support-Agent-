from pydantic import BaseModel

class AgentResponse(BaseModel):
    query: str
    intent: str
    response: str