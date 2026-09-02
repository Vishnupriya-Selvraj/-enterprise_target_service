/**
 * checkout-api – Production‑grade NoSQL sanitisation & atomic update helper
 *
 *  • Validates all incoming payloads against a strict Joi schema
 *  • Strips any raw `$` operators or regexes that could lead to NoSQL injection
 *  • Performs an optimistic‑concurrency update using a `__v` (version) field
 *  • Wraps every MongoDB call with `maxTimeMS` / `writeConcern.wtimeout`
 *
 *  Usage:
 *      const { validateCartPayload, updateCartAtomic } = require('./dbHelpers');
 *
 *      // 1️⃣ Validate request body
 *      const { error, value } = validateCartPayload(req.body);
 *      if (error) return res.status(400).json({ error: error.message });
 *
 *      // 2️⃣ Build filter & update
 *      const filter = { _id: value.cartId, userId: value.userId, __v: value.__v };
 *      const update = {
 *          $set: { status: value.status, items: value.items },
 *          $currentDate: { lastModified: true },
 *          $inc: { __v: 1 }          // optimistic‑concurrency bump
 *      };
 *
 *      // 3️⃣ Execute atomic update
 *      const result = await updateCartAtomic(db.collection('carts'), filter, update);
 *      if (!result) return res.status(409).json({ error: 'Cart was modified by another process' });
 *
 *      return res.json({ success: true, cart: result.value });
 */

const Joi = require('joi');
const { ObjectId } = require('mongodb');

/**
 * 1️⃣  Payload validation – no raw `$` operators, strict types
 */
const cartSchema = Joi.object({
  userId: Joi.string()
    .length(24)
    .hex()
    .required()
    .description('MongoDB ObjectId of the user'),

  cartId: Joi.string()
    .length(24)
    .hex()
    .required()
    .description('MongoDB ObjectId of the cart'),

  __v: Joi.number()
    .integer()
    .min(0)
    .required()
    .description('Optimistic‑concurrency version'),

  status: Joi.string()
    .valid('OPEN', 'RESERVED', 'COMPLETED')
    .required(),

  items: Joi.array()
    .items(
      Joi.object({
        productId: Joi.string()
          .length(24)
          .hex()
          .required(),
        quantity: Joi.number()
          .integer()
          .min(1)
          .required()
      })
    )
    .min(1)
    .required()
});

/**
 * Validate request body against the schema
 * @param {Object} payload
 * @returns {Object} { error, value }
 */
function validateCartPayload(payload) {
  // Reject any keys that start with `$` or contain regex patterns
  const sanitized = sanitizePayload(payload);
  return cartSchema.validate(sanitized, { abortEarly: false });
}

/**
 * 2️⃣  Sanitisation – strip any `$` keys or regexes that could be used for injection
 * @param {Object} obj
 * @returns {Object}
 */
function sanitizePayload(obj) {
  if (Array.isArray(obj)) {
    return obj.map(sanitizePayload);
  }
  if (obj && typeof obj === 'object') {
    const cleaned = {};
    for (const [k, v] of Object.entries(obj)) {
      if (k.startsWith('$')) continue;          // drop any $‑prefixed key
      if (typeof v === 'object' && v !== null && '$regex' in v) continue; // drop regex
      cleaned[k] = sanitizePayload(v);
    }
    return cleaned;
  }
  return obj;
}

/**
 * 3️⃣  Atomic update helper – optimistic‑concurrency + NOWAIT safeguards
 * @param {Collection} coll – MongoDB collection
 * @param {Object} filter – query filter (must include __v for OCC)
 * @param {Object} update – MongoDB update document
 * @param {Object} [options] – optional overrides
 * @returns {Promise<Object|null>} – updated document or null if version mismatch
 */
async function updateCartAtomic(coll, filter, update, options = {}) {
  const defaultOpts = {
    // 50 ms read timeout, 100 ms write timeout
    maxTimeMS: 50,
    writeConcern: { w: 'majority', wtimeout: 100 },
    returnDocument: 'after', // return the updated doc
    // Ensure we only succeed if the version matches
    // (filter already contains __v)
  };

  const mergedOpts = { ...defaultOpts, ...options };

  const result = await coll.findOneAndUpdate(filter, update, mergedOpts);

  // If no document was returned, the version was stale (optimistic‑concurrency failure)
  return result.value || null;
}

/**
 * 4️⃣  Example of a lock‑guarded operation (try‑lock pattern)
 *      (Assumes a Redis‑based lock library like `redlock` is available)
 */
const Redlock = require('redlock');
const redis = require('redis');
const redisClient = redis.createClient();
const redlock = new Redlock([redisClient], {
  retryCount: 0, // no retry – fail‑fast
  retryDelay: 200 // ms
});

/**
 * Acquire a lock for a cart, perform an atomic update, then release
 * @param {ObjectId|string} cartId
 * @param {Object} updateDoc
 * @returns {Promise<Object|null>}
 */
async function updateCartWithLock(cartId, updateDoc) {
  const resource = `locks:cart:${cartId}`;
  const ttl = 200; // 200 ms TTL

  let lock;
  try {
    lock = await redlock.acquire([resource], ttl);
  } catch (e) {
    // Lock acquisition failed – return 429‑style error
    throw new Error('Too many concurrent updates – try again later');
  }

  try {
    const filter = { _id: new ObjectId(cartId) };
    return await updateCartAtomic(coll, filter, updateDoc);
  } finally {
    // Always release the lock
    await lock.release().catch(() => { /* ignore */ });
  }
}

module.exports = {
  validateCartPayload,
  sanitizePayload,
  updateCartAtomic,
  updateCartWithLock
};