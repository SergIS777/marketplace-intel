"""Diff-анализатор: снапшоты -> события для алертов"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import logging

log = logging.getLogger("intel.analyzer")

class DiffAnalyzer:
    def __init__(self, data_dir="/app/data"):
        self.data_dir = Path(data_dir)

    def analyze(self):
        events = []
        cur = pd.read_csv(self.data_dir / 'wb_cards_latest.csv')

        # Предыдущий снапшот для diff (если есть)
        snapshots = sorted(self.data_dir.glob('wb_cards_2*.csv'))
        prev = pd.read_csv(snapshots[-2]) if len(snapshots) >= 2 else None

        # 1. Остатки
        for _, row in cur.iterrows():
            stock = row['stock_total']
            if stock <= 3:
                events.append({'type': 'CRITICAL', 'category': 'stock', 'nm_id': int(row['nm_id']),
                    'message': f"{row['name'][:40]}: ОСТАТОК {int(stock)} шт — скоро out-of-stock!"})
            elif stock <= 10:
                events.append({'type': 'WARNING', 'category': 'stock', 'nm_id': int(row['nm_id']),
                    'message': f"{row['name'][:40]}: низкий остаток ({int(stock)} шт)"})

            # 2. Изменение цены между снапшотами
            if prev is not None:
                old = prev[prev['nm_id'] == row['nm_id']]
                if not old.empty and old.iloc[0]['price_rub'] != row['price_rub']:
                    delta = row['price_rub'] - old.iloc[0]['price_rub']
                    events.append({'type': 'INFO', 'category': 'price', 'nm_id': int(row['nm_id']),
                        'message': f"{row['name'][:40]}: цена {old.iloc[0]['price_rub']:.0f} -> {row['price_rub']:.0f} ({delta:+.0f})"})

        # 3. Свежий негатив (7 дней)
        rev_file = self.data_dir / 'wb_reviews_latest.csv'
        if rev_file.exists():
            rev = pd.read_csv(rev_file)
            neg = rev[(rev['rating'] <= 2) & (rev['created_date'] >= '2026-08-29')]
            for _, r in neg.head(5).iterrows():
                author = r['author'] if pd.notna(r['author']) else 'Аноним'
                events.append({'type': 'WARNING', 'category': 'negative_review', 'nm_id': int(r['nm_id']),
                    'message': f"Негатив {int(r['rating'])}★ от {author}: {str(r['text'])[:80]}"})

        with open(self.data_dir / 'events_latest.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        return events

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    events = DiffAnalyzer().analyze()
    print(f"\n=== СОБЫТИЙ: {len(events)} ===")
    for e in events:
        icon = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'INFO': 'ℹ️'}.get(e['type'], '•')
        print(f"{icon} [{e['category']}] {e['message']}")
