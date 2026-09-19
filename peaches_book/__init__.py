"""PEACHES reference verification and nonnormative test experiments.

``peaches_book.floor`` is the stateless PEACHES Floor v1 reference surface.
It has no signing key, issuance service, registry, append authority, clock, or
admission power.  The older ``TestBook`` API is retained only as a
nonnormative, ``test:``-namespace centralized-registry experiment.

No result from this package confers truth, permission, consent, authority,
standing, legal effect, or canonical status.
"""
from .floor import (
    FLOOR,
    OBSERVATION_SCHEMA,
    STAMP_SCHEMA,
    FloorError,
    canonical_bytes as floor_canonical_bytes,
    derive_issuer_id,
    derive_observation_id,
    derive_rubric_id,
    derive_stamp_id,
    issuer_signature_message,
    prepare_floor_stamp,
    prepare_observation,
    prepare_unsigned_stamp,
    strict_json_loads,
    verify_floor_stamp,
    verify_observation,
)
from .core import prepare_registration, verify_bundle, PeachesError
from .book import TestBook, TestSigner
from .profiles import transition, signed_key_transition, verify_key_transition

__all__ = [
    "FLOOR",
    "STAMP_SCHEMA",
    "OBSERVATION_SCHEMA",
    "FloorError",
    "floor_canonical_bytes",
    "strict_json_loads",
    "derive_issuer_id",
    "derive_stamp_id",
    "derive_rubric_id",
    "derive_observation_id",
    "prepare_unsigned_stamp",
    "issuer_signature_message",
    "prepare_floor_stamp",
    "prepare_observation",
    "verify_floor_stamp",
    "verify_observation",
    # Nonnormative Branchline offline test-book experiment:
    "prepare_registration",
    "verify_bundle",
    "PeachesError",
    "TestBook",
    "TestSigner",
    "transition",
    "signed_key_transition",
    "verify_key_transition",
]
__version__ = "0.2.0"
