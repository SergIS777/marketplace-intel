# LLM-интеграция — единая точка правды (Фаза 3+)
- Провайдер: ModelScope, домен inference: https://api-inference.modelscope.ai/v1/chat/completions (НЕ .cn — 401)
- Токен: MODEL_SCOPE_API_KEY в .env (формат ms-..., Bearer). Персональный SDK/API-токен ModelScope. В git не коммитится.
- Модель: Qwen/Qwen3-30B-A3B-Instruct-2507
- Запрос: OpenAI-совместимый chat/completions, max_tokens 700, temperature 0.7, timeout 30s
- Паттерн (прод в bot/llm_reviewer.py): few-shot топ-3 из history + дедуп по id (0 токенов в тихий день)
- Проверка токена: bot/test_modelscope.py
- Фаза 3: бэкенд переиспользует паттерн в services/llm_trainer.py; без токена — mock-режим

### Типы токенов ModelScope
- **read-only permission** — только чтение из hub (модели, датасеты). НЕ подходит для inference API.
- **write permission** — для API-вызовов включая inference. **ЭТО НУЖНО.**
- **fine-grained permission** — детальные ограничения (избыточно для нас).
- **admin permission** — управление аккаунтом (избыточно).

Создаём на https://modelscope.ai/my/settings/token → выбираем **write permission**.