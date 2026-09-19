# Branchline offline test-book profile — nonnormative rules

**Status: NONNORMATIVE CENTRALIZED EXPERIMENT.** These rules describe the
existing local `TestBook` implementation. They are not the PEACHES floor, live
governance, a proposed Book service, or prerequisites for Genesis. The current
floor is [FLOOR.md](FLOOR.md), and the exact no-Genesis boundary is recorded in
[PREGENESIS-FREEZE.md](PREGENESIS-FREEZE.md).

This experiment intentionally tests a different architecture: one configured
checker signs and appends registration records to a local SQLite chain. Its
terms such as “active checker,” “registration,” “sequence,” “head,” and
“canonical store” are local to the experiment. They create no role, status, or
authority in PEACHES. In particular, an experimental checker-signed
registration is not an independently issuer-signed floor stamp.

## Envelope and identity

The experiment's unsigned registration envelope contains `schema`, `book_id`,
`profile_id`, `object_id`, exact `object`, `request_id`,
`request_intent_hash`, `observed_at`, `issuer_id`, and `claim_ceiling`. An
experimental checker-generated `registration_id`, sequence, previous head,
checker identity, and registered time are separate fields. Optional
institution material is carried separately and is never interpreted as
PEACHES authority.

Experiment-canonical bytes are UTF-8 JSON with sorted object keys, compact
separators, finite values, safe integers, bounded depth/items, and a
100,000-byte ceiling. SHA-256 digests those bytes. Fixture signatures use
Ed25519. These choices neither govern nor silently amend the floor.

## Append and persistence

The experimental offline registry is SQLite-backed with WAL and
`synchronous=FULL`. Its persistence surface is the `metadata`, `records`, and
`controls` tables. `records` is append-only and binds sequence, request
identity, intent hash, registration identity, previous head, and the
serialized bundle. `controls` contains signed test transitions. JSONL is not
the experiment's canonical store; exports are explicit test envelopes.

Only the active configured checker may append **within this experiment**. A
request retry with the same intent is idempotent. The same request with
changed object or intent is a conflict. Interrupted writes are recovered by
querying request ID plus intent hash and return `FOUND`, `NOT_FOUND`, or
`CONFLICT`; uncertain outcomes are never blindly retried. None of these
mechanics gates independent floor stamps.

## Verification ceiling

The experiment may report `SIGNATURE_VALID_UNANCHORED`,
`VALID_UNDER_DECLARED_CONTEXT`, or `BOOK_LOCAL_VALIDATED` under its own
contracts. Those names do not report floor conformance. None of these results
means truth, authority, consent, ethics, standing, approval, freshness, or
authorization.

## Transitions and mirrors

The experimental fixture transition is a signed control record with old/new
profile IDs, old/new checker IDs, and an effective next sequence. Both
synthetic test keys sign the same canonical control body. Earlier records
remain byte-preserved. A profile/schema change that is not covered by that
control is an incompatible successor condition. A compromised experimental
checker must not silently rewrite history or resume new append.

Experimental exports validate schema, book/profile identity, controls, record
sequence, unique identities, signatures, previous-head chain, and head. A
mirror is `INVALID`, `CURRENT_RELATIVE_TO_BOUND_HEAD`, `STALE`, `AHEAD`, or
`CONFLICTING` only relative to the verified local prefix; freshness remains
unknown without independent evidence.

## Scope exclusions

There is no Genesis, floor stamp, live checker, official channel, live key,
institutional attestation authority, real identity, registry publication,
background process, payment, model lock, private-context access, canon
admission, or automatic harmfulness decision in this profile. Its checker
designation, key custody, succession, append boundary, and mirror policy are
preserved only as experiment residuals; none is a Genesis prerequisite.
