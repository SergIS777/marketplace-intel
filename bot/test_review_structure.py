import requests
import json

article = 330990418
url1 = f'https://card.wb.ru/cards/v4/detail?appType=1&curr=rub&dest=-1257786&nm={article}'
r1 = requests.get(url1, timeout=10)
root = r1.json()['products'][0]['root']

# Получаем отзывы
url2 = f'https://feedbacks1.wb.ru/feedbacks/v1/{root}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/'
}
r2 = requests.get(url2, headers=headers, timeout=10)
data = r2.json()

print(f'Всего отзывов получено: {len(data.get("feedbacks", []))}')
print(f'\n=== Первый отзыв (полная структура) ===')
first = data['feedbacks'][0]
print(json.dumps(first, indent=2, ensure_ascii=False))
