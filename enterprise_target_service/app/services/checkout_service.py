import time
from typing import Dict, Any
from enterprise_target_service.app.database.mongo_client import mongo_manager

class CheckoutDomainService:
    """Core domain service executing cart transactions against live MongoDB."""

    def __init__(self):
        self.coll = mongo_manager.get_collection()

    def get_user_pending_cart(self, user_id: str) -> Dict[str, Any]:
        """Queries pending cart items for a user."""
        start = time.perf_counter()
        items = list(self.coll.find({"user_id": user_id, "status": "PENDING"}))
        duration_ms = (time.perf_counter() - start) * 1000
        return {
            "user_id": user_id,
            "items_count": len(items),
            "items": items,
            "query_duration_ms": duration_ms
        }

    def process_checkout_transaction(self, user_id: str) -> Dict[str, Any]:
        """Atomically transitions user cart from PENDING to COMPLETED."""
        start = time.perf_counter()
        result = self.coll.update_many(
            {"user_id": user_id, "status": "PENDING"},
            {"$set": {"status": "COMPLETED", "updated_at": time.time()}}
        )
        duration_ms = (time.perf_counter() - start) * 1000
        return {
            "user_id": user_id,
            "items_completed": result.modified_count,
            "transaction_duration_ms": duration_ms,
            "status": "SUCCESS"
        }

checkout_service = CheckoutDomainService()
