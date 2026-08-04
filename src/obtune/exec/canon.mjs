// Canonical output serialization — JavaScript side.
// Mirrors src/obtune/exec/canon.py exactly; tests/test_canon_parity.py runs a shared
// fixture list through both and requires byte-identical strings. See canon.py for the spec.

export class Unserializable extends Error {}

function fmtNumber(x) {
  if (!Number.isFinite(x)) throw new Unserializable(`non-finite number: ${x}`);
  if (x === 0) return '0'; // also normalizes -0
  // Integral values print as plain decimals, matching canon.py's collapse of
  // integral floats. Non-integral values use JS shortest round-trip, which agrees
  // with Python repr() (both are shortest-roundtrip shortest-representation), with
  // exponent zero-padding already absent on this side.
  return String(x);
}

function escapeStr(s) {
  let out = '"';
  for (const ch of s) {
    const o = ch.codePointAt(0);
    if (ch === '"') out += '\\"';
    else if (ch === '\\') out += '\\\\';
    else if (ch === '\n') out += '\\n';
    else if (ch === '\r') out += '\\r';
    else if (ch === '\t') out += '\\t';
    else if (o < 0x20) out += '\\u' + o.toString(16).padStart(4, '0');
    else out += ch;
  }
  return out + '"';
}

export function canon(value, depth = 0) {
  if (depth > 40) throw new Unserializable('value nested too deeply (possible cycle)');
  if (value === null) return 'null';
  if (value === undefined) throw new Unserializable('undefined in output position');
  const t = typeof value;
  if (t === 'boolean') return value ? 'true' : 'false';
  if (t === 'number') return fmtNumber(value);
  if (t === 'bigint') return value.toString();
  if (t === 'string') return escapeStr(value);
  if (t === 'function' || t === 'symbol') throw new Unserializable(`unsupported type: ${t}`);
  if (Array.isArray(value)) return '[' + value.map((v) => canon(v, depth + 1)).join(',') + ']';
  const tag = Object.prototype.toString.call(value);
  if (tag === '[object Set]') throw new Unserializable('Set in output position: order not stable');
  if (tag === '[object Map]') {
    const entries = [...Map.prototype.entries.call(value)].map(([k, v]) => [keyOf(k), v]);
    entries.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
    return '{' + entries.map(([k, v]) => `${escapeStr(k)}:${canon(v, depth + 1)}`).join(',') + '}';
  }
  if (t === 'object') {
    // Compare by constructor NAME, not identity: objects created inside a vm context
    // have that context's intrinsics, so `value.constructor !== Object` is true for
    // ordinary object literals produced by the program under test.
    const ctorName = value.constructor ? value.constructor.name : null;
    if (ctorName !== null && ctorName !== 'Object') {
      throw new Unserializable(`unsupported object type: ${ctorName}`);
    }
    const entries = Object.entries(value).map(([k, v]) => [k, v]);
    entries.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
    return '{' + entries.map(([k, v]) => `${escapeStr(k)}:${canon(v, depth + 1)}`).join(',') + '}';
  }
  throw new Unserializable(`unsupported type: ${t}`);
}

function keyOf(k) {
  if (typeof k === 'string') return k;
  if (typeof k === 'boolean') return k ? 'true' : 'false';
  if (typeof k === 'number' && Number.isInteger(k)) return String(k);
  throw new Unserializable(`unsupported map key type: ${typeof k}`);
}

export function canonOrNull(value) {
  try {
    return canon(value);
  } catch (e) {
    if (e instanceof Unserializable) return null;
    throw e;
  }
}
