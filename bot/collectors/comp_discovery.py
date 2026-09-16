"""Авто-поиск конкурентов: для каждого нашего товара — топ похожих карточек других продавцов"""
import re
import requests
import pandas as pd
import yaml
from pathlib import Path

DATA = Path('/app/data')
CFG = Path('/app/config/competitors.yaml')

def norm(s):
    s = str(s).lower().replace('ö', 'o').replace('ё', 'e').replace('ü', 'u')
    return re.sub(r'[^a-zа-я0-9]+', ' ', s).strip()

def toks(s):
    return set(w for w in norm(s).split() if len(w) >= 3 or w.isdigit())

def digs(s):
    return set(w for w in norm(s).split() if any(c.isdigit() for c in w))

def query_for(name):
    words = norm(name).split()
    head = ' '.join(words[:3])
    parts = [head]
    m = re.search(r'\d+\s+в\s+\d+', norm(name))
    if m:
        parts.append(m.group(0))
    for w in words:
        if any(c.isdigit() for c in w) and w not in ' '.join(parts):
            parts.append(w)
    return ' '.join(parts).strip()

def is_match(our_name, our_brand, res_name):
    a, b = norm(our_name), norm(res_name)
    brand = norm(our_brand)
    if brand and len(brand) >= 4 and brand in b:
        return True
    common_words = set(w for w in toks(a) & toks(b) if len(w) >= 6)
    common_digits = digs(a) & digs(b)
    return bool(common_words) and bool(common_digits)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}

def search(q, limit=20):
    import time
    for attempt in range(3):
        r = requests.get('https://search.wb.ru/exactmatch/ru/common/v4/search',
                         params={'appType': 1, 'curr': 'rub', 'dest': -1257786,
                                 'query': q, 'resultset': 'catalog', 'sort': 'popular', 'limit': limit},
                         headers=HEADERS, timeout=15)
        if r.status_code == 200 and r.text.strip():
            try:
                j = r.json()
                return (j.get('data') or {}).get('products') or j.get('products') or []
            except Exception:
                pass
        print(f'    попытка {attempt + 1}: status {r.status_code}, тело {r.text[:60]!r}')
        time.sleep(3 + attempt * 3)
    return []

def main():
    cards = pd.read_csv(DATA / 'wb_cards_latest.csv')
    own = set(int(x) for x in cards['nm_id'])
    entries = []
    for _, c in cards.iterrows():
        nm = int(c['nm_id'])
        q = query_for(c['name'])
        try:
            res = search(q)
        except Exception as e:
            print(f'  {nm}: ошибка поиска {e}')
            continue
        found = 0
        for p in res:
            pid = int(p.get('id', 0))
            if pid in own or pid == 0:
                continue
            if is_match(c['name'], c['brand'], p.get('name', '')):
                entries.append({'nm_id': pid, 'for_nm': nm, 'tag': 'авто'})
                found += 1
                print(f'  {nm} -> конкурент {pid} | {str(p.get("name"))[:40]}')
                if found >= 5:
                    break
        print(f'  {nm}: найдено {found} (запрос: {q})')
        import time; time.sleep(15)
    if entries:
        old = []
        if CFG.exists():
            old_cfg = yaml.safe_load(CFG.read_text()) or {}
            old = old_cfg.get('competitors') or []
        if len(entries) >= len(old) * 0.8:
            CFG.write_text(yaml.safe_dump({'competitors': entries}, allow_unicode=True, sort_keys=False), encoding='utf-8')
            print(f'competitors.yaml перезаписан: {len(entries)} конкурентов (было {len(old)})')
        else:
            print(f'ВНИМАНИЕ: найдено {len(entries)}, было {len(old)} — yaml НЕ перезаписан (защита от потери)')
    else:
        print('НИЧЕГО не найдено — yaml не тронут')

if __name__ == '__main__':
    main()
