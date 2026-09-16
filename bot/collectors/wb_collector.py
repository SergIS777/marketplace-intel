import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import time
from typing import List, Dict

log = logging.getLogger("intel.wb")

class WBCollector:
    """Публичный коллектор Wildberries через search API v18
    Стратегия: поиск по ключевым словам + фильтр по supplier='LOWENGRASS'
    """
    
    SEARCH_QUERIES = [
        "Пароочиститель LOWENGRASS",
        "Аэрогриль LOWENGRASS", 
        "Паровая швабра LOWENGRASS",
        "LOWENGRASS Steam Max",
        "LOWENGRASS Steam Pro"
    ]
    TARGET_SUPPLIER = "LOWENGRASS"
    
    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9",
            "Referer": "https://www.wildberries.ru/",
            "Origin": "https://www.wildberries.ru"
        })
    
    def _request_with_retry(self, url: str, retries: int = 3) -> requests.Response:
        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=15)
                if resp.status_code == 429:
                    log.warning(f"Rate limit, ждём 10 сек (attempt {attempt+1}/{retries})")
                    time.sleep(10)
                    continue
                return resp
            except Exception as e:
                log.error(f"Request error: {e}")
                time.sleep(2)
        return None
    
    def collect_products(self) -> Dict[int, Dict]:
        """Собрать все товары LOWENGRASS через поиск по ключевым словам"""
        products_map = {}  # nm_id -> product (для дедупликации)
        
        for query in self.SEARCH_QUERIES:
            try:
                log.info(f"Поиск: {query}")
                url = (
                    f"https://search.wb.ru/exactmatch/ru/common/v18/search"
                    f"?appType=1&curr=rub&dest=-1257786&lang=ru&page=1"
                    f"&query={query}&resultset=catalog&sort=popular&spp=100"
                )
                
                resp = self._request_with_retry(url)
                if not resp or resp.status_code != 200:
                    log.error(f"Сбой для запроса {query}: status={resp.status_code if resp else 'None'}")
                    continue
                
                data = resp.json()
                for p in data.get("products", []):
                    supplier = p.get("supplier", "")
                    if supplier == self.TARGET_SUPPLIER:
                        sizes = p.get("sizes", [])
                        price_data = sizes[0].get("price", {}) if sizes else {}
                        products_map[p.get("id")] = {
                            "nm_id": p.get("id"),
                            "name": p.get("name", ""),
                            "brand": p.get("brand", ""),
                            "supplier": supplier,
                            "rating": p.get("rating", 0),
                            "feedbacks_count": p.get("feedbacks", 0),
                            "price_rub": price_data.get("product", 0) / 100,
                            "old_price_rub": price_data.get("basic", 0) / 100,
                            "timestamp": datetime.now().isoformat()
                        }
                
                log.info(f"Найдено товаров LOWENGRASS по запросу: {len([p for p in data.get('products', []) if p.get('supplier') == self.TARGET_SUPPLIER])}")
                time.sleep(2)
                
            except Exception as e:
                log.error(f"Ошибка при запросе {query}: {e}")
        
        log.info(f"ИТОГО собрано уникальных товаров LOWENGRASS: {len(products_map)}")
        return products_map
    
    def collect_reviews(self, nm_ids: List[int], limit: int = 50) -> List[Dict]:
        """Собрать отзывы через feedbacks API (пробуем шарды 1-16)"""
        all_reviews = []
        
        for nm_id in nm_ids:
            for shard in range(1, 17):
                try:
                    url = f"https://feedbacks{shard}.wb.ru/feedbacks/v1/{nm_id}"
                    resp = self._request_with_retry(url, retries=1)
                    if not resp or resp.status_code != 200:
                        continue
                    
                    data = resp.json()
                    feedbacks = data.get("feedbacks")
                    if feedbacks:  # Не пустой массив
                        for fb in feedbacks[:limit]:
                            all_reviews.append({
                                "nm_id": nm_id,
                                "feedback_id": fb.get("id"),
                                "rating": fb.get("productValuation"),
                                "text": fb.get("text", ""),
                                "created_at": fb.get("createdDate"),
                                "username": fb.get("userName"),
                                "shard": shard,
                                "timestamp": datetime.now().isoformat()
                            })
                        log.info(f"nm_id {nm_id}: шард {shard}, {len(feedbacks[:limit])} отзывов")
                        break
                    else:
                        log.info(f"nm_id {nm_id}: шард {shard} — feedbacks=null (не тот шард)")
                    
                    time.sleep(0.3)
                except Exception as e:
                    log.error(f"Отзывы nm_id {nm_id}, шард {shard}: {e}")
        
        log.info(f"ИТОГО собрано отзывов: {len(all_reviews)}")
        return all_reviews
    
    def collect_all(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Товары
        products_map = self.collect_products()
        if products_map:
            df = pd.DataFrame(products_map.values())
            df.to_csv(self.data_dir / f"wb_products_{timestamp}.csv", index=False)
            log.info(f"wb_products_{timestamp}.csv: {len(products_map)} товаров")
            
            # Отзывы
            nm_ids = list(products_map.keys())
            reviews = self.collect_reviews(nm_ids)
            if reviews:
                df = pd.DataFrame(reviews)
                df.to_csv(self.data_dir / f"wb_reviews_{timestamp}.csv", index=False)
                log.info(f"wb_reviews_{timestamp}.csv: {len(reviews)} отзывов")
        
        self._cleanup_old_snapshots(days=30)
    
    def _cleanup_old_snapshots(self, days: int = 30):
        cutoff = datetime.now().timestamp() - days * 86400
        removed = 0
        for f in self.data_dir.glob("wb_*.csv"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        if removed:
            log.info(f"Удалено {removed} старых снапшотов")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    collector = WBCollector()
    collector.collect_all()
    log.info("Коллекция WB завершена")
