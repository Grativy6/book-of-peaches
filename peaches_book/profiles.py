"""EXPERIMENTAL/NONNORMATIVE centralized test-registry transitions.

These helpers exercise one legacy registry design in ``test:`` namespaces.
They are not the PEACHES floor and designate no official checker or successor.
"""
from .core import PeachesError, canonical_bytes, b64, unb64
from .floor import _validate_ed25519_signature_encoding
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_TRANSITION_SIGNED_FIELDS = {
    "schema",
    "book_id",
    "previous_head",
    "old_profile",
    "new_profile",
    "old_checker_id",
    "new_checker_id",
    "effective_sequence",
}
_TRANSITION_FIELDS = _TRANSITION_SIGNED_FIELDS | {"old_signature", "new_signature"}

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
    if not isinstance(book_id, str) or not book_id.startswith("test:"): raise PeachesError("test book_id required")
    if not isinstance(previous_head, str) or not previous_head: raise PeachesError("previous_head required")
    body={"schema":"peaches.key-transition/0.1","old_profile":old_profile,"new_profile":new_profile,
          "old_checker_id":old_signer.key_id,"new_checker_id":new_signer.key_id,"effective_sequence":effective_sequence,
          "book_id":book_id,"previous_head":previous_head}
    signed=canonical_bytes(body)
    body["old_signature"]=b64(old_signer.key.sign(signed))
    body["new_signature"]=b64(new_signer.key.sign(signed))
    return body

def verify_key_transition(record):
    try:
        if not isinstance(record, dict) or set(record) != _TRANSITION_FIELDS: return False
        if record["schema"] != "peaches.key-transition/0.1": return False
        if (not isinstance(record["book_id"], str) or not record["book_id"].startswith("test:")
                or not isinstance(record["previous_head"], str) or not record["previous_head"]
                or not isinstance(record["old_profile"], str) or not record["old_profile"].startswith("test:")
                or not isinstance(record["new_profile"], str) or not record["new_profile"].startswith("test:")
                or isinstance(record["effective_sequence"], bool)
                or not isinstance(record["effective_sequence"], int)
                or record["effective_sequence"] < 1):
            return False
        old=record["old_checker_id"]; new=record["new_checker_id"]
        if not isinstance(old, str) or not isinstance(new, str) or not old.startswith("test:") or not new.startswith("test:"): return False
        unsigned={k:record[k] for k in _TRANSITION_SIGNED_FIELDS}
        signed=canonical_bytes(unsigned)
        old_key=unb64(old[5:]); old_signature=unb64(record["old_signature"])
        new_key=unb64(new[5:]); new_signature=unb64(record["new_signature"])
        if (b64(old_key)!=old[5:] or b64(new_key)!=new[5:]
                or b64(old_signature)!=record["old_signature"]
                or b64(new_signature)!=record["new_signature"]):
            return False
        _validate_ed25519_signature_encoding(old_key,old_signature)
        _validate_ed25519_signature_encoding(new_key,new_signature)
        Ed25519PublicKey.from_public_bytes(old_key).verify(old_signature,signed)
        Ed25519PublicKey.from_public_bytes(new_key).verify(new_signature,signed)
        return True
    except Exception: return False
