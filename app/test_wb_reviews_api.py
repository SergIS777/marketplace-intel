import requests
import json

article = 330990418

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/',
    'Content-Type': 'application/json'
}

# Получаем данные товара
url1 = f'https://card.wb.ru/cards/v4/detail?appType=1&curr=rub&dest=-1257786&nm={article}'
r1 = requests.get(url1, timeout=10)
data = r1.json()
product = data['products'][0]

nm_id = product['id']
root = product['root']
match_id = product['matchId']
print(f'nm_id: {nm_id}, root: {root}, matchId: {match_id}')

# 1. Перебор поддоменов feedbacks1-feedbacks10 с GET через /{root}
print('\n=== ВАРИАНТ 1: GET feedbacks{N}.wb.ru/feedbacks/v1/{root} ===')
for n in range(1, 11):
    try:
        url = f'https://feedbacks{n}.wb.ru/feedbacks/v1/{root}'
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            print(f'  feedbacks{n}.wb.ru GET /{root}: Status {r.status_code}, Size {len(r.text)}')
            data = r.json()
            print(f'    Keys: {list(data.keys())[:10]}')
            if 'feedbacks' in data:
                print(f'    Есть feedbacks! Count: {len(data["feedbacks"])}')
                if data['feedbacks']:
                    print(f'    Пример: {json.dumps(data["feedbacks"][0], ensure_ascii=False)[:200]}')
        else:
            print(f'  feedbacks{n}.wb.ru GET: {r.status_code}')
    except Exception as e:
        print(f'  feedbacks{n}.wb.ru: {type(e).__name__}')

# 2. Перебор с POST через /by-imt
print('\n=== ВАРИАНТ 2: POST feedbacks{N}.wb.ru/feedbacks/v1/by-imt ===')
for n in range(1, 11):
    try:
        url = f'https://feedbacks{n}.wb.ru/feedbacks/v1/by-imt'
        payload = {'imtId': root, 'skip': 0, 'take': 5}
        r = requests.post(url, json=payload, headers=headers, timeout=5)
        print(f'  feedbacks{n}.wb.ru POST: Status {r.status_code}, Size {len(r.text)}')
        if r.status_code == 200:
            data = r.json()
            if 'feedbacks' in data and data['feedbacks']:
                print(f'    НАШЛИ ОТЗЫВЫ! Count: {len(data["feedbacks"])}')
                print(f'    Пример: {json.dumps(data["feedbacks"][0], ensure_ascii=False)[:200]}')
    except Exception as e:
        print(f'  feedbacks{n}.wb.ru: {type(e).__name__}')

# 3. Альтернативные endpoints
print('\n=== ВАРИАНТ 3: Альтернативные endpoints ===')
alt_urls = [
    f'https://card-feedback.wb.ru/cards/v1/detail?nm={nm_id}',
    f'https://card-feedback.wb.ru/cards/v2/detail?nm={nm_id}',
    f'https://feedback-api.wildberries.ru/feedbacks/v1/by-imt/{root}',
    f'https://app-api.wildberries.ru/feedbacks?nmId={nm_id}',
    f'https://basket-01.wbbasket.ru/vol{nm_id//100000}/part{nm_id//1000}/{nm_id}/info/ru/feedbacks.json',
    f'https://static-basket-01.wbbasket.ru/vol{nm_id//100000}/part{nm_id//1000}/{nm_id}/info/ru/feedbacks.json',
]
for url in alt_urls:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f'  {url[:70]}: {r.status_code}, Size {len(r.text)}')
        if r.status_code == 200 and len(r.text) > 100:
            try:
                data = r.json()
                print(f'    Keys: {list(data.keys())[:10]}')
            except:
                print(f'    Not JSON')
    except Exception as e:
        print(f'  {url[:50]}: {type(e).__name__}')
