from curl_cffi import requests
import json

# Имитация Chrome на уровне TLS
session = requests.Session(impersonate="chrome120")

article = 330990418
print(f"=== Тест вопросов через curl_cffi (chrome120) ===")
print(f"Артикул: {article}")

# Шаг 1: Карточка через правильный endpoint
url_card = f'https://card.wb.ru/cards/v4/detail?appType=1&curr=rub&dest=-1257786&nm={article}'
print(f"\nШаг 1: {url_card}")
try:
    r1 = session.get(url_card, timeout=10)
    print(f"Status: {r1.status_code}")
    if r1.status_code == 200:
        products = r1.json().get('products', [])
        if products:
            root_id = products[0].get('root')
            print(f"root: {root_id}")
except Exception as e:
    print(f"Ошибка: {type(e).__name__}")
    root_id = None

if not root_id:
    print("Не удалось получить root")
else:
    # Шаг 2: Вопросы через feedbacks1 с isQuestion=True
    print(f"\nШаг 2: Тест isQuestion=True")
    url_q = 'https://feedbacks1.wb.ru/feedbacks/v1/by-imt'
    payload = {
        'imtId': root_id,
        'skip': 0,
        'take': 20,
        'order': 'dateDesc',
        'isQuestion': True
    }
    try:
        r2 = session.post(url_q, json=payload, timeout=10)
        print(f"Status: {r2.status_code}, Size: {len(r2.text)}b")
        if r2.status_code == 200:
            data = r2.json()
            keys = list(data.keys())[:10]
            print(f"Keys: {keys}")
            feedbacks = data.get('feedbacks', [])
            if feedbacks:
                print(f"Вопросов: {len(feedbacks)}")
                for i, q in enumerate(feedbacks[:3], 1):
                    print(f"\n--- Вопрос {i} ---")
                    print(f"Текст: {q.get('text', '')[:150]}")
        else:
            print(f"Ответ: {r2.text[:200]}")
    except Exception as e:
        print(f"Ошибка: {type(e).__name__} - {e}")

    # Шаг 3: Обычный GET на feedbacks1 (может там есть type=question?)
    print(f"\nШаг 3: GET feedbacks1 с поиском type")
    url_fb = f'https://feedbacks1.wb.ru/feedbacks/v1/{root_id}'
    try:
        r3 = session.get(url_fb, timeout=10)
        print(f"Status: {r3.status_code}")
        if r3.status_code == 200:
            data = r3.json()
            feedbacks = data.get('feedbacks', [])
            # Ищем любые элементы с type=question или без rating
            questions = [f for f in feedbacks if f.get('type') == 'question' or f.get('productValuation') is None]
            print(f"Найдено вопросов: {len(questions)} из {len(feedbacks)} отзывов")
            if questions:
                print(f"Пример: {json.dumps(questions[0], ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"Ошибка: {type(e).__name__}")
