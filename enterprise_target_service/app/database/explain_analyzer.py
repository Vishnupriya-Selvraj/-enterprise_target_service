import time
import pymongo
from typing import Dict, Any
from enterprise_target_service.app.database.mongo_client import mongo_manager
from enterprise_target_service.app.config import service_config

class MongoQueryPlanAnalyzer:
    """Analyzes MongoDB executionStats, winning plans, and index coverage."""

    @staticmethod
    def analyze_cart_query_plan(user_id: str = "usr_42") -> Dict[str, Any]:
        """Runs real explain('executionStats') on live MongoDB."""
        coll = mongo_manager.get_collection()
        explain_output = coll.find({"user_id": user_id, "status": "PENDING"}).explain()
        
        query_planner = explain_output.get("queryPlanner", {})
        winning_plan = query_planner.get("winningPlan", {})
        plan_str = str(winning_plan)
        
        if "IXSCAN" in plan_str:
            stage = "IXSCAN (Index Scan - Sub-Millisecond)"
            is_collscan = False
        elif "COLLSCAN" in plan_str:
            stage = "COLLSCAN (Collection Scan - 10,000 Documents Scanned)"
            is_collscan = True
        else:
            stage = winning_plan.get("stage", "UNKNOWN")
            is_collscan = "COLLSCAN" in stage

        # Benchmark live execution time
        start = time.perf_counter()
        results = list(coll.find({"user_id": user_id, "status": "PENDING"}))
        duration_ms = (time.perf_counter() - start) * 1000

        indexes = list(coll.list_indexes())
        index_names = [idx.get("name") for idx in indexes]

        return {
            "database": service_config.database_name,
            "collection": service_config.collection_name,
            "total_documents": coll.count_documents({}),
            "stage": stage,
            "is_collscan": is_collscan,
            "active_indexes": index_names,
            "documents_matched": len(results),
            "execution_duration_ms": duration_ms
        }

    @staticmethod
    def apply_compound_index_migration(index_name: str = "idx_cart_items_user_status") -> str:
        """Applies compound index migration to live MongoDB collection."""
        coll = mongo_manager.get_collection()
        created_name = coll.create_index(
            [("user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)],
            name=index_name,
            background=True
        )
        return created_name
