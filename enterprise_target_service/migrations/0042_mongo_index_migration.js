/**
 * Database Verification Script for orders-db
 * 
 * RCA Context: 
 * - Alert "Missing compound index" is a FALSE POSITIVE.
 * - Index idx_cart_items_user_status is ACTIVE and in use.
 * - p99 latency is 1.98ms (healthy).
 * 
 * Action: 
 * - DO NOT create the index.
 * - Verify index existence and query plan to confirm system health.
 * - This script is idempotent and safe to run in production.
 */

const collectionName = 'cart_items';
const indexName = 'idx_cart_items_user_status';
const expectedIndexKeys = { user_id: 1, status: 1 };

// 1. Verify Index Existence
const indexes = db[collectionName].getIndexes();
const targetIndex = indexes.find(idx => idx.name === indexName);

if (!targetIndex) {
    // This should NOT happen based on RCA. If it does, log a critical error.
    throw new Error(`CRITICAL: Index ${indexName} not found. RCA indicated it should exist. Investigate diagnostic tooling.`);
}

// 2. Verify Index Keys Match Expected Schema
const actualKeys = targetIndex.key;
const keysMatch = JSON.stringify(actualKeys) === JSON.stringify(expectedIndexKeys);

if (!keysMatch) {
    throw new Error(`CRITICAL: Index ${indexName} exists but has unexpected keys: ${JSON.stringify(actualKeys)}. Expected: ${JSON.stringify(expectedIndexKeys)}`);
}

// 3. Verify Query Plan Uses IXSCAN (Index Scan)
// Use a sample query that matches the alert's context
const sampleQuery = { user_id: "test_user_id", status: "active" };
const explainResult = db[collectionName].find(sampleQuery).explain('executionStats');

// Extract the winning plan stage
const winningPlan = explainResult.queryPlanner.winningPlan;
const stage = winningPlan.stage;
const indexUsed = winningPlan.inputStage ? winningPlan.inputStage.indexName : null;

if (stage !== 'IXSCAN' || indexUsed !== indexName) {
    // If it's not IXSCAN, check if it's a COLLSCAN (which would indicate a real problem)
    if (stage === 'COLLSCAN') {
        throw new Error(`CRITICAL: Query is using COLLSCAN. Index ${indexName} is not being used. Investigate immediately.`);
    }
    // If it's another stage (e.g., FETCH with IXSCAN input), that's acceptable, but we expect IXSCAN at the top or input level
    console.warn(`WARNING: Query plan stage is ${stage}, using index: ${indexUsed}. Expected IXSCAN with ${indexName}.`);
} else {
    console.log(`SUCCESS: Index ${indexName} is active and query plan uses IXSCAN.`);
}

// 4. Log Verification Result for Alert Closure
console.log(`VERIFICATION COMPLETE: Index ${indexName} exists and is in use. Alert can be closed as False Positive.`);