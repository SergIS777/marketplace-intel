rom fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from services.mock_store import mock_store_service

router = APIRouter()

class Review(BaseModel):
    id: str
    nm_id: int
    rating: int
    text: str
    author: str
    date: str
    answered: bool
    answer: Optional[str] = None

@router.get("/reviews", response_model=List[Review])
async def get_reviews(unanswered_only: bool = False):
    return mock_store_service.get_reviews("store_1", unanswered_only=unanswered_only)

@router.get("/reviews/unanswered", response_model=List[Review])
async def get_unanswered_reviews():
    return mock_store_service.get_reviews("store_1", unanswered_only=True)

@router.post("/reviews/{review_id}/answer")
async def answer_review(review_id: str, answer: str):
    return {"message": "Answer posted", "review_id": review_id, "answer": answer}
