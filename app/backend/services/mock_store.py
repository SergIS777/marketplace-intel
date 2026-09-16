rom typing import List, Dict, Optional

class MockStoreService:
    def __init__(self):
        self.stores = {
            "store_1": {
                "id": "store_1",
                "name": "LOWENGRASS",
                "owner_id": "user_123",
                "created_at": "2026-01-15T10:00:00Z",
                "stats": {"total_products": 4, "total_sales": 156, "revenue": 2450000, "avg_rating": 4.7}
            }
        }
        self.products = {
            "store_1": [
                {"nm_id": 330990418, "name": "Кресло офисное LOWENGRASS Premium", "price": 15990, "stock": 47, "sales_last_30d": 23, "rating": 4.8, "reviews_count": 156},
                {"nm_id": 618612802, "name": "Стол письменный DORFHAUS", "price": 24990, "stock": 23, "sales_last_30d": 12, "rating": 4.6, "reviews_count": 89},
                {"nm_id": 912617526, "name": "Стул обеденный SCANDI", "price": 8990, "stock": 112, "sales_last_30d": 45, "rating": 4.9, "reviews_count": 234},
                {"nm_id": 913015022, "name": "Комод CLASSIC 4 ящика", "price": 12490, "stock": 67, "sales_last_30d": 18, "rating": 4.5, "reviews_count": 72}
            ]
        }
        self.reviews = {
            "store_1": [
                {"id": "rev_001", "nm_id": 330990418, "rating": 5, "text": "Отличное кресло! Качество на высоте.", "author": "Анна К.", "date": "2026-09-15T14:30:00Z", "answered": False},
                {"id": "rev_002", "nm_id": 618612802, "rating": 4, "text": "Стол хороший, но доставка долгая.", "author": "Михаил П.", "date": "2026-09-14T09:15:00Z", "answered": False},
                {"id": "rev_003", "nm_id": 912617526, "rating": 5, "text": "Идеальный стул!", "author": "Елена С.", "date": "2026-09-13T16:45:00Z", "answered": True, "answer": "Спасибо!"}
            ]
        }
    
    def get_store(self, store_id: str) -> Optional[Dict]:
        return self.stores.get(store_id)
    
    def get_products(self, store_id: str) -> List[Dict]:
        return self.products.get(store_id, [])
    
    def get_reviews(self, store_id: str, unanswered_only: bool = False) -> List[Dict]:
        reviews = self.reviews.get(store_id, [])
        if unanswered_only:
            return [r for r in reviews if not r.get("answered")]
        return reviews

mock_store_service = MockStoreService()
