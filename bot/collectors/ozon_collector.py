import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import time
from typing import List, Dict

log = logging.getLogger("intel.ozon")

class OzonCollector:
    """Публичный коллектор Ozon через seller API (открытые данные)"""
    
    # Реальные товары LOWENGRASS на Ozon (из скриншотов)
    LOWENGRASS_PRODUCTS = [
        {"sku": "5557488274", "name": "Аэрогриль 15л"},
        {"sku": "391382765", "name": "Аэрогриль 10л"},
        {"sku": "618612802", "name": "Пароочиститель Steam Max"},
        {"sku": "330990418", "name": "Пароочиститель STEAM PRO"},
    ]
    
    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Origin": "https://www.ozon.ru",
            "Referer": "https://www.ozon.ru/"
        })
    
    def collect_product_page(self, sku: str) -> Dict:
        """Ozon отдаёт данные через внутренний API на странице товара"""
        try:
            url = f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=%2Fproduct%2F{sku}%2F"
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code != 200:
                log.warning(f"SKU {sku}: status {resp.status_code}")
                return {}
            
            data = resp.json()
            # Ozon возвращает сложную структуру — извлекаем нужное
            # (конкретный путь к данным зависит от текущей версии API)
            
            # Базовое извлечение (может потребоваться адаптация)
            layout = data.get("layoutTrackingInfo", {}) or {}
            widgetStates = data.get("widgetStates", {})
            
            # Ищем данные о товаре в структуре ответа
            product_info = {
                "sku": sku,
                "timestamp": datetime.now().isoformat()
            }
            
            # Парсим widgetStates для цены и рейтинга
            for key, value in widgetStates.items():
                try:
                    import json
                    widget_data = json.loads(value) if isinstance(value, str) else value
                    # Ищем разные типы виджетов
                    if isinstance(widget_data, dict):
                        # Цена
                        if "webPrice" in str(widget_data)[:200]:
                            product_info["price_data"] = widget_data
                        # Рейтинг и отзывы
                        if "webReviewProductScore" in str(widget_data)[:200]:
                            product_info["review_data"] = widget_data
                except:
                    pass
            
            return product_info
            
        except Exception as e:
            log.error(f"Ошибка для SKU {sku}: {e}")
            return {}
    
    def collect_all(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        results = []
        
        for product in self.LOWENGRASS_PRODUCTS:
            sku = product["sku"]
            log.info(f"Собираю Ozon SKU {sku} ({product['name']})")
            
            data = self.collect_product_page(sku)
            if data:
                results.append({
                    "sku": sku,
                    "name": product["name"],
                    "raw_data": str(data)[:500],
                    "timestamp": datetime.now().isoformat()
                })
            
            time.sleep(2)
        
        if results:
            df = pd.DataFrame(results)
            df.to_csv(self.data_dir / f"ozon_products_{timestamp}.csv", index=False)
            log.info(f"ozon_products_{timestamp}.csv: {len(results)} товаров")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    collector = OzonCollector()
    collector.collect_all()
