"""Парсер отзывов Wildberries через публичный API (без Selenium)"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

class WBReviewsParser:
    def __init__(self, data_dir="/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Origin': 'https://www.wildberries.ru',
            'Referer': 'https://www.wildberries.ru/'
        }
    
    def get_root(self, nm_id):
        """Получает root ID товара через v4 endpoint"""
        url = f'https://card.wb.ru/cards/v4/detail?appType=1&curr=rub&dest=-1257786&nm={nm_id}'
        r = requests.get(url, headers=self.headers, timeout=10)
        if r.status_code == 200:
            products = r.json().get('products', [])
            if products:
                return products[0].get('root')
        return None
    
    def get_reviews(self, root):
        """Получает все отзывы по root"""
        url = f'https://feedbacks1.wb.ru/feedbacks/v1/{root}'
        r = requests.get(url, headers=self.headers, timeout=15)
        if r.status_code == 200:
            return r.json().get('feedbacks', [])
        return []
    
    def parse_product(self, nm_id):
        """Парсит отзывы для одного товара"""
        print(f'\nПарсинг товара nm_id={nm_id}...')
        
        # Шаг 1: получаем root
        root = self.get_root(nm_id)
        if not root:
            print(f'  Не удалось получить root для {nm_id}')
            return []
        print(f'  root={root}')
        
        # Шаг 2: получаем отзывы
        reviews_raw = self.get_reviews(root)
        print(f'  Получено отзывов: {len(reviews_raw)}')
        
        # Шаг 3: преобразуем в удобный формат
        reviews = []
        for r in reviews_raw:
            reviews.append({
                'nm_id': nm_id,
                'review_id': r.get('id'),
                'author': r.get('wbUserDetails', {}).get('name', 'Аноним'),
                'rating': r.get('productValuation'),
                'text': r.get('text', ''),
                'pros': r.get('pros', ''),
                'cons': r.get('cons', ''),
                'color': r.get('color', ''),
                'created_date': r.get('createdDate', ''),
                'updated_date': r.get('updatedDate', ''),
                'has_answer': r.get('answer') is not None,
                'answer_text': r.get('answer', {}).get('text', '') if r.get('answer') else ''
            })
        return reviews
    
    def parse_all(self, nm_ids):
        """Парсит отзывы для нескольких товаров"""
        all_reviews = []
        for nm_id in nm_ids:
            reviews = self.parse_product(nm_id)
            all_reviews.extend(reviews)
            time.sleep(2)  # Rate limit
        
        return all_reviews
    
    def save(self, reviews):
        """Сохраняет отзывы в CSV"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        if reviews:
            df = pd.DataFrame(reviews)
            df.to_csv(self.data_dir / f'wb_reviews_{timestamp}.csv', index=False, encoding='utf-8')
            df.to_csv(self.data_dir / 'wb_reviews_latest.csv', index=False, encoding='utf-8')
            print(f'\nСохранено {len(reviews)} отзывов')
            print(f'Файлы: wb_reviews_{timestamp}.csv, wb_reviews_latest.csv')
            
            # Статистика
            print('\n=== Статистика ===')
            print(f'Средний рейтинг: {df["rating"].mean():.2f}')
            print(f'Отзывов с текстом: {df[df["text"].str.len() > 0].shape[0]}')
            print(f'Отзывов с ответом продавца: {df["has_answer"].sum()}')
            print(f'\nРаспределение рейтингов:')
            for rating in sorted(df['rating'].unique()):
                count = df[df['rating'] == rating].shape[0]
                print(f'  {rating}⭐: {count} отзывов')

if __name__ == '__main__':
    # nm_id товаров LOWENGRASS из последнего снапшота
    products_df = pd.read_csv('/app/data/wb_products_latest.csv')
    nm_ids = products_df['nm_id'].tolist()
    
    print(f'=== Парсер отзывов Wildberries ===')
    print(f'Товаров для парсинга: {len(nm_ids)}')
    print(f'nm_ids: {nm_ids}')
    
    parser = WBReviewsParser()
    reviews = parser.parse_all(nm_ids)
    parser.save(reviews)
    
    print('\nГотово!')
