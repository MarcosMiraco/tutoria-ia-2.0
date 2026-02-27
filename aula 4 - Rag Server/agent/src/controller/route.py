from fastapi import APIRouter
from pydantic import BaseModel
from service.qa import QAService

router = APIRouter()

service = QAService()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    response: str
    status: str


@router.post("/ask", response_model=AskResponse)
async def ask_endpoint(payload: AskRequest):
    try:
        answer = service.handle_question(payload.question)
        return { "response": answer, "status": "success" }
    except Exception as e:
        return { "response": str(e), "status": "error" }