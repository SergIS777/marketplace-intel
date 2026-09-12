# START HERE — Marketplace Intel

## Что это
Автономная платформа управления магазином Wildberries:
AI-консультант + аналитика + автоматизация в одном приложении.

## Документы для чтения (в этом порядке)
1. `docs/BUSINESS_PLAN.md` — полная бизнес-логика (24 раздела)
2. `docs/FUTURE_ARCHITECTURE.md` — архитектура масштабирования
3. `docs/PHASE2_ROADMAP.md` — план подключения Seller API
4. `CHANGELOG.md` — история изменений

## Текущий статус
- Платформа v3.1 работает 24/7 на VPS (Голландия)
- Telegram-бот + Streamlit-дашборд + мониторинг конкурентов + AI-ответы
- Бизнес-план готов: START/PRO/MAX тарифы, философия продукта
- Следующий шаг: регистрация WB Partners + песочница

## Что делать дальше
1. Создать `START_HERE.md` (этот файл) ✅
2. Проверить сервер: `free -h && uptime && docker stats`
3. Регистрация WB Partners: seller.wildberries.ru
4. Создать тестовый токен в кабинете продавца
5. Первый запрос в песочницу: `curl -H "Authorization: $WB_TEST_TOKEN" https://marketplace-api-sandbox.wildberries.ru/ping`

## Продолжение работы
Если контекст потерян: дай GitHub-токен и напиши
"продолжаем с START_HERE.md" — новый AI прочитает документы
и войдёт в курс дела за 2 минуты.
