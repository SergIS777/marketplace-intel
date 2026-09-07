"""Аналитика отзывов Wildberries для отчёта LOWENGRASS"""
import pandas as pd
from collections import Counter
import json
from pathlib import Path
from datetime import datetime

class WBReviewsAnalyzer:
    def __init__(self, data_dir="/app/data"):
        self.data_dir = Path(data_dir)
    
    def analyze(self):
        """Полная аналитика отзывов"""
        df = pd.read_csv(self.data_dir / 'wb_reviews_clean.csv')
        
        # Основные метрики
        stats = {
            'total_reviews': len(df),
            'avg_rating': round(df['rating'].mean(), 2),
            'reviews_with_text': int(df[df['text'].str.len() > 0].shape[0]),
            'reviews_with_answers': int(df['has_answer'].sum()),
            'answer_rate': round(df['has_answer'].sum() / len(df) * 100, 1),
            'rating_distribution': df['rating'].value_counts().sort_index().to_dict(),
            'latest_review_date': df['created_date'].max()[:10],
            'oldest_review_date': df['created_date'].min()[:10]
        }
        
        # Анализ ключевых слов в позитивных отзывах (4-5 звёзд)
        positive = df[df['rating'] >= 4]['text'].dropna()
        positive_keywords = ['мощный', 'качество', 'быстро', 'чистит', 'отличный', 'нравится', 
                           'рекомендую', 'удобный', 'хороший', 'справляется', 'супер', 'класс']
        
        positive_themes = Counter()
        for text in positive:
            text_lower = text.lower()
            for kw in positive_keywords:
                if kw in text_lower:
                    positive_themes[kw] += 1
        
        stats['positive_themes_top10'] = positive_themes.most_common(10)
        
        # Анализ ключевых слов в негативных отзывах (1-2 звезды)
        negative = df[df['rating'] <= 2]['text'].dropna()
        negative_keywords = ['брак', 'вернуть', 'отказ', 'не работает', 'поломка', 'обман', 
                           'пункт', 'не выдали', 'пришел', 'мощность', 'пустой', 'запах']
        
        negative_themes = Counter()
        for text in negative:
            text_lower = text.lower()
            for kw in negative_keywords:
                if kw in text_lower:
                    negative_themes[kw] += 1
        
        stats['negative_themes_top10'] = negative_themes.most_common(10)
        
        # Топ-5 примеров с текстом
        stats['best_reviews'] = []
        best = df[(df['rating'] == 5) & (df['text'].str.len() > 80)].sort_values('created_date', ascending=False).head(5)
        for _, row in best.iterrows():
            stats['best_reviews'].append({
                'author': row['author'] if pd.notna(row['author']) else 'Аноним',
                'date': row['created_date'][:10],
                'text': row['text'][:250]
            })
        
        stats['worst_reviews'] = []
        worst = df[(df['rating'] <= 2) & (df['text'].str.len() > 40)].sort_values('created_date', ascending=False).head(5)
        for _, row in worst.iterrows():
            stats['worst_reviews'].append({
                'author': row['author'] if pd.notna(row['author']) else 'Аноним',
                'date': row['created_date'][:10],
                'rating': int(row['rating']),
                'text': row['text'][:250]
            })
        
        return stats
    
    def generate_report(self):
        """Генерирует текстовый отчёт"""
        stats = self.analyze()
        
        report = f"""# ОТЧЁТ ПО ОТЗЫВАМ LOWENGRASS
Сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## ОБЩИЕ ПОКАЗАТЕЛИ
- Всего отзывов: {stats['total_reviews']}
- Средний рейтинг: {stats['avg_rating']}/5.0
- Отзывов с текстом: {stats['reviews_with_text']}
- Ответов продавца: {stats['reviews_with_answers']} ({stats['answer_rate']}%)
- Период: {stats['oldest_review_date']} — {stats['latest_review_date']}

## РАСПРЕДЕЛЕНИЕ РЕЙТИНГА
"""
        for rating in sorted(stats['rating_distribution'].keys(), reverse=True):
            count = stats['rating_distribution'][rating]
            percent = round(count / stats['total_reviews'] * 100, 1)
            bar = '█' * int(percent / 2)
            report += f"- {rating}⭐: {count} ({percent}%) {bar}\n"
        
        report += f"""
## ТОП ПОЗИТИВНЫХ ТЕМ (4-5 звёзд)
"""
        for theme, count in stats['positive_themes_top10']:
            report += f"- {theme}: {count} упоминаний\n"
        
        report += f"""
## ТОП ЖАЛОБ (1-2 звезды)
"""
        for theme, count in stats['negative_themes_top10']:
            report += f"- {theme}: {count} упоминаний\n"
        
        report += f"""
## ЛУЧШИЕ ОТЗЫВЫ (для демонстрации клиентам)
"""
        for i, r in enumerate(stats['best_reviews'], 1):
            report += f"{i}. [{r['author']}, {r['date']}]\n   {r['text']}\n\n"
        
        report += f"""
## ПРОБЛЕМНЫЕ ОТЗЫВЫ (для работы над ошибками)
"""
        for i, r in enumerate(stats['worst_reviews'], 1):
            report += f"{i}. [{r['author']}, {r['date']}] ⭐{r['rating']}\n   {r['text']}\n\n"
        
        report += f"""
## РЕКОМЕНДАЦИИ LOWENGRASS
1. ОТЛИЧНАЯ РАБОТА: {stats['answer_rate']}% отзывов с ответом — это очень высокий показатель
2. СИЛЬНЫЕ СТОРОНЫ (подсвечивать в маркетинге):
   - Мощность и эффективность чистки
   - Универсальность применения
   - Хорошая комплектация
3. ТОЧКИ РОСТА:
   - Улучшить упаковку (жалобы на повреждённый товар)
   - Проверка комплектации перед отправкой
   - Работа с возвратами по браку
"""
        
        # Сохраняем отчёт
        report_path = self.data_dir / 'lowengrass_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Сохраняем статистику в JSON для бота
        stats_path = self.data_dir / 'lowengrass_stats.json'
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        return report

if __name__ == '__main__':
    analyzer = WBReviewsAnalyzer()
    report = analyzer.generate_report()
    print(report)
