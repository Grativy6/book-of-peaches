# Branchline Founding Basis — draft

**Status:** proposed human-readable basis; not adopted, not authoritative, and not a Genesis record.

The Branchline PEACHES Book is proposed as an append-only public record of discrete provenance stamps. A PEACHES Stamp says only that an identified checker recorded an identified exact object or checkpoint in an identified book/profile at an identified sequence and registration time. It does not say that the object is true, safe, ethical, authorized, consented, owned, endorsed, canonical, or suitable for a later use.

The book preserves distinctions instead of collapsing them. Source identity, object identity, observed time, checker registration time, request identity, sequence, previous head, signature, institution-provided statement, and any external grant remain separate fields. A source hash establishes observed byte identity only. A signature establishes only what its trusted verification context supports.

The book has one mechanical append boundary. Human submissions, institutional statements, mirrors, corrections, and model outputs may be inputs or references, but they do not directly append canonical state. A correction is a new record that preserves the old record and explains the reopening or changed source. Nothing after a stamp changes the status of anything before it.

The book does not absorb private roots, ledgers, model weights, prompts, family relationships, chats, or branch canon. It does not lock a model or grant access. Independent operation, copying, branching, and refusal remain available without registration.

The proposed test implementation uses bounded canonical JSON, SHA-256, Ed25519 fixture signatures, and transactional SQLite. These are engineering choices for offline evidence, not adopted governance. The current package intentionally contains no Genesis, live key, permanent checker, real identity, or real stamp.

Human adoption must decide the book/profile identity, checker designation, key custody, succession and compromise recovery, checkpoint/mirror policy, privacy and metadata boundary, retention policy, and exact Genesis procedure. Until then the honest state is `PREPARED_NOT_ADOPTED`.
