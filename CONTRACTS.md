# PEACHES offline contracts (0.1)

PEACHES means Provenance, Ethics, Authority, Consent, Human Empathetic Standing. A stamp records an identified registration event under an identified book/profile. It does not supply truth, ethics, authority, consent, standing, ownership, endorsement, or certification. Current usability of a separately sourced grant is a different question from historic stamp verification.

## Two layers

The **common stamp specification** defines canonical finite JSON, distinct `book_id`, `profile_id`, `object_id`, `request_id`, `registration_id`, issuer declarations and checker signatures, claim ceiling, and verification results. The common API is:

```python
prepare_registration(payload: dict) -> dict
verify_bundle(bundle: dict) -> dict
```

The **Branchline Book profile** adds a test-book append rule, transactional SQLite record table, signed sequence and previous-head fields, inclusion evidence, export envelope and mirror/import expectations. It does not change the stamp meaning or absorb an institution/external book. Institution stamps and a later PEACHES registration remain separate events.

This implementation is intentionally offline and test-only. Every book and issuer must use the `test:` namespace, and no real Genesis, live key, permanent checker, or real stamp is created.

## Bytes and identities

Objects are serialized as UTF-8 JSON with sorted keys, compact separators, no floats, finite values only, and integers bounded to the interoperable safe range (`2^53-1`); larger numbers must be decimal strings. Maximum canonical payload is 100,000 bytes. Digests are SHA-256 over those bytes. Fixture signatures use Ed25519 through the pinned `cryptography` dependency.

The object digest is not a request identity. A changed object with an existing request ID is a conflict. An unchanged retry is idempotent. A deliberate second registration uses a new request ID. An interrupted write is recovered by querying the SQLite `records` table by request ID and intent hash; uncertain external outcomes are never retried blindly by this package.

Request IDs are unique within one declared test book. Stamp IDs commit to the
canonical envelope, including book/profile, checker position and previous
head. SHA-256 supplies collision resistance, not a mathematical guarantee
that no two IDs can ever coincide. A database uniqueness conflict is an
append failure requiring review; it never overwrites the earlier record.
Delayed requests retain source observation time separately from the checker's
registration time.

To minimize disclosure, submit a commitment object rather than private source
content. The receipt then identifies that exact commitment object; it does not
prove the undisclosed source or make its contents public. This package does
not discover or ingest private evidence.

`issuer_id` is an unverified submitter declaration in this release. The checker signature authenticates the checker’s registration event, not the issuer’s identity or institutional claims. No issuer attestation is promoted to authority.

The append path uses SQLite WAL mode, `synchronous=FULL`, a transaction, a process-local lock, an expected-head check and a unique request/registration table. Recovery distinguishes `FOUND`, `NOT_FOUND`, and `CONFLICT` for an uncertain request. A valid prefix does not establish freshness, and conflicting or stale mirrors must remain visible to a higher-level integration. A signature without trusted checker role, sequence, previous head and inclusion is reported as `SIGNATURE_VALID_UNANCHORED`, never as a registered stamp.

The test profile includes a signed key/profile transition fixture: both the old checker and new checker sign the same control record, effective at a named next sequence. Old records retain their original bytes and trust context. A changed profile or schema otherwise requires a named test successor rather than silently rewriting ancestry. Live key governance is not implemented.

## Result ceiling

`VALID_UNDER_DECLARED_CONTEXT` means the canonical envelope and signature match caller-declared checker, chain and inclusion parameters. It is conditional evidence, not a book receipt. `SIGNATURE_VALID_UNANCHORED` verifies only the signature and canonical envelope. `BOOK_LOCAL_VALIDATED` and `BOOK_LOCAL_INCLUDED` additionally use the configured test book's anchored control timeline and records. No result means approved, safe, authorized, ethical, consented, current or true; a verified prefix does not prove freshness.

## Recovery procedure

Retain the request ID and intent hash before dispatch. After an unknown result,
call `TestBook.recover_request(request_id, intent_hash)`: `FOUND` returns the
recorded bundle, `NOT_FOUND` permits reconsidering the same request, and
`CONFLICT` requires review. Changed intent requires a new deliberate request
or a surfaced conflict; never treat a retry as renewed authority.

Export with `TestBook.export()` and import into a separately configured
test mirror with `import_export()`. Preserve its book, genesis and current
checker/profile bindings. Current-state equality is relative to the bound
head, not proof of network freshness. Profile/key transition fixtures retain
old bytes and signed controls; incompatible source contracts require a named
successor. All keys supplied by `TestSigner` are public synthetic fixtures.
