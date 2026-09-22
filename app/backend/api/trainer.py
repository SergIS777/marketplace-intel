from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# === МОДЕЛИ ЗАПРОСОВ И ОТВЕТОВ (КОНТРАКТ) ===

class ChatMessage(BaseModel):
    role: str  # "user" или "assistant"
    content: str

class ChatRequest(BaseModel):
    quest_id: str
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    reply: str
    quest_id: str

class QuestSubmitRequest(BaseModel):
    quest_id: str
    proof_text: str  # В будущем можно добавить proof_image_url: Optional[str]

class QuestSubmitResponse(BaseModel):
    is_approved: bool
    feedback: str          # Вердикт LLM-тренера (похвала или указание на ошибку)
    xp_awarded: int        # Сколько XP начислено (0 если не одобрено)
    next_quest_id: Optional[str]  # ID следующего шага, если текущий завершён
    level_up: bool         # Был ли повышён уровень

# === МОК-РЕАЛИЗАЦИЯ (пока без реального вызова ModelScope) ===

MOCK_QUESTS = {
    "quest_1": {"title": "Анкета продавца", "xp": 20, "next": "quest_2"},
    "quest_2": {"title": "Выбор ниши", "xp": 30, "next": "quest_3"},
    "quest_3": {"title": "Регистрация WB Partners", "xp": 40, "next": None},
}

@router.post("/quest/submit", response_model=QuestSubmitResponse, tags=["trainer"])
async def submit_quest_proof(request: QuestSubmitRequest):
    """
    Мок-эндпоинт: принимает доказательство, имитирует проверку LLM 
    и возвращает вердикт, XP и следующий квест.
    """
    quest = MOCK_QUESTS.get(request.quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")

    # ИМИТАЦИЯ ЛОГИКИ LLM (в Фазе 3 здесь будет вызов services/llm_service.py)
    # Для мока: если в доказательстве больше 10 символов, считаем его валидным
    is_valid = len(request.proof_text.strip()) > 10
    
    if is_valid:
        return QuestSubmitResponse(
            is_approved=True,
            feedback=f"Отличная работа! Ты успешно выполнил шаг: '{quest['title']}'. Тренер доволен.",
            xp_awarded=quest["xp"],
            next_quest_id=quest["next"],
            level_up=False # В реальной логике здесь будет проверка суммы XP
        )
    else:
        return QuestSubmitResponse(
            is_approved=False,
            feedback="Кажется, доказательство слишком короткое или не содержит нужных деталей. Попробуй описать свой действие подробнее (минимум 10 символов).",
            xp_awarded=0,
            next_quest_id=request.quest_id,
            level_up=False
        )

@router.post("/chat", response_model=ChatResponse, tags=["trainer"])
async def trainer_chat(request: ChatRequest):
    """
    Мок-эндпоинт: имитирует ответ LLM-тренера на вопрос пользователя.
    """
    # ИМИТАЦИЯ ОТВЕТА LLM
    mock_replies = [
        "Отличный вопрос! На этом этапе важно сосредоточиться на юнит-экономике. Посчитай маржинальность до закупки.",
        "Не переживай, это частая ошибка новичков. Давай разберём твой скриншот: обрати внимание на поле 'Комиссия'.",
        "Ты двигаешься в правильном направлении! Следующий шаг — зарегистрировать профиль продавца по нашей карте."
    ]
    
    return ChatResponse(
        reply=mock_replies[len(request.messages) % len(mock_replies)],
        quest_id=request.quest_id
    )