# Branchline offline test-book profile contracts (0.1)

**Status: NONNORMATIVE CENTRALIZED EXPERIMENT.** This file documents the
interfaces already implemented by the local SQLite `TestBook`. It does not
define the PEACHES floor, a proposed Book service, or a Genesis prerequisite.
See [FLOOR.md](FLOOR.md) for the current floor and
[PREGENESIS-FREEZE.md](PREGENESIS-FREEZE.md) for the exact no-Genesis freeze.

PEACHES means Provenance, Ethics, Authority, Consent, Human Empathetic
Standing. Under the floor, a stamp is independently issued by its stated
issuer. The experiment below instead records a checker-signed registration
event under an identified test book/profile. That difference is deliberate
and quarantined. Neither form supplies truth, ethics, authority, consent,
standing, ownership, endorsement, certification, or legal effect. Current
usability of a separately sourced grant is a different question from historic
verification.

## Two experimental layers

The historical **experiment-common registration contract** defines canonical
finite JSON, distinct `book_id`, `profile_id`, `object_id`, `request_id`,
`registration_id`, issuer declarations and checker signatures, claim ceiling,
and verification results. “Common” here means shared by this implementation;
it does not mean normative across PEACHES. The experiment API is:

```python
prepare_registration(payload: dict) -> dict
verify_bundle(bundle: dict) -> dict
```

The **Branchline offline test-book profile** adds a test-book
append rule, transactional SQLite record table, signed sequence and
previous-head fields, inclusion evidence, export envelope and mirror/import
expectations. It neither changes the floor nor absorbs an institution or
external record. Institution statements and experimental registrations remain
separate events.

This implementation is intentionally offline and test-only. Every experiment
book and issuer must use the `test:` namespace, and no Genesis, live key,
permanent checker, floor stamp, or official PEACHES registration is created.

## Bytes and identities

Experiment objects are serialized as UTF-8 JSON with sorted keys, compact
separators, no floats, finite values only, and integers bounded to the
interoperable safe range (`2^53-1`); larger numbers must be decimal strings.
Maximum canonical payload is 100,000 bytes. Digests are SHA-256 over those
bytes. Fixture signatures use Ed25519 through the pinned `cryptography`
dependency. These choices are local to the experiment unless separately
named by another rubric.

The object digest is not a request identity. A changed object with an existing request ID is a conflict. An unchanged retry is idempotent. A deliberate second registration uses a new request ID. An interrupted write is recovered by querying the SQLite `records` table by request ID and intent hash; uncertain external outcomes are never retried blindly by this package.

Request IDs are unique within one declared test book. Experiment registration
IDs commit to the
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

`issuer_id` is an unverified submitter declaration in this experiment. The
checker signature authenticates only the experimental checker’s registration
event, not the issuer’s identity or institutional claims. Consequently, an
experimental registration is not a floor stamp. No issuer attestation is
promoted to authority.

The experimental append path uses SQLite WAL mode, `synchronous=FULL`, a
transaction, a process-local lock, an expected-head check and a unique
request/registration table. Recovery distinguishes `FOUND`, `NOT_FOUND`, and
`CONFLICT` for an uncertain request. A valid prefix does not establish
freshness, and conflicting or stale mirrors must remain visible to a
higher-level integration. Within this experiment, a signature without the
configured checker role, sequence, previous head and inclusion is reported as
`SIGNATURE_VALID_UNANCHORED`, never as an included registration. This rule has
no effect on independently issued floor stamps.

The experiment includes a signed key/profile transition fixture: both the old
checker and new checker sign the same control record, effective at a named
next sequence. Old records retain their original bytes and trust context. A
changed profile or schema otherwise requires a named test successor rather
than silently rewriting ancestry. This models centralized-registry succession
only; PEACHES does not inherit it, and live key governance is not implemented.

## Result ceiling

These result names apply only to the experiment. `VALID_UNDER_DECLARED_CONTEXT`
means its canonical envelope and signature match caller-declared checker,
chain and inclusion parameters. It is conditional evidence, not a floor
receipt. `SIGNATURE_VALID_UNANCHORED` verifies only the experiment signature
and canonical envelope. `BOOK_LOCAL_VALIDATED` and `BOOK_LOCAL_INCLUDED`
additionally use the configured test registry's control timeline and records.
No result means approved, safe, authorized, ethical, consented, current or
true; a verified prefix does not prove freshness.

## Recovery procedure

Retain the request ID and intent hash before dispatch. After an unknown result,
call `TestBook.recover_request(request_id, intent_hash)`: `FOUND` returns the
recorded bundle, `NOT_FOUND` permits reconsidering the same request, and
`CONFLICT` requires review. Changed intent requires a new deliberate request
or a surfaced conflict; never treat a retry as renewed authority.

Export with `TestBook.export()` and import into a separately configured test
mirror with `import_export()`. Preserve the experiment's book, local genesis
marker, and current checker/profile bindings. Its local genesis marker is not
the PEACHES Genesis. Current-state equality is relative to the bound head, not
proof of network freshness. Profile/key transition fixtures retain old bytes
and signed controls; incompatible experiment contracts require a named
successor. All keys supplied by `TestSigner` are public synthetic fixtures.
