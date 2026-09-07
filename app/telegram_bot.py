"""LOWENGRASS Intel: бот-пульт (демо)"""
import os
import asyncio
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

DATA = Path('/app/data')
bot = Bot(token=os.environ.get('TELEGRAM_BOT_TOKEN', ''))
dp = Dispatcher()

PROMO = [
    ('🍂 Осенняя распродажа WB', 'активна до 15.09 — маржа выдержит?'),
    ('🔟 Мегараспродажа 10.10', '06-12.10, заявки до 03.10'),
    ('⬛ Чёрная пятница', '24-30.11, главный сейл года'),
    ('🎄 Новогодняя распродажа', '15.12-15.01'),
]

SHORT = {
    330990418: 'Швабра 30в1',
    618612802: 'Пароочиститель 6000Вт',
    912617526: 'Аэрогриль 15л',
    913015022: 'Аэрогриль 10л',
}

def short_name(row):
    return SHORT.get(int(row['nm_id']), str(row['name'])[:20])

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📦 Остатки', callback_data='stock'),
         InlineKeyboardButton(text='🚨 Алерты', callback_data='alerts')],
        [InlineKeyboardButton(text='💬 Отзывы', callback_data='reviews'),
         InlineKeyboardButton(text='✍️ Черновики', callback_data='drafts')],
        [InlineKeyboardButton(text='📊 Отчёт', callback_data='report'),
         InlineKeyboardButton(text='🎁 Акции', callback_data='promo')],
        [InlineKeyboardButton(text='📈 Дашборд', callback_data='dash'),
         InlineKeyboardButton(text='ℹ️ Помощь', callback_data='help')],
        [InlineKeyboardButton(text='🕵️ Конкуренты', callback_data='comp'), InlineKeyboardButton(text='📊 Темп продаж', callback_data='vel')],
    ])

async def send_stock(m):
    df = pd.read_csv(DATA / 'wb_cards_latest.csv')
    lines = ['📦 Остатки LOWENGRASS:\n']
    for _, r in df.iterrows():
        s = int(r['stock_total'])
        flag = '🛑' if s == 0 else ('🚨' if s <= 3 else ('⚠️' if s <= 10 else '✅'))
        price = f"{int(r['price_rub'])}₽" if r['price_rub'] > 0 else 'цена исчезла (нет в продаже)'
        lines.append(f"{flag} {int(r['nm_id'])} · {short_name(r)}\n   {price} | остаток: {s} шт | ★{r['review_rating']} | отзывов: {int(r['feedbacks_count'])}")
    await m.answer('\n'.join(lines))

async def send_alerts(m):
    f = DATA / 'events_latest.json'
    events = json.loads(f.read_text()) if f.exists() else []
    if not events:
        await m.answer('Событий нет 🎉')
        return
    icon = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'INFO': 'ℹ️'}
    lines = [f'🚨 Алерты ({len(events)}):\n']
    lines += [f"{icon.get(e['type'], '•')} {e['message']}\n" for e in events]
    await m.answer('\n'.join(lines))

async def send_reviews(m):
    cards = pd.read_csv(DATA / 'wb_cards_latest.csv')
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💬 {int(r['nm_id'])} · {short_name(r)}", callback_data=f"rev:{int(r['nm_id'])}")]
        for _, r in cards.iterrows()
    ])
    await m.answer('💬 Отзывы по какому товару показать?', reply_markup=kb)

@dp.callback_query(F.data.startswith('rev:'))
async def cb_reviews(c: CallbackQuery):
    nm_id = int(c.data.split(':')[1])
    cards = pd.read_csv(DATA / 'wb_cards_latest.csv')
    row = cards[cards['nm_id'] == nm_id].iloc[0]
    root = int(row['root'])
    df = pd.read_csv(DATA / 'wb_reviews_latest.csv')
    df = df[df['root'] == root].sort_values('created_date', ascending=False)
    neg = len(df[df['rating'] <= 2])
    lines = [f"💬 {int(row['nm_id'])} · {short_name(row)}\nОтзывов: {len(df)} | негативных: {neg}\n\nСвежие:\n"]
    for _, r in df.head(4).iterrows():
        author = r['author'] if pd.notna(r['author']) else 'Аноним'
        txt = str(r['text'])[:120] if pd.notna(r['text']) else '(без текста)'
        lines.append(f"{'⭐' * int(r['rating'])} {author} ({str(r['created_date'])[:10]})\n{txt}\n")
    await c.message.answer('\n'.join(lines))
    await c.answer()

async def send_drafts(m):
    f = DATA / 'drafts_latest.csv'
    if not f.exists():
        await m.answer('Черновиков нет.')
        return
    df = pd.read_csv(f)
    proc_file = DATA / 'processed_reviews.csv'
    done = set()
    if proc_file.exists():
        done = set(pd.read_csv(proc_file)['review_id'])
    df = df[~df['review_id'].isin(done)]
    if len(df) == 0:
        await m.answer('Все недавние негативы обработаны 👍\nНовые черновики появятся при новых отзывах.')
        return
    await m.answer('✍️ Черновики ответов на недавний негатив (ждут твоего решения).\nНовые появляются только при новых отзывах.\n')
    for _, r in df.head(4).iterrows():
        rid = r['review_id']
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Вариант LLM', callback_data=f'ok:{rid}'),
             InlineKeyboardButton(text='✍️ Напишу сам', callback_data=f'own:{rid}')],
            [InlineKeyboardButton(text='⏭ Пропустить', callback_data=f'skip:{rid}')]])
        await m.answer(f"💬 {r['author']} ({int(r['rating'])}★)\n\n📝 Отзыв полностью:\n{str(r['review_text'])[:3500]}")
        await m.answer(f"✍️ Черновик ответа (полный):\n\n{str(r['draft_response'])[:3500]}", reply_markup=kb)

async def send_report(m):
    f = DATA / 'lowengrass_stats.json'
    if not f.exists():
        await m.answer('Отчёта нет.')
        return
    s = json.loads(f.read_text())
    text = (f"📊 Отчёт LOWENGRASS\n\n• Отзывов: {s['total_reviews']}\n• Рейтинг: {s['avg_rating']}/5 ⭐\n"
            f"• Ответов продавца: {s['answer_rate']}%\n\nТоп похвал:\n"
            + '\n'.join(f"• {t}: {c}" for t, c in s['positive_themes_top10'][:4])
            + "\n\nТоп жалоб:\n"
            + '\n'.join(f"• {t}: {c}" for t, c in s['negative_themes_top10'][:4]))
    await m.answer(text)

async def send_promo(m):
    lines = ['🎁 Календарь акций WB:\n']
    lines += [f"• {name}\n  {note}\n" for name, note in PROMO]
    await m.answer('\n'.join(lines))

async def send_dash(m):
    await m.answer('📈 Дашборд LOWENGRASS (живые графики):\nhttp://46.17.101.142:8501')

async def send_velocity(m):
    snaps = sorted(DATA.glob('wb_cards_2*.csv'))
    if len(snaps) < 2:
        await m.answer('Снапшотов пока мало — темп появится после второго обновления (каждые 3 часа).')
        return
    prev = pd.read_csv(snaps[0])
    cur = pd.read_csv(snaps[-1])
    t1 = datetime.strptime(str(prev['timestamp'].iloc[0])[:16], '%Y-%m-%dT%H:%M')
    t2 = datetime.strptime(str(cur['timestamp'].iloc[0])[:16], '%Y-%m-%dT%H:%M')
    hours = max((t2 - t1).total_seconds() / 3600, 1)
    lines = [f'📊 Темп продаж (за {hours:.0f} ч, снапшотов: {len(snaps)}):\n' + ('' if hours >= 6 else '⚠️ Статистика копится — прогноз предварительный\n')]
    for _, c in cur.iterrows():
        p = prev[prev['nm_id'] == c['nm_id']]
        if p.empty:
            continue
        s = int(c['stock_total'])
        delta = int(p.iloc[0]['stock_total']) - s
        per_day = delta / hours * 24
        if s == 0:
            lines.append(f"🛑 {int(c['nm_id'])} · {short_name(c)}: OUT-OF-STOCK — раскупили")
        elif per_day > 0:
            days = s / per_day
            flag = '🚨' if days < 3 else ('⚠️' if days < 7 else '✅')
            lines.append(f"{flag} {int(c['nm_id'])} · {short_name(c)}: −{delta} шт ({per_day:.1f}/сут) → хватит на ~{days:.1f} дн")
        elif delta < 0:
            lines.append(f"⬆️ {int(c['nm_id'])} · {short_name(c)}: остаток вырос на {-delta} шт (дозаказ или возвраты)")
        else:
            lines.append(f"✅ {int(c['nm_id'])} · {short_name(c)}: продаж нет, остаток {s} шт")
    await m.answer('\n'.join(lines))

async def send_help(m):
    await m.answer(
        'ℹ️ Разделы:\n\n📦 Остатки — склады, красный флаг если кончается\n🚨 Алерты — критичные события\n'
        '💬 Отзывы — свежие отзывы покупателей\n✍️ Черновики — ответы LLM, «Одобрить» сохраняет в базу знаний\n'
        '📊 Отчёт — аналитика: рейтинг, темы, жалобы\n🎁 Акции — календарь распродаж\n🕵️ Конкуренты — их цены, остатки и темп продаж\n📊 Темп продаж — продажи в день и на сколько дней хватит остатка\n📈 Дашборд — ссылка на графики')

@dp.message(Command('start'))
async def cmd_start(m: Message):
    await m.answer('🤖 LOWENGRASS Intel — пульт управления магазином', reply_markup=menu())

@dp.message(Command('stock'))
async def c1(m: Message): await send_stock(m)
@dp.message(Command('alerts'))
async def c2(m: Message): await send_alerts(m)
@dp.message(Command('reviews'))
async def c3(m: Message): await send_reviews(m)
@dp.message(Command('drafts'))
async def c4(m: Message): await send_drafts(m)
@dp.message(Command('report'))
async def c5(m: Message): await send_report(m)
@dp.message(Command('promo'))
async def c6(m: Message): await send_promo(m)
@dp.message(Command('help'))
async def c7(m: Message): await send_help(m)
@dp.message(Command('dashboard'))
async def c8(m: Message): await send_dash(m)
@dp.message(Command('velocity'))
async def c9(m: Message): await send_velocity(m)

@dp.callback_query(F.data == 'stock')
async def q1(c: CallbackQuery): await send_stock(c.message); await c.answer()
@dp.callback_query(F.data == 'alerts')
async def q2(c: CallbackQuery): await send_alerts(c.message); await c.answer()
@dp.callback_query(F.data == 'reviews')
async def q3(c: CallbackQuery): await send_reviews(c.message); await c.answer()
@dp.callback_query(F.data == 'drafts')
async def q4(c: CallbackQuery): await send_drafts(c.message); await c.answer()
@dp.callback_query(F.data == 'report')
async def q5(c: CallbackQuery): await send_report(c.message); await c.answer()
@dp.callback_query(F.data == 'promo')
async def q6(c: CallbackQuery): await send_promo(c.message); await c.answer()
@dp.callback_query(F.data == 'dash')
async def q7(c: CallbackQuery): await send_dash(c.message); await c.answer()
@dp.callback_query(F.data == 'help')
async def q8(c: CallbackQuery): await send_help(c.message); await c.answer()
@dp.callback_query(F.data == 'vel')
async def q9(c: CallbackQuery): await send_velocity(c.message); await c.answer()

async def send_competitors(m):
    f = DATA / 'competitors_latest.csv'
    if not f.exists():
        await m.answer('Данных по конкурентам пока нет. Запусти collectors/comp_discovery.py, затем comp_collector.py.')
        return
    cur = pd.read_csv(f)
    if 'for_nm' not in cur.columns:
        await m.answer('Старый формат данных: запусти comp_discovery.py и comp_collector.py.')
        return
    snaps = sorted(DATA.glob('competitors_2*.csv'))
    prev = pd.read_csv(snaps[-2]) if len(snaps) >= 2 else None
    ours = pd.read_csv(DATA / 'wb_cards_latest.csv')
    sent = 0
    for fnm, grp in cur.groupby('for_nm'):
        fnm = int(fnm)
        o = ours[ours['nm_id'] == fnm]
        our_price = None
        if len(o):
            o = o.iloc[0]
            head = f"🕵️ Конкуренты · {short_name(o)} ({fnm})\n   мы: {int(o['price_rub'])}₽ | остаток {int(o['stock_total'])}"
            our_price = float(o['price_rub'])
        else:
            head = f"🕵️ Конкуренты · {fnm}"
        lines = [head]
        for _, r in grp.head(4).iterrows():
            st = int(r['stock_total'])
            flag = '🛑' if st == 0 else ('⚠️' if st <= 10 else '✅')
            line = f"{flag} {int(r['nm_id'])} · {str(r['name'])[:55]}: {int(r['price_rub'])}₽ | ост {st}"
            if our_price and r['price_rub'] < our_price:
                line += f" | 🚨 дешевле нас на {int(our_price - r['price_rub'])}₽"
            if prev is not None:
                prow = prev[prev['nm_id'] == r['nm_id']]
                if len(prow):
                    d = int(prow.iloc[0]['stock_total']) - st
                    if d > 0:
                        line += f" | темп −{d}"
                    elif d < 0:
                        line += f" | ⬆️ +{-d}"
            lines.append(line)
        await m.answer('\n'.join(lines))
        sent += 1
    if not sent:
        await m.answer('Конкуренты не найдены.')

@dp.callback_query(F.data == 'comp')
async def q10(c: CallbackQuery):
    await send_competitors(c.message)
    await c.answer()

@dp.message(Command('competitors'))
async def c10(m: Message): await send_competitors(m)

PENDING_OWN = {}

def _save_pair(row, response, source):
    hist_file = DATA / 'history' / 'answered_reviews.csv'
    hist = pd.read_csv(hist_file)
    new = pd.DataFrame([{'nm_id': row['nm_id'], 'customer_text': row['review_text'],
        'seller_response': response, 'rating': row['rating'],
        'created_date': row['timestamp'], 'review_id': row['review_id'], 'source': source}])
    pd.concat([hist, new], ignore_index=True).to_csv(hist_file, index=False)
    return len(hist) + 1

def _mark_processed(rid, action):
    proc_file = DATA / 'processed_reviews.csv'
    old = pd.read_csv(proc_file) if proc_file.exists() else pd.DataFrame(columns=['review_id', 'action', 'ts'])
    pd.concat([old, pd.DataFrame([{'review_id': rid, 'action': action, 'ts': datetime.now().isoformat()}])],
              ignore_index=True).to_csv(proc_file, index=False)

@dp.callback_query(F.data.startswith('ok:'))
async def cb_approve(c: CallbackQuery):
    rid = c.data.split(':')[1]
    r = pd.read_csv(DATA / 'drafts_latest.csv')
    r = r[r['review_id'] == rid].iloc[0]
    n = _save_pair(r, r['draft_response'], 'llm')
    _mark_processed(rid, 'llm')
    await c.message.edit_reply_markup(reply_markup=None)
    await c.message.answer(f"✅ Вариант LLM одобрен! База знаний: {n} пар.")

@dp.callback_query(F.data.startswith('own:'))
async def cb_own(c: CallbackQuery):
    rid = c.data.split(':')[1]
    PENDING_OWN[c.from_user.id] = rid
    await c.message.edit_reply_markup(reply_markup=None)
    await c.message.answer('✍️ Пришли свой вариант ответа одним сообщением.\nСохраню пару «отзыв → твой текст» в базу знаний.\n/cancel — отмена.')

@dp.callback_query(F.data.startswith('skip:'))
async def cb_skip(c: CallbackQuery):
    rid = c.data.split(':')[1]
    _mark_processed(rid, 'skip')
    await c.message.edit_reply_markup(reply_markup=None)
    await c.message.answer('⏭ Пропущено. Отзыв больше не будет всплывать.')

@dp.message(Command('cancel'))
async def c_cancel(m: Message):
    PENDING_OWN.pop(m.from_user.id, None)
    await m.answer('Отменено. Ничего не сохранено.')

@dp.message(F.text)
async def h_own_text(m: Message):
    rid = PENDING_OWN.pop(m.from_user.id, None)
    if rid is None:
        return
    r = pd.read_csv(DATA / 'drafts_latest.csv')
    r = r[r['review_id'] == rid].iloc[0]
    n = _save_pair(r, m.text, 'human')
    _mark_processed(rid, 'human')
    await m.answer(f"✅ Твой вариант сохранён! База знаний: {n} пар.\nСистема будет учиться на твоём ответе.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
