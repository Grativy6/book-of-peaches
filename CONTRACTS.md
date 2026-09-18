# PEACHES offline contracts (0.1)

PEACHES means Provenance, Ethics, Authority, Consent, Human Empathetic Standing. A stamp records an identified registration event under an identified book/profile. It does not supply truth, ethics, authority, consent, standing, ownership, endorsement, or certification. Current usability of a separately sourced grant is a different question from historic stamp verification.

## Two layers

The **common stamp specification** defines canonical finite JSON, distinct `book_id`, `profile_id`, `object_id`, `request_id`, `registration_id`, issuer and checker signatures, claim ceiling, and verification results. The common API is:

```python
prepare_registration(payload: dict) -> dict
verify_bundle(bundle: dict) -> dict
```

The **Branchline Book profile** adds a test-book append rule, transactional SQLite record table, signed sequence and previous-head fields, inclusion evidence, export envelope and mirror/import expectations. It does not change the stamp meaning or absorb an institution/external book. Institution stamps and a later PEACHES registration remain separate events.

This implementation is intentionally offline and test-only. Every book and issuer must use the `test:` namespace, and no real Genesis, live key, permanent checker, or real stamp is created.

## Bytes and identities

Objects are serialized as UTF-8 JSON with sorted keys, compact separators, no floats, finite values only, and integers bounded to the interoperable safe range (`2^53-1`); larger numbers must be decimal strings. Maximum canonical payload is 100,000 bytes. Digests are SHA-256 over those bytes. Fixture signatures use Ed25519 through the pinned `cryptography` dependency.

The object digest is not a request identity. A changed object with an existing request ID is a conflict. An unchanged retry is idempotent. A deliberate second registration uses a new request ID. An interrupted write is recovered by querying the SQLite `records` table by request ID and intent hash; uncertain external outcomes are never retried blindly by this package.

`issuer_id` is an unverified submitter declaration in this release. The checker signature authenticates the checker’s registration event, not the issuer’s identity or institutional claims. No issuer attestation is promoted to authority.

The append path uses SQLite WAL mode, `synchronous=FULL`, a transaction, a process-local lock, an expected-head check and a unique request/registration table. Recovery distinguishes `FOUND`, `NOT_FOUND`, and `CONFLICT` for an uncertain request. A valid prefix does not establish freshness, and conflicting or stale mirrors must remain visible to a higher-level integration. A signature without trusted checker role, sequence, previous head and inclusion is reported as `SIGNATURE_VALID_UNANCHORED`, never as a registered stamp.

The test profile includes a signed key/profile transition fixture: both the old checker and new checker sign the same control record, effective at a named next sequence. Old records retain their original bytes and trust context. A changed profile or schema otherwise requires a named test successor rather than silently rewriting ancestry. Live key governance is not implemented.

## Result ceiling

`VALID_REGISTERED_STAMP` means the bytes, object/request identities, trusted checker role, chain position, inclusion and signature verified for the supplied bundle. `SIGNATURE_VALID_UNANCHORED` means only that the signature verifies. Neither status means approved, safe, authorized, ethical, consented, current, or true. `VALID_PREFIX` means the local test book's records verified; it does not prove that the book is current or canonical outside its named test book.
