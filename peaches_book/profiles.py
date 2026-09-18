"""Explicit test-profile compatibility and successor decisions."""
from .core import PeachesError, canonical_bytes, b64, unb64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def transition(old: dict, new: dict) -> dict:
    """Classify a profile transition without rewriting old records."""
    if old.get("book_id") != new.get("book_id"):
        return {"status":"INCOMPATIBLE_SUCCESSOR_REQUIRED","reason":"book_identity_changed"}
    if old.get("profile_id") == new.get("profile_id") and old.get("schema") == new.get("schema"):
        return {"status":"COMPATIBLE_PROFILE"}
    if old.get("profile_id") != new.get("profile_id"):
        return {"status":"INCOMPATIBLE_SUCCESSOR_REQUIRED","reason":"profile_identity_changed","successor":"test:successor-profile"}
    return {"status":"INCOMPATIBLE_SUCCESSOR_REQUIRED","reason":"schema_changed","successor":"test:successor-schema"}

def signed_key_transition(old_profile, new_profile, old_signer, new_signer, effective_sequence, book_id=None, previous_head=None):
    if not str(new_profile).startswith("test:"): raise PeachesError("test profile required")
    body={"schema":"peaches.key-transition/0.1","old_profile":old_profile,"new_profile":new_profile,
          "old_checker_id":old_signer.key_id,"new_checker_id":new_signer.key_id,"effective_sequence":effective_sequence}
    if book_id is not None: body["book_id"] = book_id
    if previous_head is not None: body["previous_head"] = previous_head
    signed=canonical_bytes(body)
    body["old_signature"]=b64(old_signer.key.sign(signed))
    body["new_signature"]=b64(new_signer.key.sign(signed))
    return body

def verify_key_transition(record):
    try:
        old=record["old_checker_id"]; new=record["new_checker_id"]
        if not old.startswith("test:") or not new.startswith("test:"): return False
        unsigned={k:record[k] for k in record if k not in ("old_signature","new_signature")}
        Ed25519PublicKey.from_public_bytes(unb64(old[5:])).verify(unb64(record["old_signature"]),canonical_bytes(unsigned))
        Ed25519PublicKey.from_public_bytes(unb64(new[5:])).verify(unb64(record["new_signature"]),canonical_bytes(unsigned))
        return True
    except Exception: return False
