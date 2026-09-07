# FUTURE ARCHITECTURE — масштабирование Marketplace Intel (Wildberries)

> Назначение файла: пошаговый план «как добавлять магазины и ничего не сломать».
> Для меня будущего и для AI-ассистента в новом чате (начинать с чтения этого файла).
> Актуально для версии v3.1, сентябрь 2026.

## 0. Текущее состояние (честно)

- 1 магазин: LOWENGRASS, 4 артикула (config/products.yaml — плоская схема)
- 1 контейнер marketplace-intel: telegram_bot + dashboard + scheduler
- Данные общие: data/ (снапшоты, черновики, история, конкуренты)
- Расписание (MSK): каждые 3 ч пайплайн; 10:00 отчёт + конкуренты; 04:20 cleanup

ВАЖНО: код сейчас одномагазинный. Второй магазин = Фаза 1 (~1 рабочий день).
После Фазы 1 магазины 3..N добавляются КОНФИГОМ, ноль строк кода.

## 1. Целевая схема конфига (config/products.yaml v2)

stores:
  lowengrass:
    display: LOWENGRASS
    brand: LÖWENGRASS
    nm_ids: [330990418, 618612802, 912617526, 913015022]
    morning_chat_id: -100...
    faq: [...]
    tone: "..."
  dorfhaus:
    display: DORFHAUS
    brand: DORFHAUS
    nm_ids: [...]
    morning_chat_id: -100...
    faq: [...]
    tone: "..."

Совместимость: новый модуль app/config_loader.py, функция load_stores():
если в yaml нет ключа stores: — старая плоская схема заворачивается
в магазин lowengrass. Все модули читают конфиг ТОЛЬКО через load_stores().

## 2. Целевая раскладка данных

data/
├── lowengrass/
│   ├── wb_cards_latest.csv, wb_cards_2*.csv
│   ├── wb_reviews_2*.csv
│   ├── drafts_latest.csv, drafts_2*.csv, processed_reviews.csv
│   ├── competitors_latest.csv, competitors_2*.csv
│   └── history/answered_reviews.csv
├── dorfhaus/
│   └── ... то же самое
└── logs/

Правило: модули никогда не пишут в корень data/, только в data/<store>/.
cleanup.py: паттерны становятся data/*/wb_reviews_2* и т.д.

## 3. Фаза 1 — второй магазин (код, ~1 день)

Порядок шагов (каждый = отдельный патч с assert + деплой + тест):

1. app/config_loader.py (новый): load_stores() + legacy-fallback.
2. collectors/wb_full_collector.py: цикл for store in stores: → пишем в data/<store>/.
3. diff_analyzer.py: по магазинам (своя папка чтения/записи).
4. llm_reviewer.py: по магазинам; few-shot из data/<store>/history/; tone/faq из конфига магазина.
5. comp_discovery.py + comp_collector.py: competitors.yaml переезжает в data/<store>/competitors.yaml.
6. telegram_bot.py: команда /store — inline-кнопки списка магазинов, выбор запоминается
   на пользователя (dict user_id → store); все send_* читают data/<store>/; шапка сообщения = магазин.
7. scheduler.py: refresh(store) в цикле; в 10:00 discovery+collector+отчёт по каждому магазину.
8. dashboard.py: st.sidebar.radio('Магазин', stores) — все секции читают выбранный.
9. cleanup.py: glob по уровню магазина.

Чек-лист теста Фазы 1:
- [ ] /stock /velocity /reviews /drafts /competitors работают по обоим магазинам
- [ ] утренний отчёт приходит в свой чат каждого магазина
- [ ] черновики магазина A не появляются в магазине B
- [ ] cleanup чистит обе папки, потолок диска прежний

## 4. Фаза 2 — магазины 3..N (ноль строк кода, ~15 минут на магазин)

1. Достать nm_ids (страница бренда на WB или кабинет продавца).
2. Добавить секцию в config/products.yaml.
3. Перезапустить scheduler и бота (команды в разделе 7).
4. Прогнать вручную discovery + collector, проверить /competitors.
5. Проверить утренний отчёт магазина на следующий день в 10:00.

## 5. Фаза 3 — изоляция клиентов (свой бот на магазин)

Когда магазины = разные владельцы:
- BotFather: новый бот, токен в .env (TG_TOKEN_DORFHAUS)
- запуск второго процесса: python telegram_bot.py --store dorfhaus
- ИЛИ второй контейнер в docker-compose (полная изоляция памяти и сбоев)
- Критерий изоляции: клиент A физически не видит данные клиента B
  (отдельная папка данных после Фазы 1 + отдельный бот после Фазы 3)

## 6. Фаза 4 — Ozon и другие площадки

- Ozon = ОТДЕЛЬНЫЙ репозиторий ozon-intel: другие API (Seller API v1/v2/v3), другая авторизация.
- Из этого репо переносим паттерны: collector→diff→LLM→bot→dashboard, retention, human-in-the-loop.
- Не смешивать WB и Ozon в одном репо: API не пересекаются, путаница гарантирована.

## 7. Шпаргалка команд

### VPS (SSH)
# здоровье
uptime && free -h && df -h / && docker stats --no-stream
# логи
docker exec marketplace-intel tail -30 /app/data/bot.log
docker exec marketplace-intel tail -30 /app/data/sched.log
# рестарт бота
docker exec marketplace-intel pkill -f telegram_bot.py; sleep 2; docker exec -d marketplace-intel sh -c "python telegram_bot.py > /app/data/bot.log 2>&1"
# рестарт планировщика
docker exec marketplace-intel pkill -f scheduler.py; sleep 2; docker exec -d marketplace-intel sh -c "python scheduler.py > /app/data/sched.log 2>&1"
# рестарт дашборда
docker exec marketplace-intel pkill -f "streamlit run"; sleep 2; docker exec -d marketplace-intel sh -c "streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 > /app/data/dash.log 2>&1"
# ручной прогон
docker exec -w /app marketplace-intel python collectors/wb_full_collector.py
docker exec -w /app marketplace-intel python collectors/comp_discovery.py
docker exec -w /app marketplace-intel python collectors/comp_collector.py

### ПК (PowerShell)
# один файл с VPS
scp root@46.17.101.142:marketplace-intel/app/FILE .\app\FILE
# полная копия без data
scp root@46.17.101.142:marketplace-intel-src.tar.gz .\ ; tar -xzf marketplace-intel-src.tar.gz
# git
git status --short ; git add -A ; git commit -m "..." ; git push

### Правила Git
- В Git НЕ попадают: .env, data/, *.bak*, apply_patch*.py (.gitignore)
- Одно логическое изменение = один коммит
- Перед push смотреть git status --short: только ожидаемые файлы

## 8. Мини-FAQ (вопросы, которые могут задать)

Q: Как добавить второй магазин?
A: После Фазы 1 — через config/products.yaml за 15 минут без кода. До Фазы 1 — день работы по плану раздела 3.

Q: Как изолировать клиентов?
A: Отдельная папка данных (Фаза 1) + отдельный бот/процесс (Фаза 3).

Q: Если WB поменяет API?
A: Коллекторы изолированы в отдельных файлах: правка эндпоинта = правка одного файла, система не замечает. Ретраи и антибот уже встроены.

Q: Сколько стоит эксплуатация?
A: VPS ~1000₽/мес, LLM — бесплатный тариф, диск ~40 МБ на магазин (retention).

Q: Персональные данные (152-ФЗ)?
A: Не храним: только публичные отзывы и цены из публичных API.

## 9. Как работать с этим файлом в новом чате

Дать AI токен репозитория и сказать:
«Проект marketplace-intel. Начни с docs/FUTURE_ARCHITECTURE.md и docs/CHANGELOG.md,
потом читай код по списку файлов из ARCHITECTURE.md».
