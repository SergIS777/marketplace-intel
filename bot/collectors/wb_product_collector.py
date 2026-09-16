"""Коллектор товаров WB через search API v18"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import time

log = logging.getLogger("intel.wb.products")

class WBProductCollector:
    def __init__(self, shop_config, data_dir: str = "/app/data"):
        self.shop = shop_config
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.wildberries.ru/",
            "Origin": "https://www.wildberries.ru"
        })
    
    def collect_products(self):
        """Собирает товары по поисковым запросам"""
        products_map = {}
        
        for query in self.shop.search_queries:
            try:
                log.info(f"Поиск: {query}")
                url = (
                    f"https://search.wb.ru/exactmatch/ru/common/v18/search"
                    f"?appType=1&curr=rub&dest=-1257786&lang=ru&page=1"
                    f"&query={query}&resultset=catalog&sort=popular&spp=100"
                )
                
                resp = self.session.get(url, timeout=15)
                
                if resp.status_code == 429:
                    log.warning("Rate limit, ждём 15 сек")
                    time.sleep(15)
                    resp = self.session.get(url, timeout=15)
                
                if resp.status_code != 200:
                    log.error(f"Статус {resp.status_code}")
                    time.sleep(5)
                    continue
                
                data = resp.json()
                
                for p in data.get("products", []):
                    if p.get("supplier", "") == self.shop.name:
                        sizes = p.get("sizes", [])
                        price_data = sizes[0].get("price", {}) if sizes else {}
                        
                        old_price = price_data.get("basic", 0) / 100
                        current_price = price_data.get("product", 0) / 100
                        discount = 0
                        if old_price > 0:
                            discount = round((1 - current_price / old_price) * 100, 1)
                        
                        products_map[p.get("id")] = {
                            "nm_id": p.get("id"),
                            "name": p.get("name", ""),
                            "brand": p.get("brand", ""),
                            "rating": p.get("rating", 0),
                            "feedbacks_count": p.get("feedbacks", 0),
                            "price_rub": current_price,
                            "old_price_rub": old_price,
                            "discount_percent": discount,
                            "timestamp": datetime.now().isoformat()
                        }
                
                found = len([p for p in data.get("products", []) if p.get("supplier") == self.shop.name])
                log.info(f"Найдено товаров: {found}")
                
                # Увеличенная задержка между запросами
                time.sleep(5)
                
            except Exception as e:
                log.error(f"Ошибка: {e}")
        
        log.info(f"Всего уникальных товаров: {len(products_map)}")
        return products_map
    
    def save(self):
        """Сохраняет результаты"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        products = self.collect_products()
        
        if products:
            df = pd.DataFrame(products.values())
            df.to_csv(self.data_dir / f"wb_products_{timestamp}.csv", index=False)
            df.to_csv(self.data_dir / "wb_products_latest.csv", index=False)
            log.info(f"Сохранено {len(products)} товаров")
