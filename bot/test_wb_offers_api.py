import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/'
}

article = 330990418
root = 312328182
vol = article // 100000
part = article // 1000

endpoints = [
    ('card v4 prices', f'https://card.wb.ru/cards/v4/detail?appType=1&curr=rub&dest=-1257786&nm={article}'),
    ('basket sellers.json', f'https://basket-01.wbbasket.ru/vol{vol}/part{part}/{article}/info/ru/sellers.json'),
    ('static-basket sellers', f'https://static-basket-01.wbbasket.ru/vol{vol}/part{part}/{article}/info/ru/sellers.json'),
    ('basket offers.json', f'https://basket-01.wbbasket.ru/vol{vol}/part{part}/{article}/info/ru/offers.json'),
    ('static-basket offers', f'https://static-basket-01.wbbasket.ru/vol{vol}/part{part}/{article}/info/ru/offers.json'),
    ('card v1 sellers', f'https://card.wb.ru/cards/sellers?nm={article}'),
    ('card v2 sellers', f'https://card.wb.ru/cards/v2/sellers?nm={article}'),
    ('feedbacks1 root (все данные)', f'https://feedbacks1.wb.ru/feedbacks/v1/{root}'),
]

print(f'nm_id: {article}, root: {root}\n')

for name, url in endpoints:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        size = len(r.text)
        print(f'{name}: {r.status_code}, {size}b')
        if r.status_code == 200 and size > 50:
            try:
                d = r.json()
                keys = list(d.keys())[:8]
                print(f'  Keys: {keys}')
                # Ищем массив офферов/селлеров
                for k in ['sellers', 'offers', 'products', 'items', 'data']:
                    if k in d and isinstance(d[k], list) and len(d[k]) > 0:
                        print(f'  НАЙДЕН массив {k}: {len(d[k])} элементов')
                        first = d[k][0]
                        if isinstance(first, dict):
                            print(f'  Первый элемент keys: {list(first.keys())[:10]}')
                            print(f'  Пример: {json.dumps(first, ensure_ascii=False)[:250]}')
                        break
            except:
                print(f'  Не JSON: {r.text[:100]}')
    except Exception as e:
        print(f'{name}: {type(e).__name__}')
