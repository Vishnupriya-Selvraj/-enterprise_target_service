/**
 * mongoClientFactory.js
 *
 * Production‑grade MongoDB client factory.
 *
 * • Enforces SOP‑recommended pool sizing (maxPoolSize, minPoolSize, maxIdleTimeMS, waitQueueTimeoutMS).  
 * • Reads configuration from environment variables – makes the values explicit in the container image.  
 * • Guarantees a **single** MongoClient instance per process (idempotent `getClient()` call).  
 * • Exposes the underlying `db` handle for convenience (`getDb()`).
 *
 * Usage (Node):
 *   const { getDb } = require('./mongoClientFactory');
 *   const db = await getDb();   // resolves to the `ecommerce_prod` database
 *
 *   // Example query:
 *   const cartItems = await db.collection('cart_items')
 *                              .find({ user_id: userId, status: 'ACTIVE' })
 *                              .toArray();
 */

const { MongoClient } = require('mongodb');

// ---------------------------------------------------------------------------
// 1️⃣  Default SOP‑recommended values (can be overridden via env‑vars)
// ---------------------------------------------------------------------------
const DEFAULTS = {
  // Connection string – keep it simple for a localhost dev / prod deployment.
  // In production you will replace `localhost` with the proper replica‑set URI.
  MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/ecommerce_prod',

  // Pool sizing – 5× expected concurrent DB calls (≈ 100 for our traffic peak).
  MAX_POOL_SIZE: parseInt(process.env.MONGODB_MAX_POOL_SIZE, 10) || 100,
  MIN_POOL_SIZE: parseInt(process.env.MONGODB_MIN_POOL_SIZE, 10) || 20,

  // Connections idle > 30 s are closed – frees sockets for scaling pods.
  MAX_IDLE_TIME_MS: parseInt(process.env.MONGODB_MAX_IDLE_TIME_MS, 10) || 30_000,

  // How long a driver thread may wait for a free connection before erroring.
  WAIT_QUEUE_TIMEOUT_MS: parseInt(process.env.MONGODB_WAIT_QUEUE_TIMEOUT_MS, 10) || 5_000,

  // Optional TLS / auth – forward‑compatible.
  MONGODB_TLS: process.env.MONGODB_TLS === 'true',
  MONGODB_USER: process.env.MONGODB_USER || '',
  MONGODB_PASSWORD: process.env.MONGODB_PASSWORD || '',
};

let _client = null; // singleton

/**
 * Build the final MongoDB URI, injecting auth & TLS if supplied.
 */
function buildUri() {
  const {
    MONGODB_URI,
    MONGODB_USER,
    MONGODB_PASSWORD,
    MONGODB_TLS,
  } = DEFAULTS;

  // If auth is required, inject it into the URI (MongoDB driver will URL‑encode).
  if (MONGODB_USER && MONGODB_PASSWORD) {
    const authPart = `${encodeURIComponent(MONGODB_USER)}:${encodeURIComponent(MONGODB_PASSWORD)}@`;
    return MONGODB_URI.replace('mongodb://', `mongodb://${authPart}`);
  }

  // Append TLS flag if needed.
  if (MONGODB_TLS) {
    return `${MONGODB_URI}?tls=true`;
  }

  return MONGODB_URI;
}

/**
 * Returns a *connected* MongoClient instance.
 * The first call creates the client; subsequent calls return the same instance.
 *
 * @returns {Promise<MongoClient>}
 */
async function getClient() {
  if (_client && _client.isConnected && _client.isConnected()) {
    return _client;
  }

  const uri = buildUri();

  const clientOptions = {
    // Core pool settings
    maxPoolSize: DEFAULTS.MAX_POOL_SIZE,
    minPoolSize: DEFAULTS.MIN_POOL_SIZE,
    maxIdleTimeMS: DEFAULTS.MAX_IDLE_TIME_MS,
    waitQueueTimeoutMS: DEFAULTS.WAIT_QUEUE_TIMEOUT_MS,

    // Enable the new Server Discovery and Monitoring engine (default in 4.4+)
    useUnifiedTopology: true,

    // Optional TLS – only set when env‑var is true.
    tls: DEFAULTS.MONGODB_TLS,
  };

  // Create & connect
  const client = new MongoClient(uri, clientOptions);
  await client.connect();

  // Store singleton
  _client = client;
  console.info('[MongoClientFactory] Connected – pool size:', clientOptions.maxPoolSize);
  return _client;
}

/**
 * Convenience helper – returns the `ecommerce_prod` DB handle.
 *
 * @returns {Promise<Db>}
 */
async function getDb() {
  const client = await getClient();
  // The database name is part of the connection string; fallback to explicit name.
  const dbName = client.s.options?.dbName || 'ecommerce_prod';
  return client.db(dbName);
}

/**
 * Graceful shutdown – call from SIGTERM / process exit handlers.
 */
async function closeClient() {
  if (_client && _client.isConnected && _client.isConnected()) {
    await _client.close();
    console.info('[MongoClientFactory] Connection closed.');
    _client = null;
  }
}

// Export only the public API – keep the singleton hidden.
module.exports = {
  getClient,
  getDb,
  closeClient,
};