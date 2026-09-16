# Architecture — Marketplace Intel

Документ оформлен по стандарту **arc42** (12 секций), диаграммы — по уровням **C4** в mermaid.

***

## 1. Введение и цели

**Marketplace Intel** — автономная система наблюдения и коммуникации для
магазина LOWENGRASS (Wildberries): снимает публичные данные, рождает алерты,
пишет черновики ответов LLM, даёт пульт управления в Telegram и живой дашборд.
Self-hosted, без доступа в кабинет продавца, на free-tier API.

### Топ-3 цели

1. **Автономность 24/7**: обновление каждые 3 часа, утренний отчёт в 09:00, человек не трогает файлы
2. **Экономичность**: 0 вызовов LLM в тихий день (дедупликация), free-tier ModelScope, потолок диска ~40 МБ
3. **Human-in-the-loop**: LLM предлагает — человек решает; одобренное растит базу знаний

### Стейкхолдеры

| Роль | Интерес |
| --- | --- |
| Владелец бренда (ИП Зимина Е.В.) | утренний отчёт, алерты out-of-stock, контроль коммуникации |
| Менеджер маркетплейсов | пульт в Telegram: остатки, отзывы, черновики одной кнопкой |
| Руководитель отдела продаж | дашборд: рейтинг, динамика, точки роста |
| AI-специалист (автор) | внедрение ИИ с измеримым результатом |

***

## 2. Ограничения архитектуры

- Малый VPS (2 CPU, ~2 GB) → один Docker-контейнер, лимит 512M
- **Нет Seller API** → вопросы покупателей, чужие офферы, воронка и продажи недоступны (WBAAS anti-bot: 498/403/404)
- Free-tier ModelScope → дедупликация вызовов LLM обязательна
- Публичные API WB без «официальной» документации → эмпирический подбор endpoint'ов

***

## 3. Контекст системы (C4 Level 1: Context)

```
graph LR
    WB["Wildberries<br/>публичные API"] -->|"card.wb.ru, feedbacks1.wb.ru"| COL["collectors"]
    COL --> CSV["CSV-слой снапшотов<br/>data/"]
    CSV --> AN["diff_analyzer.py<br/>алерты"]
    CSV --> LLM["llm_reviewer.py<br/>Qwen3 (ModelScope)"]
    AN --> BOT["telegram_bot.py<br/>aiogram, пульт"]
    LLM --> BOT
    CSV --> DASH["dashboard.py<br/>Streamlit :8501"]
    BOT -->|"одобрение"| KB["history/answered_reviews.csv<br/>база знаний"]
    KB --> LLM
    SCH["scheduler.py<br/>каждые 3 часа + 09:00"] --> COL
    SCH -->|"утренний отчёт"| OWNER["владелец (Telegram)"]
```

**Бизнес-контекст:** снапшот → diff → событие → черновик → одобрение → база знаний.
**Технический контекст:** все внешние сервисы (WB, ModelScope, Telegram) — по HTTP; память — файлы в volume.

***

## 4. Стратегия решений

| Решение | Обоснование | Альтернатива (отклонена) |
| --- | --- | --- |
| Публичные API WB | данные без ключа продавца | Seller API: нет доступа |
| ModelScope Qwen3-30B-A3B | free tier с `ms-` токеном | Groq: не подошла модель free-tier |
| Few-shot RAG на 998 ответах | тон бренда без обучения | Fine-tuning: дорого, медленно |
| Дедупликация черновиков | 0 токенов в тихий день | регенерация каждый крон: трата |
| aiogram-бот | пульт + human-in-the-loop | n8n-уведомлялка: нет интерактива |
| asyncio-планировщик | автономность без правки n8n | n8n cron: контейнер n8n трогать нельзя |
| Docker + compose | workflow-as-code, восстановление одной командой | системный pip: на хосте пустой |
| Retention снапшотов | потолок ~40 МБ навсегда | без retention: ~360 МБ/месяц |
| Авто-поиск конкурентов (search API + фильтр бренд/модель) | карта рынка без ручного сбора | «все предложения» на карточке: закрыто антиботом (404/429) |
| Кнопки v3 с source=llm/human | владелец учит систему своим голосом | мёртвая кнопка «Отклонить»: без полезного исхода |

***

## 5. Структура блоков (C4 Level 2/3)

```
graph TB
    subgraph VPS ["VPS (Docker)"]
        subgraph CT ["marketplace-intel (restart: unless-stopped, 512M)"]
            COL["collectors/wb_full_collector.py<br/>карточки v4 + отзывы feedbacks1"]
            AN["diff_analyzer.py<br/>diff снапшотов → события"]
            LLM["llm_reviewer.py<br/>few-shot → черновики, дедуп"]
            BOT["telegram_bot.py<br/>10 команд, кнопки"]
            DASH["dashboard.py<br/>Streamlit :8501, Plotly"]
            SCH["scheduler.py<br/>3h цикл + отчёт 09:00"]
            CLN["cleanup.py<br/>retention + логи"]
            DATA[("data/<br/>снапшоты, history/, логи")]
        end
    end
    SCH --> COL --> DATA
    COL --> AN --> DATA
    AN --> LLM --> DATA
    DATA --> BOT
    DATA --> DASH
    CLN --> DATA
```

**Таблица-карта файлов:**

| Файл | Роль | Связан с |
| --- | --- | --- |
| `app/collectors/wb_full_collector.py` | карточки (цены/остатки/акции) + отзывы → CSV | data/ |
| `app/diff_analyzer.py` | сравнение снапшотов → events_latest.json | data/ |
| `app/llm_reviewer.py` | черновики (Qwen3, few-shot, дедуп) | data/history/, products.yaml |
| `app/telegram_bot.py` | пульт: 10 команд, одобрение черновиков | data/, Telegram API |
| `app/dashboard.py` | дашборд Plotly :8501 | data/ |
| `app/scheduler.py` | автономность: 3h пайплайн + отчёт 09:00 | все модули |
| `app/cleanup.py` | retention снапшотов + обрезка логов | data/ |
| `config/products.yaml` | база знаний: specs, faq, tone | llm_reviewer.py |
| `docker-compose.yml` | порт 8501, volumes, env_file, логи 10m×3, 512M | Docker |
| `.env` | TELEGRAM_BOT_TOKEN, MODEL_SCOPE_API_KEY | контейнер |
| `app/collectors/comp_collector.py` | снапшоты конкурентов: цена/остаток/рейтинг | data/, competitors.yaml |
| `app/collectors/comp_discovery.py` | авто-поиск конкурентов на каждый наш товар | search.wb.ru, competitors.yaml |
| `config/competitors.yaml` | карта конкурентов с привязкой for_nm | discovery/collector |

**Точка входа:** чтение начинай с `app/scheduler.py` — оркестрация; данные — в `data/`.

***

## 6. Сценарии выполнения

1. **Цикл 3 часа:** scheduler → collector → diff → LLM (только новые негативы) → `last_run_status.json` → честное сообщение в Telegram
2. **Утренний отчёт 09:00:** алерты + низкий остаток + ссылка на дашборд
3. **Human-in-the-loop:** /drafts → [Одобрить] → пара «отзыв+ответ» в history/ → база знаний растёт

***

## 7. Инфраструктура

- VPS + Docker; контейнер `marketplace-intel` (python 3.11-slim)
- compose: порт 8501, volumes `./data` и `./config`, `env_file: .env`, logging json-file 10m×3, memory 512M, restart unless-stopped
- Host cron: 04:20 cleanup; опционально — копия данных в `/root/local-files` для n8n

***

## 8. Внешние компоненты

| Компонент | Назначение | Доступность |
| --- | --- | --- |
| card.wb.ru/cards/v4 | цены/остатки/акции | публично ✅ |
| feedbacks1.wb.ru | отзывы | публично ✅ |
| api-inference.modelscope.ai | LLM Qwen3 | free tier ✅ |
| api.telegram.org | бот + отчёты | ✅ |
| search.wb.ru (exactmatch v4) | авто-поиск конкурентов | публично, лимит 429 ✅ |
| вопросы/офферы/воронка WB | Фаза 2 | закрыты anti-bot ❌ |

***

## 9. Требования к качеству

| Требование | Мера |
| --- | --- |
| Автономность | человек не трогает файлы; восстановление = `docker compose up -d` |
| Экономичность | 0 вызовов LLM без новых негативов; потолок диска ~40 МБ |
| Честность UX | «новых отзывов нет» вместо ложного «новые черновики» |
| Безопасность публикации | только human-in-the-loop |

***

## 10. Риски

| Риск | Вероятность | Митигация |
| --- | --- | --- |
| WB поменяет антибот/API | средняя | меняются только коллекторы, верхний слой нетронут |
| Кончится free-tier ModelScope | средняя | модель/провайдер меняются в одном месте |
| Утечка токенов | низкая | `.env` chmod 600, не коммитится |
| Пересоздание контейнера сотрёт docker-cp файлы | средняя | исходники на хосте: `~/marketplace-intel/app` |

***

## 11. Глоссарий

| Термин | Значение |
| --- | --- |
| nm_id | артикул товара WB |
| root | ID объединённой карточки (общие отзывы у нескольких nm_id) |
| Снапшот | CSV-срез данных с меткой времени |
| Few-shot | примеры реальных ответов бренда в промпте |
| Retention | автоудаление старых снапшотов и логов |

***

## 12. Ссылки

- README.md — быстрый старт
- WB публичные API: card.wb.ru, feedbacks1.wb.ru
- ModelScope: https://modelscope.cn
- aiogram 3: https://docs.aiogram.dev
- Streamlit: https://docs.streamlit.io
