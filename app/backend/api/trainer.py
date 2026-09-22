from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.llm_service import llm_service  # <-- добавили импорт

router = APIRouter()

# === МОДЕЛИ ЗАПРОСОВ И ОТВЕТОВ (без изменений) ===

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    quest_id: str
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    reply: str
    quest_id: str

class QuestSubmitRequest(BaseModel):
    quest_id: str
    proof_text: str

class QuestSubmitResponse(BaseModel):
    is_approved: bool
    feedback: str
    xp_awarded: int
    next_quest_id: Optional[str]
    level_up: bool

# === МОК-ДАННЫЕ КВЕСТОВ (без изменений) ===

MOCK_QUESTS = {
    "quest_1": {"title": "Анкета продавца", "description": "Расскажи о целях и интересах — подберём нишу", "xp": 20, "next": "quest_2"},
    "quest_2": {"title": "Выбор ниши", "description": "AI-рекомендация по 6 параметрам рынка", "xp": 30, "next": "quest_3"},
    "quest_3": {"title": "Регистрация WB Partners", "description": "Создай профиль продавца по нашей карте", "xp": 40, "next": None},
}

@router.post("/quest/submit", response_model=QuestSubmitResponse, tags=["trainer"])
async def submit_quest_proof(request: QuestSubmitRequest):
    """
    Принимает доказательство выполнения квеста, проверяет через LLM,
    начисляет XP и открывает следующий шаг.
    """
    quest = MOCK_QUESTS.get(request.quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")

    # ВЫЗОВ LLM-СЕРВИСА (вместо мок-логики)
    llm_result = llm_service.check_quest_proof(
        quest_title=quest["title"],
        quest_description=quest["description"],
        proof_text=request.proof_text
    )
    
    # Начисляем XP пропорционально оценке LLM
    xp_awarded = int(quest["xp"] * llm_result["xp_multiplier"])
    
    # Определяем, переходить ли к следующему квесту
    is_approved = llm_result["is_approved"] and xp_awarded > 0
    next_quest_id = quest["next"] if is_approved else request.quest_id
    
    return QuestSubmitResponse(
        is_approved=is_approved,
        feedback=llm_result["feedback"],
        xp_awarded=xp_awarded,
        next_quest_id=next_quest_id,
        level_up=False  # В Фазе 3 здесь будет реальная проверка уровня
    )

@router.post("/chat", response_model=ChatResponse, tags=["trainer"])
async def trainer_chat(request: ChatRequest):
    """
    Диалог с AI-тренером: пользователь задаёт вопрос по текущему квесту.
    """
    quest = MOCK_QUESTS.get(request.quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")
    
    # Берём последнее сообщение пользователя
    user_message = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
    if not user_message:
        raise HTTPException(status_code=400, detail="Нет сообщения от пользователя")
    
    # Преобразуем историю в формат для LLM
    chat_history = [{"role": m.role, "content": m.content} for m in request.messages]
    
    # ВЫЗОВ LLM-СЕРВИСА
    reply = llm_service.chat_with_trainer(
        quest_title=quest["title"],
        quest_description=quest["description"],
        user_message=user_message,
        chat_history=chat_history
    )
    
    return ChatResponse(
        reply=reply,
        quest_id=request.quest_id
    )