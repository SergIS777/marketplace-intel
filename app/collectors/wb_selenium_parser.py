"""Selenium парсер отзывов и деталей товаров WB"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd

log = logging.getLogger("intel.wb.selenium")

class WBSeleniumParser:
    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Настройки Chrome для headless режима
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Обход детекции webdriver
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Скрываем webdriver флаг
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        
        self.wait = WebDriverWait(self.driver, 10)
    
    def parse_product_page(self, nm_id: int) -> Dict:
        """Парсит страницу товара: отзывы, описание, характеристики"""
        url = f"https://www.wildberries.ru/catalog/{nm_id}/detail.aspx"
        
        try:
            log.info(f"Открываю страницу товара {nm_id}")
            self.driver.get(url)
            time.sleep(8)
            
            result = {
                "nm_id": nm_id,
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
            
            # Парсим отзывы
            result["reviews"] = self._parse_reviews()
            
            # Парсим описание
            result["description"] = self._parse_description()
            
            # Парсим характеристики
            result["characteristics"] = self._parse_characteristics()
            
            # Парсим акции
            result["promotions"] = self._parse_promotions()
            
            return result
            
        except Exception as e:
            log.error(f"Ошибка парсинга страницы {nm_id}: {e}")
            return {"nm_id": nm_id, "error": str(e)}
    
    def _parse_reviews(self) -> List[Dict]:
        """Парсит отзывы со страницы"""
        reviews = []
        
        try:
            # Кликаем на кнопку "Все отзывы"
            try:
                reviews_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.comments__btn-all, a.comments__btn-all"))
                )
                reviews_button.click()
                time.sleep(3)
            except TimeoutException:
                log.warning("Кнопка отзывов не найдена")
                return reviews
            
            # Прокручиваем для подгрузки отзывов
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(2)
            
            # Парсим отзывы
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.comments__item")
            
            for elem in review_elements[:10]:  # Берём первые 10 отзывов
                try:
                    review_data = {}
                    
                    # Автор
                    try:
                        author = elem.find_element(By.CSS_SELECTOR, "p.feedback__header").text.strip()
                        review_data["author"] = author
                    except NoSuchElementException:
                        review_data["author"] = "Аноним"
                    
                    # Рейтинг
                    try:
                        rating_elem = elem.find_element(By.CSS_SELECTOR, "span.feedback__rating")
                        rating_classes = rating_elem.get_attribute("class") or ""
                        rating = next((int(cls[4:]) for cls in rating_classes.split() if cls.startswith("star") and cls[4:].isdigit()), 0)
                        review_data["rating"] = rating
                    except NoSuchElementException:
                        review_data["rating"] = 0
                    
                    # Дата
                    try:
                        date_elem = elem.find_element(By.CSS_SELECTOR, "div.feedback__date")
                        review_data["date"] = date_elem.text.strip()
                    except NoSuchElementException:
                        review_data["date"] = ""
                    
                    # Текст отзыва
                    text_parts = []
                    
                    # Плюсы
                    try:
                        pros_elem = elem.find_element(By.CSS_SELECTOR, "span.feedback__advantages")
                        review_data["pros"] = pros_elem.text.strip()
                        text_parts.append(f"Плюсы: {review_data['pros']}")
                    except NoSuchElementException:
                        review_data["pros"] = ""
                    
                    # Минусы
                    try:
                        cons_elem = elem.find_element(By.CSS_SELECTOR, "span.feedback__disadvantages")
                        review_data["cons"] = cons_elem.text.strip()
                        text_parts.append(f"Минусы: {review_data['cons']}")
                    except NoSuchElementException:
                        review_data["cons"] = ""
                    
                    # Комментарий
                    try:
                        comment_elem = elem.find_element(By.CSS_SELECTOR, "span.feedback__comment")
                        review_data["comment"] = comment_elem.text.strip()
                        text_parts.append(f"Комментарий: {review_data['comment']}")
                    except NoSuchElementException:
                        review_data["comment"] = ""
                    
                    # Общий текст
                    review_data["text"] = " | ".join(text_parts)
                    
                    if review_data["text"]:
                        reviews.append(review_data)
                    
                except Exception as e:
                    log.error(f"Ошибка парсинга отзыва: {e}")
            
        except Exception as e:
            log.error(f"Ошибка парсинга раздела отзывов: {e}")
        
        return reviews
    
    def _parse_description(self) -> str:
        """Парсит описание товара"""
        try:
            desc_elem = self.driver.find_element(By.CSS_SELECTOR, "div.product-description__text, div.description__text")
            return desc_elem.text.strip()
        except NoSuchElementException:
            return ""
    
    def _parse_characteristics(self) -> Dict[str, str]:
        """Парсит характеристики товара"""
        chars = {}
        
        try:
            char_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.characteristics__item, tr.product-params__row")
            
            for elem in char_elements[:20]:
                try:
                    key_elem = elem.find_element(By.CSS_SELECTOR, "span.characteristics__name, td:first-child")
                    value_elem = elem.find_element(By.CSS_SELECTOR, "span.characteristics__value, td:last-child")
                    
                    key = key_elem.text.strip()
                    value = value_elem.text.strip()
                    
                    if key and value:
                        chars[key] = value
                except NoSuchElementException:
                    continue
        
        except Exception as e:
            log.error(f"Ошибка парсинга характеристик: {e}")
        
        return chars
    
    def _parse_promotions(self) -> List[str]:
        """Парсит акции и спецпредложения"""
        promos = []
        
        try:
            promo_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.promo-banner, div.product-promo")
            
            for elem in promo_elements[:5]:
                try:
                    promo_text = elem.text.strip()
                    if promo_text and len(promo_text) > 10:
                        promos.append(promo_text)
                except:
                    continue
        
        except Exception as e:
            log.error(f"Ошибка парсинга акций: {e}")
        
        return promos
    
    def parse_multiple_products(self, nm_ids: List[int]) -> List[Dict]:
        """Парсит несколько товаров"""
        results = []
        
        for nm_id in nm_ids:
            result = self.parse_product_page(nm_id)
            results.append(result)
            time.sleep(5)  # Задержка между товарами
        
        return results
    
    def save_results(self, results: List[Dict]):
        """Сохраняет результаты в CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Сохраняем отзывы
        all_reviews = []
        for result in results:
            if "reviews" in result:
                for review in result["reviews"]:
                    review["nm_id"] = result["nm_id"]
                    review["timestamp"] = result["timestamp"]
                    all_reviews.append(review)
        
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            df.to_csv(self.data_dir / f"wb_reviews_{timestamp}.csv", index=False)
            df.to_csv(self.data_dir / "wb_reviews_latest.csv", index=False)
            log.info(f"Сохранено {len(all_reviews)} отзывов")
        
        # Сохраняем детали товаров
        details = []
        for result in results:
            details.append({
                "nm_id": result["nm_id"],
                "description": result.get("description", ""),
                "characteristics": json.dumps(result.get("characteristics", {}), ensure_ascii=False),
                "promotions": " | ".join(result.get("promotions", [])),
                "reviews_count": len(result.get("reviews", [])),
                "timestamp": result["timestamp"]
            })
        
        if details:
            df = pd.DataFrame(details)
            df.to_csv(self.data_dir / f"wb_details_{timestamp}.csv", index=False)
            df.to_csv(self.data_dir / "wb_details_latest.csv", index=False)
            log.info(f"Сохранено {len(details)} деталей товаров")
    
    def close(self):
        """Закрывает браузер"""
        self.driver.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
    
    # Тестовые nm_id из LOWENGRASS
    nm_ids = [330990418, 618612802]
    
    parser = WBSeleniumParser()
    try:
        results = parser.parse_multiple_products(nm_ids)
        parser.save_results(results)
        log.info("Парсинг завершён")
    finally:
        parser.close()
