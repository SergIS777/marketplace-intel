"""Полный коллектор LOWENGRASS: v4 карточки + отзывы по всем 4 товарам"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import logging

log = logging.getLogger("intel.wb.full")

PRODUCT_IDS = [330990418, 618612802, 912617526, 913015022]

class WBFullCollector:
    def __init__(self, data_dir="/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Origin': 'https://www.wildberries.ru',
            'Referer': 'https://www.wildberries.ru/'
        })

    def get_card(self, nm_id):
        url = f'https://card.wb.ru/cards/v4/detail?appType=1&curr=rub&dest=-1257786&nm={nm_id}'
        r = self.session.get(url, timeout=10)
        if r.status_code != 200:
            return None
        products = r.json().get('products', [])
        if not products:
            return None
        p = products[0]
        sizes = p.get('sizes', [])
        price = sizes[0].get('price', {}) if sizes else {}
        old = price.get('basic', 0) / 100
        cur = price.get('product', 0) / 100
        return {
            'nm_id': p.get('id'),
            'root': p.get('root'),
            'name': p.get('name', ''),
            'brand': p.get('brand', ''),
            'rating': p.get('rating', 0),
            'review_rating': p.get('reviewRating', 0),
            'feedbacks_count': p.get('feedbacks', 0),
            'price_rub': cur,
            'old_price_rub': old,
            'stock_total': p.get('totalQuantity', 0),
            'promotions_count': len(p.get('promotions', [])),
            'timestamp': datetime.now().isoformat()
        }

    def get_reviews(self, root, nm_id):
        url = f'https://feedbacks1.wb.ru/feedbacks/v1/{root}'
        r = self.session.get(url, timeout=15)
        if r.status_code != 200:
            return []
        out = []
        for f in r.json().get('feedbacks', []):
            out.append({
                'nm_id': nm_id,
                'root': root,
                'review_id': f.get('id'),
                'author': (f.get('wbUserDetails') or {}).get('name', ''),
                'rating': f.get('productValuation'),
                'text': f.get('text', ''),
                'pros': f.get('pros', ''),
                'cons': f.get('cons', ''),
                'created_date': f.get('createdDate', ''),
                'has_answer': f.get('answer') is not None,
                'answer_text': (f.get('answer') or {}).get('text', '')
            })
        return out

    def collect_all(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M')
        cards, all_reviews = [], []
        for nm_id in PRODUCT_IDS:
            log.info(f'Карточка {nm_id}...')
            card = self.get_card(nm_id)
            if card:
                cards.append(card)
                log.info(f'  {card["name"][:40]} | {card["price_rub"]}R | stock {card["stock_total"]}')
                revs = self.get_reviews(card['root'], nm_id)
                all_reviews.extend(revs)
                log.info(f'  root {card["root"]} -> отзывов: {len(revs)}')
            time.sleep(2)

        if cards:
            df = pd.DataFrame(cards)
            df.to_csv(self.data_dir / f'wb_cards_{ts}.csv', index=False)
            df.to_csv(self.data_dir / 'wb_cards_latest.csv', index=False)
            log.info(f'Карточек сохранено: {len(cards)}')
        if all_reviews:
            df = pd.DataFrame(all_reviews).drop_duplicates(subset='review_id')
            df.to_csv(self.data_dir / f'wb_reviews_{ts}.csv', index=False)
            df.to_csv(self.data_dir / 'wb_reviews_latest.csv', index=False)
            log.info(f'Уникальных отзывов сохранено: {len(df)}')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    WBFullCollector().collect_all()
