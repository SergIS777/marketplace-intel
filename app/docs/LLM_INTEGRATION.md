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

## Модель

### Текущая (прод v3.1 - bot/llm_reviewer.py)
- ❌ `Qwen/Qwen3-30B-A3B-Instruct-2507` — **УДАЛЕНА из API** (ошибка 400: no provider supported)

### Рекомендуемые для Фазы 3 (проверено 22.09.2026)
- ✅ `Qwen/Qwen3.5-27B` — **ОСНОВНОЙ ВЫБОР**: новая модель, баланс качество/скорость, 1 Magicube/вызов
- ✅ `Qwen/Qwen3.8-27B` — альтернатива: ещё новее, та же производительность
- ✅ `Qwen/Qwen3.5-35B-A3B` — MoE: быстрее (3B активных), дешевле

### Для тестов
- `Qwen/Qwen3.5-122B-A10B` — большая модель для сложных задач
- `DeepSeek-V4.1-Flash` — быстрая альтернатива

### Проверка доступных моделей
```bash
$headers = @{"Authorization" = "Bearer $env:MODEL_SCOPE_API_KEY"}
Invoke-RestMethod -Uri "https://api-inference.modelscope.ai/v1/models" -Headers $headers

### Расход (Magicubes)
Free tier: ~2000 Magicubes при регистрации
27B модель: ~1 Magicube/вызов
Итого: ~2000 вызовов = ~400-600 сессий тренера

## Фаза 3: LLM-тренер (реализовано 22.09.2026)

### Эндпоинты
- `POST /api/v1/quest/submit` — проверка доказательства через LLM
  - Промпт: анализ доказательства на соответствие заданию (минимум 20 символов, конкретика)
  - Ответ: `is_approved`, `feedback`, `xp_awarded`, `next_quest_id`
  
- `POST /api/v1/chat` — диалог с тренером
  - Промпт: контекст текущего квеста + история диалога (последние 5 сообщений)
  - Ответ: `reply` (краткий, 3-4 предложения, поддерживающий тон)

### Модель
- Qwen/Qwen3.5-27B (замена удалённой Qwen3-30B-A3B)
- Расход: ~1 Magicube/вызов
- Температура: 0.3 для проверки доказательств, 0.7 для чата

### Токен
- `MODEL_SCOPE_API_KEY_APP` (write permission)
- Отдельный от бота (`MODEL_SCOPE_API_KEY`)
- Загрузка: python-dotenv из корня репозитория

### Тестирование
- Swagger UI: http://localhost:8000/docs
- Оба эндпоинта возвращают реальные ответы (не мок)