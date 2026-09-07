import asyncio
from playwright.async_api import async_playwright
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

log = logging.getLogger("intel.wb.reviews")

async def parse_reviews(nm_id: int, max_reviews: int = 50):
    """Парсит отзывы со страницы товара через браузер"""
    url = f"https://www.wildberries.ru/catalog/{nm_id}/detail.aspx"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        log.info(f"Открываю страницу товара {nm_id}")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Ждём появления кнопки "Все отзывы" или раздела отзывов
        await page.wait_for_timeout(3000)
        
        # Ищем кнопку "Все отзывы" или "Отзывы"
        reviews_button = None
        for selector in [
            'button:has-text("Все отзывы")',
            'button:has-text("отзыв")',
            '[data-wba-header-cart-btn]',
            'a[href*="otzyvy"]',
            'button[data-link="text=Все отзывы"]'
        ]:
            try:
                if await page.locator(selector).count() > 0:
                    reviews_button = page.locator(selector).first
                    log.info(f"Найдена кнопка: {selector}")
                    break
            except:
                continue
        
        if reviews_button:
            await reviews_button.click()
            await page.wait_for_timeout(3000)
        
        # Перехватываем сетевые запросы к API отзывов
        feedbacks_data = []
        
        async def handle_response(response):
            url = response.url
            if 'feedbacks' in url or 'review' in url:
                try:
                    data = await response.json()
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if 'feedback' in key.lower() or 'review' in key.lower():
                                feedbacks_data.append(value)
                except:
                    pass
        
        page.on("response", handle_response)
        
        # Прокручиваем страницу чтобы подгрузить отзывы
        for i in range(10):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(1000)
        
        await browser.close()
        
        # Также попробуем извлечь отзывы из HTML
        # (запустим ещё раз для парсинга DOM)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Ищем отзывы в DOM
            review_elements = await page.locator('.feedback__item, .review-item, [data-feedback-id]').all()
            log.info(f"Найдено review-элементов в DOM: {len(review_elements)}")
            
            reviews = []
            for elem in review_elements[:max_reviews]:
                try:
                    text = await elem.inner_text()
                    reviews.append({
                        "nm_id": nm_id,
                        "text": text[:500],
                        "source": "dom",
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    pass
            
            await browser.close()
            
            # Объединяем данные из сети и DOM
            all_reviews = reviews
            
            # Добавляем данные из перехваченных запросов
            for data in feedbacks_data:
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            all_reviews.append({
                                "nm_id": nm_id,
                                "text": item.get("text", ""),
                                "rating": item.get("productValuation") or item.get("rating"),
                                "author": item.get("userName") or item.get("author"),
                                "date": item.get("createdDate") or item.get("date"),
                                "source": "network",
                                "timestamp": datetime.now().isoformat()
                            })
            
            return all_reviews

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    nm_ids = [330990418, 618612802]
    
    for nm_id in nm_ids:
        log.info(f"=== Парсю отзывы для nm_id {nm_id} ===")
        reviews = await parse_reviews(nm_id)
        
        if reviews:
            df = pd.DataFrame(reviews)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = f"/app/data/wb_reviews_{nm_id}_{timestamp}.csv"
            df.to_csv(output_path, index=False)
            log.info(f"Сохранено {len(reviews)} отзывов в {output_path}")
            
            # Показываем первые 3
            for r in reviews[:3]:
                log.info(f"  Отзыв: {r.get('text', '')[:100]}...")
        else:
            log.warning(f"Отзывы не найдены для nm_id {nm_id}")

if __name__ == "__main__":
    asyncio.run(main())
