"""Автономность: пайплайн каждые 3 часа + утренний отчёт 09:00"""
import os
import asyncio
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA = Path('/app/data')
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OWNER = 517455356  # ← твой chat_id из @userinfobot
DASH = 'http://46.17.101.142:8501'

def tg(text):
    if OWNER and TOKEN:
        requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                      json={'chat_id': OWNER, 'text': text}, timeout=10)

async def run(cmd):
    p = await asyncio.create_subprocess_shell(cmd, cwd='/app')
    await p.wait()

def stock_diff():
    snaps = sorted(DATA.glob('wb_cards_2*.csv'))
    if len(snaps) < 2:
        return ''
    prev = pd.read_csv(snaps[-2]).set_index('nm_id')
    cur = pd.read_csv(snaps[-1]).set_index('nm_id')
    lines = []
    for nm, c in cur.iterrows():
        if nm not in prev.index:
            continue
        p = int(prev.loc[nm, 'stock_total']); s = int(c['stock_total'])
        if s == 0 and p > 0:
            lines.append(f"🛑 {int(nm)} · {str(c['name'])[:18]}: {p} → 0 — ушёл в out-of-stock")
        elif s > p:
            lines.append(f"⬆️ {int(nm)} · {str(c['name'])[:18]}: {p} → {s} (+{s - p}, дозаказ/возвраты)")
        elif s < p:
            lines.append(f"⬇️ {int(nm)} · {str(c['name'])[:18]}: {p} → {s} (−{p - s}, продажи)")
    return '\n'.join(lines)

def reviews_diff():
    snaps = sorted(DATA.glob('wb_reviews_2*.csv'))
    if len(snaps) < 2:
        return 0, 0
    prev = set(pd.read_csv(snaps[-2])['review_id'])
    cur = pd.read_csv(snaps[-1])
    new = cur[~cur['review_id'].isin(prev)]
    return len(new), int((new['rating'] <= 2).sum())

async def refresh():
    tg('🔄 Обновляю данные: карточки, остатки, отзывы...')
    if datetime.now().hour == 6:
        await run('python collectors/comp_discovery.py')
    await run('python collectors/wb_full_collector.py')
    await run('python diff_analyzer.py')
    await run('python collectors/comp_collector.py')
    await run('python llm_reviewer.py')
    nd = 0
    st_file = DATA / 'last_run_status.json'
    if st_file.exists():
        try:
            nd = int(json.loads(st_file.read_text()).get('new_drafts', 0))
        except Exception:
            nd = 0
    parts = [f'✅ Данные обновлены ({datetime.now():%H:%M}).']
    sd = stock_diff()
    if sd:
        parts.append('📦 Изменения остатков:\n' + sd)
    nr, neg = reviews_diff()
    if nr:
        parts.append(f'💬 Новых отзывов: {nr} (негативных: {neg})' + (' — черновики готовы в ✍️.' if nd else ''))
    else:
        parts.append('💬 Новых отзывов нет — черновики без изменений.' + (f' Новых негативов: {nd}, черновики в ✍️.' if nd else ''))
    tg('\n\n'.join(parts))

def morning():
    cards = pd.read_csv(DATA / 'wb_cards_latest.csv')
    f = DATA / 'events_latest.json'
    events = json.loads(f.read_text()) if f.exists() else []
    icon = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'INFO': 'ℹ️'}
    lines = [f"📊 Утренний отчёт LOWENGRASS ({datetime.now():%d.%m.%Y})\n"]
    for e in events[:6]:
        lines.append(f"{icon.get(e['type'], '•')} {e['message']}\n")
    low = cards[cards['stock_total'] <= 10]
    if len(low):
        lines.append('📦 Низкий остаток: ' + ', '.join(str(n)[:25] for n in low['name']))
    lines.append(f"\n📈 Дашборд: {DASH}")
    tg('\n'.join(lines))

async def main():
    st = {'ref': '', 'mor': ''}
    while True:
        await asyncio.sleep(20)
        n = datetime.now()
        if n.minute < 1 and n.hour % 3 == 0 and st['ref'] != n.strftime('%Y%m%d%H'):
            st['ref'] = n.strftime('%Y%m%d%H')
            await refresh()
        if n.hour == 9 and n.minute < 1 and st['mor'] != n.strftime('%Y%m%d'):
            st['mor'] = n.strftime('%Y%m%d')
            morning()

if __name__ == '__main__':
    asyncio.run(main())
