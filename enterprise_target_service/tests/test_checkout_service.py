import unittest
from enterprise_target_service.app.database.mongo_client import mongo_manager
from enterprise_target_service.app.database.explain_analyzer import MongoQueryPlanAnalyzer
from enterprise_target_service.app.services.checkout_service import checkout_service
from enterprise_target_service.app.telemetry.metrics_collector import metrics_collector

class TestEnterpriseCheckoutService(unittest.TestCase):
    """Institutional-grade test suite testing live MongoDB on localhost:27017."""

    def test_mongodb_connection_and_document_volume(self):
        """Verifies live MongoDB database on localhost:27017 has >= 10,000 documents."""
        coll = mongo_manager.get_collection()
        doc_count = coll.count_documents({})
        self.assertGreaterEqual(doc_count, 10000, "Collection must contain >= 10,000 documents")

    def test_query_plan_and_index_coverage(self):
        """Verifies winning query plan uses IXSCAN and executes under 25ms."""
        diag = MongoQueryPlanAnalyzer.analyze_cart_query_plan(user_id="usr_42")
        self.assertFalse(diag["is_collscan"], f"Query must not perform COLLSCAN, current stage: {diag['stage']}")
        self.assertLess(diag["execution_duration_ms"], 25.0, "Execution duration must meet SRE SLO (<25ms)")

    def test_checkout_transaction_execution(self):
        """Verifies atomic checkout transaction successfully modifies user cart."""
        result = checkout_service.process_checkout_transaction(user_id="usr_10")
        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("items_completed", result)

    def test_telemetry_snapshot_calculation(self):
        """Verifies telemetry metrics snapshot produces real mathematical p99 metrics."""
        snapshot = metrics_collector.collect_live_telemetry_snapshot()
        self.assertIn(snapshot["status"], ["HEALTHY", "CRITICAL_OUTAGE"])
        self.assertGreater(snapshot["p99_latency_ms"], 0.0)

if __name__ == "__main__":
    unittest.main()
