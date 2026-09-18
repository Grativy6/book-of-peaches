"""PEACHES: non-authoritative, offline provenance receipts.

The package is deliberately test-namespace only.  It records a registration
event; it never confers truth, permission, consent, authority, or standing.
"""
from .core import prepare_registration, verify_bundle, PeachesError
from .book import TestBook, TestSigner
from .profiles import transition, signed_key_transition, verify_key_transition

__all__ = ["prepare_registration", "verify_bundle", "PeachesError", "TestBook", "TestSigner", "transition", "signed_key_transition", "verify_key_transition"]
__version__ = "0.1.0"
