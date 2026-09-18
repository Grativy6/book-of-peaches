# PEACHES Book Rules — offline profile

These rules describe the current test profile. They are not live governance.

## Envelope and identity

The unsigned registration envelope contains `schema`, `book_id`, `profile_id`, `object_id`, exact `object`, `request_id`, `request_intent_hash`, `observed_at`, `issuer_id`, and `claim_ceiling`. A checker-generated `registration_id`, sequence, previous head, checker identity, and registered time are separate fields. Optional institution material is carried separately and is never interpreted as PEACHES authority.

Canonical bytes are UTF-8 JSON with sorted object keys, compact separators, finite values, safe integers, bounded depth/items, and a 100,000-byte ceiling. SHA-256 digests those bytes. Fixture signatures use Ed25519. Any future live profile must freeze or explicitly replace these choices.

## Append and persistence

The offline book is SQLite-backed with WAL and `synchronous=FULL`. The actual persistence surface is the `metadata`, `records`, and `controls` tables. `records` is append-only and binds sequence, request identity, intent hash, registration identity, previous head, and the serialized bundle. `controls` contains signed test transitions. JSONL is not the canonical store; exports are explicit test envelopes.

Only the active configured checker may append. A request retry with the same intent is idempotent. The same request with changed object or intent is a conflict. Interrupted writes are recovered by querying request ID plus intent hash and return `FOUND`, `NOT_FOUND`, or `CONFLICT`; uncertain outcomes are never blindly retried.

## Verification ceiling

`SIGNATURE_VALID_UNANCHORED` means signature bytes verify under the supplied public key and nothing about book inclusion. `VALID_UNDER_DECLARED_CONTEXT` means the signature and supplied book context agree; the context is explicitly caller-supplied and is not itself a book receipt. A locally checked chain may report `BOOK_LOCAL_VALIDATED`. None of these results means truth, authority, consent, ethics, standing, approval, freshness, or authorization.

## Transitions and mirrors

The fixture transition is a signed control record with old/new profile IDs, old/new checker IDs, and an effective next sequence. Both test keys sign the same canonical control body. Earlier records remain byte-preserved. A profile/schema change that is not covered by that control is an incompatible successor condition. A compromised checker must not silently rewrite history or resume new append.

Exports must validate schema, book/profile identity, controls, record sequence, unique identities, signatures, previous-head chain, and head. A mirror is `INVALID`, `CURRENT_RELATIVE_TO_BOUND_HEAD`, `STALE`, `AHEAD`, or `CONFLICTING` only relative to the verified local prefix; freshness remains unknown without an independent signed checkpoint.

## Scope exclusions

There is no Genesis, live checker, official channel, live key, institutional attestation authority, real identity, registry publication, background process, payment, model lock, private-context access, canon admission, or automatic harmfulness decision in this profile.
