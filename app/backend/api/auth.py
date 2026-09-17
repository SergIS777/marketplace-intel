from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    store_id: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    if request.email == "test@example.com" and request.password == "test123":
        return LoginResponse(access_token="mock_jwt_token_12345", user_id="user_123", store_id="store_1")
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/auth/register")
async def register(request: RegisterRequest):
    return {"message": "User registered", "user_id": "user_new_456", "store_id": "store_new_789"}

@router.get("/auth/me")
async def get_current_user():
    return {"user_id": "user_123", "email": "test@example.com", "name": "Тестовый пользователь", "store_id": "store_1"}
