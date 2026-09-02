import time
import pymongo
from pymongo import MongoClient
from enterprise_target_service.app.config import service_config

class MongoDBConnectionManager:
    """Singleton connection manager for MongoDB with health checks and pooling."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnectionManager, cls).__new__(cls)
            cls._instance.client = MongoClient(
                service_config.mongo_uri,
                serverSelectionTimeoutMS=2500,
                maxPoolSize=50
            )
            cls._instance.db = cls._instance.client[service_config.database_name]
            cls._instance.collection = cls._instance.db[service_config.collection_name]
        return cls._instance

    def get_collection(self):
        return self.collection

    def get_database(self):
        return self.db

    def ping(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def seed_initial_dataset_if_empty(self, target_count: int = 10000):
        """Seeds 10,000 real e-commerce cart documents if collection is empty."""
        coll = self.get_collection()
        current_count = coll.count_documents({})
        if current_count < target_count:
            docs = []
            statuses = ["PENDING", "COMPLETED", "ABANDONED", "FAILED"]
            for i in range(target_count):
                docs.append({
                    "cart_id": f"cart_{i}",
                    "user_id": f"usr_{i % 500}",
                    "product_id": f"sku_{i % 50}",
                    "quantity": 1 + (i % 5),
                    "price": round(19.99 + (i % 100), 2),
                    "status": statuses[i % 4],
                    "created_at": time.time()
                })
            coll.insert_many(docs)

mongo_manager = MongoDBConnectionManager()
