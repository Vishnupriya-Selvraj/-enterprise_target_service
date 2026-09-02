from enterprise_target_service.app.database.mongo_client import mongo_manager
from enterprise_target_service.app.telemetry.metrics_collector import metrics_collector
from enterprise_target_service.app.services.checkout_service import checkout_service
from enterprise_target_service.app.config import service_config

# Ensure MongoDB database is initialized with 10,000 real documents
try:
    mongo_manager.seed_initial_dataset_if_empty(10000)
except Exception as e:
    print(f"Target service MongoDB initialization notice: {e}")

class ECommerceApplication:
    """Enterprise checkout application instance."""
    
    def __init__(self):
        self.config = service_config
        self.metrics = metrics_collector
        self.checkout = checkout_service

    def health_check(self):
        is_alive = mongo_manager.ping()
        return {
            "service": self.config.service_name,
            "version": self.config.service_version,
            "status": "UP" if is_alive else "DOWN",
            "database_connected": is_alive
        }

    def get_metrics(self):
        return self.metrics.collect_live_telemetry_snapshot()

    def process_checkout(self, user_id: str):
        return self.checkout.process_checkout_transaction(user_id)

app_instance = ECommerceApplication()
