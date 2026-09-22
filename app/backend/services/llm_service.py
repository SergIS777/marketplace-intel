import os
import json # ✅ ИСПРАВЛЕНО 1: перенесено наверх
import requests
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. Вычисляем путь к корню репозитория (4 уровня вверх от services/llm_service.py)
_env_path = Path(__file__).parent.parent.parent.parent / '.env'

# 2. ОТЛАДОЧНЫЙ ВЫВОД: покажем, какой путь мы пытаемся открыть
print(f"\n[LLMService DEBUG] Ищем .env по пути: {_env_path.resolve()}")
print(f"[LLMService DEBUG] Файл существует? {_env_path.exists()}\n")

# 3. Загружаем переменные
load_dotenv(_env_path)

class ChatMessage(BaseModel):
    role: str
    content: str

class LLMService:
    def __init__(self):
        self.api_key = os.environ.get('MODEL_SCOPE_API_KEY_APP', '')
        self.api_url = "https://api-inference.modelscope.ai/v1/chat/completions"
        self.model = "Qwen/Qwen3.5-27B"
        self.timeout = 30
        
        print(f"[LLMService] api_key loaded: {'YES' if self.api_key else 'NO'} (len={len(self.api_key)})\n")
        
        self.use_mock = not self.api_key
    
    def _call_modelscope(self, messages: List[ChatMessage], max_tokens: int = 500, temperature: float = 0.7) -> str:
        if self.use_mock:
            return self._mock_response(messages)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [msg.dict() for msg in messages],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            r = requests.post(self.api_url, json=payload, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            return f"Ошибка вызова LLM: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Ошибка парсинга ответа LLM: {str(e)}"
    
    def _mock_response(self, messages: List[ChatMessage]) -> str:
        last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "")
        
        if "доказательство" in last_user_msg.lower() or "выполнил" in last_user_msg.lower():
            return "Отличная работа! Ты успешно выполнил задание. Тренер доволен твоим прогрессом."
        else:
            return "Это мок-ответ. Для реальных ответов LLM установи MODEL_SCOPE_API_KEY_APP в .env"
    
    def check_quest_proof(self, quest_title: str, quest_description: str, proof_text: str) -> Dict:
        system_prompt = f"""Ты — AI-тренер для начинающих продавцов на Wildberries.
Твоя задача: проверить, выполнил ли пользователь задание квеста.

ТЕКУЩЕЕ ЗАДАНИЕ:
Название: {quest_title}
Описание: {quest_description}

ПРАВИЛА ПРОВЕРКИ:
1. Доказательство должно содержать конкретные действия (не просто "я сделал")
2. Минимум 20 символов осмысленного текста
3. Должно быть видно, что пользователь понял суть задания
4. Если доказательство слабое — дай конструктивную обратную связь, что улучшить

ОТВЕТЬ В ФОРМАТЕ JSON:
{{
  "is_approved": true/false,
  "feedback": "текст обратной связи",
  "xp_multiplier": 0.0-1.0 (1.0 = полное выполнение, 0.5 = частичное, 0.0 = не выполнено)
}}
"""
        
        user_message = f"Моё доказательство выполнения задания:\n\n{proof_text}"
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_message)
        ]
        
        response_text = self._call_modelscope(messages, max_tokens=300, temperature=0.3)
        
        # Парсим JSON из ответа (с fallback)
        try:
            # Ищем JSON в ответе (LLM может добавить текст до/после)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(response_text[json_start:json_end])
                return {
                    "is_approved": result.get("is_approved", False),
                    "feedback": result.get("feedback", "Не удалось разобрать ответ LLM"),
                    "xp_multiplier": float(result.get("xp_multiplier", 0.0))
                }
        except Exception:
            pass
        
        # Fallback: если не удалось распарсить JSON
        return {
            "is_approved": len(proof_text.strip()) > 20,
            "feedback": response_text[:200],
            "xp_multiplier": 0.5 if len(proof_text.strip()) > 20 else 0.0
        }
    
    def chat_with_trainer(self, quest_title: str, quest_description: str, user_message: str, chat_history: Optional[List[Dict]] = None) -> str: # ✅ ИСПРАВЛЕНО 2: добавлен Optional
        system_prompt = f"""Ты — дружелюбный AI-тренер для начинающих продавцов на Wildberries.
Ты помогаешь пользователю выполнить текущее задание квеста.

ТЕКУЩЕЕ ЗАДАНИЕ ПОЛЬЗОВАТЕЛЯ:
Название: {quest_title}
Описание: {quest_description}

ПРАВИЛА:
1. Отвечай кратко и по делу (максимум 3-4 предложения)
2. Давай конкретные советы, а не общие фразы
3. Если вопрос не по теме — мягко верни к текущему заданию
4. Используй поддерживающий тон: "Отличный вопрос!", "Ты двигаешься в правильном направлении!"
5. Не делай работу за пользователя — направляй, но не давай готовых ответов
"""
        
        messages = [ChatMessage(role="system", content=system_prompt)]
        
        # Добавляем историю диалога (если есть)
        if chat_history:
            for msg in chat_history[-5:]:  # Последние 5 сообщений
                messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
        
        messages.append(ChatMessage(role="user", content=user_message))
        
        return self._call_modelscope(messages, max_tokens=200, temperature=0.7)


# Глобальный экземпляр для использования в роутерах
llm_service = LLMService()