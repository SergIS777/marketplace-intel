"""LLM-ответчик на отзывах с few-shot на истории LOWENGRASS"""
import os
import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class LLMReviewer:
    def __init__(self, data_dir="/app/data"):
        self.data_dir = Path(data_dir)
        self.api_key = os.environ.get('MODEL_SCOPE_API_KEY', '')
        self.api_url = "https://api-inference.modelscope.ai/v1/chat/completions"
        self.model = "Qwen/Qwen3.5-27B"
        
        # Загружаем базу знаний (историю ответов)
        history_file = self.data_dir / 'history' / 'answered_reviews.csv'
        self.history = pd.read_csv(history_file) if history_file.exists() else pd.DataFrame()
        print(f"База знаний: {len(self.history)} пар вопрос-ответ")
    
    def find_similar_examples(self, review_text, n=3):
        """Находит n похожих реальных ответов из истории"""
        if self.history.empty:
            return []
        
        # Простой поиск по ключевым словам
        keywords = review_text.lower().split()[:5]
        scores = []
        
        for idx, row in self.history.iterrows():
            customer_text = str(row.get('customer_text', '')).lower()
            score = sum(1 for kw in keywords if kw in customer_text)
            scores.append((score, idx))
        
        # Берём top-n по score, фильтруем с score > 0
        scores.sort(reverse=True)
        examples = []
        for score, idx in scores[:n]:
            if score > 0:
                row = self.history.iloc[idx]
                examples.append({
                    'customer': row.get('customer_text', ''),
                    'seller': row.get('seller_response', '')
                })
        
        return examples
    
    def build_prompt(self, review, product_specs, examples):
        """Формирует промпт для LLM с контекстом"""
        prompt = f"""Ты — менеджер по работе с клиентами бренда LOWENGRASS. 
Отвечай вежливо, конкретно, решая проблему по делу. Всегда начинай с "Здравствуйте!" и подписывайся "С уважением, команда бренда LOWENGRASS".

КОНТЕКСТ ТОВАРА:
{product_specs}

ПРИМЕРЫ РЕАЛЬНЫХ ОТВЕТОВ LOWENGRASS (пиши в том же стиле):
"""
        
        for i, ex in enumerate(examples, 1):
            prompt += f"\nПример {i}:"
            prompt += f"\nОтзыв клиента: {ex['customer'][:150]}..."
            prompt += f"\nОтвет LOWENGRASS: {ex['seller'][:200]}..."
        
        prompt += f"\n\nТЕКУЩИЙ ОТЗЫВ (напиши ответ):"
        prompt += f"\n{review}"
        
        prompt += "\n\nВАЖНО: ответ должен быть ЗАВЕРШЁННЫМ, не обрывайся на полуслове. Закончи подпись 'С уважением, команда бренда LOWENGRASS'."
        return prompt
    
    def generate_draft(self, prompt):
        """Генерирует черновик ответа через ModelScope API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 700,
            "temperature": 0.7
        }
        
        r = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            return f"Ошибка API: {r.status_code}"
    
    def review_recent_negatives(self):
        """Обработка свежих негативных отзывов"""
        reviews_file = self.data_dir / 'wb_reviews_latest.csv'
        if not reviews_file.exists():
            print("Файл отзывов не найден")
            return []
        
        reviews = pd.read_csv(reviews_file)
        
        # Берём негатив (rating <= 3) за последние 7 дней
        cutoff = (datetime.now() - pd.Timedelta(days=7)).isoformat()
        negatives = reviews[
            (reviews['rating'] <= 3) & 
            (reviews['created_date'] >= cutoff)
        ]
        
        drafts_file = self.data_dir / 'drafts_latest.csv'
        old = pd.read_csv(drafts_file) if drafts_file.exists() else pd.DataFrame()
        done = set(old['review_id']) if len(old) else set()
        fresh = negatives[~negatives['review_id'].isin(done)]
        print(f"\nНегативных за 7 дней: {len(negatives)} | с черновиком: {len(negatives) - len(fresh)} | новых: {len(fresh)}")
        if len(fresh) == 0:
            print("Новых негативов нет — LLM не дёргаем, токены не тратим.")
            (self.data_dir / 'last_run_status.json').write_text('{"new_drafts": 0}')
            return []
        
        # Загружаем specs товаров
        products_yaml = self.data_dir.parent / 'products.yaml'
        specs = {}
        if products_yaml.exists():
            import yaml
            with open(products_yaml) as f:
                data = yaml.safe_load(f)
                for p in data.get('products', []):
                    specs[p['nm_id']] = f"Товар: {p['name']}\nХарактеристики:\n" + \
                        '\n'.join(f"  - {k}: {v}" for k, v in p.get('specs', {}).items())
        
        drafts = []
        for idx, row in fresh.head(5).iterrows():
            nm_id = row['nm_id']
            review_text = row['text']
            author = row['author'] if pd.notna(row['author']) else 'Аноним'
            
            print(f"\nОбработка отзыва от {author} ({int(row['rating'])}★)...")
            
            # Контекст товара
            product_specs = specs.get(nm_id, f"Товар #{nm_id}")
            
            # Ищем похожие примеры
            examples = self.find_similar_examples(review_text, n=3)
            print(f"  Найдено похожих примеров: {len(examples)}")
            
            # Формируем промпт
            prompt = self.build_prompt(review_text, product_specs, examples)
            
            # Генерируем черновик
            draft = self.generate_draft(prompt)
            
            drafts.append({
                'review_id': row['review_id'],
                'nm_id': nm_id,
                'author': author,
                'rating': int(row['rating']),
                'review_text': review_text,
                'draft_response': draft,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"  ✅ Черновик готов ({len(draft)} символов)")
        
        # Сохраняем черновики
        if drafts:
            df = pd.concat([old, pd.DataFrame(drafts)], ignore_index=True) if len(old) else pd.DataFrame(drafts)
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            df.to_csv(self.data_dir / f'drafts_{ts}.csv', index=False, encoding='utf-8')
            df.to_csv(drafts_file, index=False, encoding='utf-8')
            print(f"\nЧерновиков всего: {len(df)} (новых: {len(drafts)})")
            (self.data_dir / 'last_run_status.json').write_text(f'{{"new_drafts": {len(drafts)}}}')
        
        return drafts

if __name__ == '__main__':
    reviewer = LLMReviewer()
    drafts = reviewer.review_recent_negatives()
    
    if drafts:
        print(f"\n{'='*60}")
        print(f"ГОТОВЫЕ ЧЕРНОВИКИ:")
        print(f"{'='*60}")
        for i, d in enumerate(drafts, 1):
            print(f"\n{i}. {d['author']} ({d['rating']}★):")
            print(f"   Отзыв: {d['review_text'][:100]}...")
            print(f"   Черновик: {d['draft_response'][:200]}...")
