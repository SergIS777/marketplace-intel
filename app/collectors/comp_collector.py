"""Конкуренты: снапшоты цен/остатков/рейтингов (публичный API WB, v4/detail)"""
import requests
import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime

DATA = Path('/app/data')
CFG = Path('/app/config/competitors.yaml')

def fetch_card(nm):
    r = requests.get('https://card.wb.ru/cards/v4/detail',
                     params={'appType': 1, 'curr': 'rub', 'dest': -1257786, 'nm': nm, 'spp': 30},
                     timeout=15)
    r.raise_for_status()
    prods = r.json().get('products', [])
    return prods[0] if prods else None

def main():
    if not CFG.exists():
        print('competitors.yaml не найден — пропускаю')
        return
    cfg = yaml.safe_load(CFG.read_text()) or {}
    comps = cfg.get('competitors') or []
    if not comps:
        print('Список конкурентов пуст — пропускаю')
        return
    rows = []
    for c in comps:
        nm = int(c['nm_id'])
        if nm <= 0:
            continue
        try:
            p = fetch_card(nm)
            if not p:
                print(f'  {nm}: не найден')
                continue
            sizes = p.get('sizes') or []
            price = (sizes[0].get('price', {}) if sizes else {}).get('product', 0) / 100
            stock = p.get('totalQuantity', 0)
            if not stock and sizes:
                stock = sum(s.get('qty', 0) for sz in sizes for s in sz.get('stocks', []))
            rows.append({
                'nm_id': p.get('id'),
                'root': p.get('root'),
                'tag': c.get('tag', ''),
                'for_nm': int(c.get('for_nm', 0)),
                'name': p.get('name', ''),
                'brand': (p.get('brand') or '').strip() or 'no-brand',
                'supplier': p.get('supplier', ''),
                'price_rub': price,
                'old_price_rub': ((sizes[0].get('price', {}) if sizes else {}).get('basic', 0)) / 100,
                'stock_total': stock,
                'rating': p.get('reviewRating', 0),
                'feedbacks': p.get('feedbacks', 0),
                'timestamp': datetime.now().isoformat()
            })
            print(f'  {nm} | {p.get("brand") or "no-brand"} | {price:.0f}₽ | stock {stock} | ★{p.get("reviewRating", 0)}')
        except Exception as e:
            print(f'  {nm}: ошибка {e}')
    if not rows:
        return
    df = pd.DataFrame(rows)
    ts = datetime.now().strftime('%Y%m%d_%H%M')
    df.to_csv(DATA / f'competitors_{ts}.csv', index=False, encoding='utf-8')
    df.to_csv(DATA / 'competitors_latest.csv', index=False, encoding='utf-8')
    print(f'Конкурентов сохранено: {len(df)}')

if __name__ == '__main__':
    main()
