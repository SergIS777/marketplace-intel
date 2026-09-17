from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from services.mock_store import mock_store_service

router = APIRouter()

class Store(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: str
    stats: dict

class Product(BaseModel):
    nm_id: int
    name: str
    price: int
    stock: int
    sales_last_30d: int
    rating: float
    reviews_count: int

@router.get("/store", response_model=Store)
async def get_store():
    return mock_store_service.get_store("store_1")

@router.get("/store/products", response_model=List[Product])
async def get_products():
    return mock_store_service.get_products("store_1")

@router.get("/store/stats")
async def get_store_stats():
    store = mock_store_service.get_store("store_1")
    return {"store_id": store["id"], **store["stats"]}
