"""LOWENGRASS Intel: дашборд (Streamlit + Plotly)"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

DATA = Path('/app/data')
st.set_page_config(page_title='LOWENGRASS Intel', page_icon='📊', layout='wide')
st.title('📊 Marketplace Intelligence: LOWENGRASS')

cards = pd.read_csv(DATA / 'wb_cards_latest.csv')
reviews_all = pd.read_csv(DATA / 'wb_reviews_latest.csv').drop_duplicates(subset='review_id')
reviews = reviews_all[reviews_all['text'].notna()]

m1, m2, m3, m4 = st.columns(4)
m1.metric('Товаров', len(cards))
m2.metric('Отзывов', len(reviews_all), f"{reviews_all['rating'].mean():.2f}★")
m3.metric('Негатив (≤2★)', int((reviews_all['rating'] <= 2).sum()))
m4.metric('Риск out-of-stock', int((cards['stock_total'] <= 3).sum()))
st.divider()

c1, c2 = st.columns(2)
with c1:
    st.subheader('📦 Остатки по товарам')
    colors = ['#d62728' if s <= 3 else '#ff7f0e' if s <= 10 else '#2ca02c' for s in cards['stock_total']]
    fig = go.Figure(go.Bar(x=[n[:25] for n in cards['name']], y=cards['stock_total'], marker_color=colors))
    fig.update_layout(yaxis_title='шт', height=350)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader('⭐ Распределение оценок')
    dist = reviews['rating'].value_counts().sort_index(ascending=False)
    fig2 = px.pie(names=dist.index.astype(str) + '★', values=dist.values, hole=0.4)
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.subheader('📈 Динамика отзывов')
    rev = reviews.copy()
    rev['date'] = pd.to_datetime(rev['created_date']).dt.to_period('M').astype(str)
    dyn = rev.groupby('date').size().reset_index(name='count')
    fig3 = px.line(dyn, x='date', y='count', markers=True)
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)
with c4:
    st.subheader('🚨 Алерты')
    f = DATA / 'events_latest.json'
    events = json.loads(f.read_text()) if f.exists() else []
    for e in events:
        icon = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'INFO': 'ℹ️'}.get(e['type'], '•')
        st.markdown(f"**{icon}** {e['message']}")

st.subheader('💬 Свежий негатив (требует ответа)')
neg = reviews[reviews['rating'] <= 2].sort_values('created_date', ascending=False)
st.dataframe(neg[['author', 'rating', 'text', 'created_date']].head(10), use_container_width=True)

st.divider()
st.header('🕵️ Конкуренты')
comp_file = DATA / 'competitors_latest.csv'
if comp_file.exists():
    comp = pd.read_csv(comp_file)
    snaps = sorted(DATA.glob('competitors_2*.csv'))
    prev = pd.read_csv(snaps[-2]) if len(snaps) >= 2 else None
    cards = pd.read_csv(DATA / 'wb_cards_latest.csv')
    if 'for_nm' not in comp.columns:
        st.info('Старый формат: запусти collectors/comp_discovery.py')
    else:
        for fnm, grp in comp.groupby('for_nm'):
            fnm = int(fnm)
            o = cards[cards['nm_id'] == fnm]
            our_price = None
            title = f'{fnm}'
            if len(o):
                o = o.iloc[0]
                our_price = float(o['price_rub'])
                title = f"{str(o['name'])[:44]} · мы: {int(our_price)}₽ | остаток {int(o['stock_total'])}"
            st.subheader(title)
            rows = []
            for _, r in grp.iterrows():
                vel = ''
                if prev is not None:
                    pr = prev[prev['nm_id'] == r['nm_id']]
                    if len(pr):
                        d = int(pr.iloc[0]['stock_total']) - int(r['stock_total'])
                        vel = f'-{d}' if d > 0 else (f'+{-d}' if d < 0 else '0')
                delta = int(our_price - r['price_rub']) if our_price else None
                rows.append({'артикул': int(r['nm_id']), 'продавец': str(r['brand'])[:16],
                             'цена, ₽': int(r['price_rub']), 'остаток': int(r['stock_total']),
                             'темп': vel, 'дешевле нас, ₽': delta if delta is not None and delta > 0 else ''})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
            if our_price:
                dfc = pd.DataFrame(rows)
                dfc['артикул'] = dfc['артикул'].astype(str)
                dfc = pd.DataFrame(rows)
                dfc['артикул'] = dfc['артикул'].astype(str)
                fig = px.bar(dfc, x='артикул', y='цена, ₽',
                             title='Цены: мы против конкурентов')
                fig.update_xaxes(type='category')
                fig.add_hline(y=our_price, line_dash='dash', line_color='green',
                              annotation_text='наша цена')
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info('Нет данных по конкурентам: запусти collectors/comp_discovery.py и comp_collector.py')
