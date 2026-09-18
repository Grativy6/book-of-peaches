"""Canonical PEACHES envelopes and trust-aware verification."""
from __future__ import annotations
import base64, hashlib, json, math
from datetime import datetime, timezone
from typing import Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

MAX_BYTES, MAX_DEPTH, MAX_ITEMS = 100_000, 32, 10_000
SAFE_MAX = 2**53 - 1
class PeachesError(ValueError): pass

def _reject(v: Any, depth=0) -> Any:
    if depth > MAX_DEPTH: raise PeachesError("maximum JSON depth exceeded")
    if isinstance(v, bool) or v is None or isinstance(v, str): return v
    if isinstance(v, float):
        if not math.isfinite(v): raise PeachesError("non-finite number")
        raise PeachesError("floats are not canonical; use a decimal string")
    if isinstance(v, int):
        if abs(v) > SAFE_MAX: raise PeachesError("integer exceeds safe range; use a decimal string")
        return v
    if isinstance(v, bytes): raise PeachesError("bytes must be base64 strings")
    if isinstance(v, dict):
        if len(v) > MAX_ITEMS or any(not isinstance(k, str) for k in v): raise PeachesError("invalid object")
        return {k: _reject(v[k], depth + 1) for k in sorted(v)}
    if isinstance(v, list):
        if len(v) > MAX_ITEMS: raise PeachesError("too many array items")
        return [_reject(x, depth + 1) for x in v]
    raise PeachesError(f"unsupported value {type(v).__name__}")

def canonical_bytes(value: Any) -> bytes:
    data = json.dumps(_reject(value), ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(data) > MAX_BYTES: raise PeachesError("canonical payload exceeds 100000 bytes")
    return data
def digest(value: Any) -> str: return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()
def b64(data: bytes) -> str: return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")
def unb64(value: str) -> bytes:
    if not isinstance(value, str): raise PeachesError("expected base64 string")
    try: return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as e: raise PeachesError("invalid base64") from e

def prepare_registration(payload: dict, context: dict | None = None) -> dict:
    if not isinstance(payload, dict): raise PeachesError("payload must be an object")
    required = {"book_id", "profile_id", "object", "request_id", "observed_at", "issuer_id"}
    missing = required - payload.keys()
    if missing: raise PeachesError("missing fields: " + ",".join(sorted(missing)))
    if not str(payload["book_id"]).startswith("test:") or not str(payload["issuer_id"]).startswith("test:"):
        raise PeachesError("test namespace required")
    try:
        stamp_time=datetime.fromisoformat(str(payload["observed_at"]).replace("Z","+00:00"))
        if stamp_time.tzinfo is None: raise ValueError
    except Exception as e: raise PeachesError("observed_at must be an ISO-8601 aware timestamp") from e
    if context and "checker_registered_at" in context:
        try:
            registered=datetime.fromisoformat(str(context["checker_registered_at"]).replace("Z","+00:00"))
            if registered.tzinfo is None: raise ValueError
        except Exception as e: raise PeachesError("checker_registered_at must be an ISO-8601 aware timestamp") from e
    obj = payload["object"]
    request_intent = {"request_id":payload["request_id"], "profile_id":payload["profile_id"], "observed_at":payload["observed_at"], "issuer_id":payload["issuer_id"], "object_id":digest(obj)}
    envelope = {"schema":"peaches.registration/0.2", "book_id":payload["book_id"], "profile_id":payload["profile_id"],
      "object_id":digest(obj), "object":obj, "request_id":payload["request_id"],
      "request_intent_hash":digest(request_intent), "observed_at":payload["observed_at"],
      "issuer_id":payload["issuer_id"], "claim_ceiling":"registration_event_only"}
    if "institution_stamp" in payload: envelope["institution_stamp"] = payload["institution_stamp"]
    if context:
        for key in ("sequence", "previous_head", "checker_id", "checker_registered_at", "profile_transition"):
            if key in context: envelope[key] = context[key]
    envelope["registration_id"] = digest(envelope)
    return envelope

def _signed_content(bundle): return {k: bundle[k] for k in bundle if k != "signature"}
def sign_registration(envelope, private_key, key_id):
    out = dict(envelope)
    out["signature"] = {"algorithm":"Ed25519", "key_id":key_id, "value":b64(private_key.sign(canonical_bytes(_signed_content(out))))}
    return out

def verify_bundle(bundle: dict, context: dict | None = None) -> dict:
    errors=[]
    try:
        fields={k:bundle[k] for k in ("sequence","previous_head","checker_id","checker_registered_at","profile_transition") if k in bundle}
        env = prepare_registration(bundle, fields)
        if bundle.get("registration_id") != env["registration_id"]: errors.append("registration_id_mismatch")
        if bundle.get("object_id") != env["object_id"]: errors.append("object_id_mismatch")
        sig=bundle.get("signature")
        if not sig: errors.append("missing_signature")
        elif sig.get("algorithm") != "Ed25519": errors.append("unsupported_signature_algorithm")
        else:
            key_id=sig.get("key_id","")
            if not key_id.startswith("test:"): errors.append("untrusted_key_namespace")
            else:
                Ed25519PublicKey.from_public_bytes(unb64(key_id[5:])).verify(unb64(sig["value"]), canonical_bytes(_signed_content(bundle)))
                if context is None:
                    if not errors: return {"status":"SIGNATURE_VALID_UNANCHORED","errors":[],"claim":"signature_only"}
                else:
                    if context.get("book_id") != bundle.get("book_id") or context.get("profile_id") != bundle.get("profile_id"): errors.append("book_or_profile_mismatch")
                    if context.get("checker_id") != key_id: errors.append("checker_role_mismatch")
                    if context.get("sequence") != bundle.get("sequence") or context.get("previous_head") != bundle.get("previous_head"): errors.append("chain_position_mismatch")
                    if context.get("inclusion") != bundle.get("registration_id"): errors.append("missing_inclusion")
    except Exception as e: errors.append(type(e).__name__ if not isinstance(e, PeachesError) else str(e))
    if errors: return {"status":"INVALID_REGISTRATION","errors":errors,"claim":"no_registration_claim"}
    if context is not None: return {"status":"VALID_UNDER_DECLARED_CONTEXT","errors":[],"trust":"caller_supplied_context_not_a_book_receipt","claim":"conditional_only"}
    return {"status":"SIGNATURE_VALID_UNANCHORED","errors":[],"claim":"signature_only"}
