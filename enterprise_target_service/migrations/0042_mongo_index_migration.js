/**
 * Verification Script for SRE-RB-409 Pre-Check
 * Purpose: Confirm index existence and query plan usage before any remediation.
 * Action: READ-ONLY. Does not modify database state.
 */

const db = require('mongodb').Db; // Assume connection is established in context

async function verifyCartItemsIndexAndPlan() {
    const collection = db.collection('cart_items');
    const indexName = 'idx_cart_items_user_status';
    const expectedFields = { user_id: 1, status: 1 };

    try {
        // Step 1: Verify Index Existence
        const indexes = await collection.getIndexes();
        const targetIndex = indexes.find(idx => idx.name === indexName);

        if (!targetIndex) {
            console.error(`CRITICAL: Index '${indexName}' not found. Remediation may be required.`);
            return { status: 'INDEX_MISSING', details: 'Index not found in collection.' };
        }

        // Verify index fields match expected
        const indexKeys = targetIndex.key;
        const keysMatch = 
            indexKeys.user_id === expectedFields.user_id &&
            indexKeys.status === expectedFields.status;

        if (!keysMatch) {
            console.error(`WARNING: Index '${indexName}' exists but has unexpected keys: ${JSON.stringify(indexKeys)}`);
            return { status: 'INDEX_MISMATCH', details: `Expected ${JSON.stringify(expectedFields)}, got ${JSON.stringify(indexKeys)}` };
        }

        console.log(`INFO: Index '${indexName}' exists with correct keys.`);

        // Step 2: Verify Query Plan (IXSCAN)
        const query = { user_id: "test_user", status: "active" };
        const explainResult = await collection.find(query).explain("executionStats");

        const winningPlan = explainResult.queryPlanner.winningPlan;
        const stage = winningPlan.stage;

        if (stage !== 'IXSCAN') {
            console.error(`CRITICAL: Query plan is using '${stage}' instead of 'IXSCAN'. Potential performance issue.`);
            return { status: 'PLAN_NOT_OPTIMAL', details: `Stage: ${stage}` };
        }

        console.log(`INFO: Query plan is using 'IXSCAN' as expected.`);
        console.log(`INFO: Execution time: ${explainResult.executionStats.executionTimeMillis}ms`);

        return { status: 'HEALTHY', details: 'Index exists and is being used via IXSCAN.' };

    } catch (error) {
        console.error(`ERROR: Verification failed: ${error.message}`);
        return { status: 'ERROR', details: error.message };
    }
}

module.exports = { verifyCartItemsIndexAndPlan };