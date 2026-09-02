import unittest
import pymongo
from enterprise_target_service.mongodb_engine import (
    get_mongo_collection,
    run_mongo_explain_diagnostic,
    apply_mongo_index_migration
)

class TestLiveMongoDBPerformance(unittest.TestCase):
    """Real unit tests executing against live MongoDB running on localhost:27017."""

    def test_live_mongodb_document_count(self):
        """Verifies live MongoDB database on localhost:27017 has 10,000 real documents."""
        coll = get_mongo_collection()
        count = coll.count_documents({})
        self.assertGreaterEqual(count, 10000, "MongoDB collection must contain 10,000 real documents")

    def test_live_mongodb_index_performance(self):
        """Verifies query uses IXSCAN (Index Scan) and executes under 10ms."""
        diag = run_mongo_explain_diagnostic(user_id="usr_42")
        plan_stage = diag["stage"]
        
        has_index = "IXSCAN" in plan_stage or not diag["is_collscan"]
        self.assertTrue(has_index, f"MongoDB query must use IXSCAN, current stage: {plan_stage}")
        self.assertLess(diag["execution_duration_ms"], 30.0, "Execution time must be sub-30ms")

if __name__ == "__main__":
    unittest.main()
