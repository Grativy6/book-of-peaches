# Checker-centered founding package template — superseded

**Status:** `SUPERSEDED_CENTRALIZED_EXPERIMENT_TEMPLATE` — preserved for
provenance only. This file is not the current pre-Genesis freeze, a Genesis
record, a live key, a checker designation, a stamp, or an adoption checklist.

The active floor is [PEACHES Floor v1](FLOOR.md), protocol identifier
`peaches.floor/1`. The exact current boundary is
[PREGENESIS-FREEZE.md](PREGENESIS-FREEZE.md), status
`FROZEN_PRE_GENESIS`. The historical package below prepared a centralized
registry experiment. Its blank or `HUMAN_ADOPTION_PENDING` fields no longer
identify PEACHES Genesis prerequisites and must not be filled to imply
adoption.

## Historical package identity

| Field | Historical value / decision | Current classification |
|---|---|---|
| `package_schema` | `branchline.peaches.pre-genesis/0.1` | ENGINEERING_CHOICE |
| `package_status` | `PRE_GENESIS_TEMPLATE_ONLY` | SUPERSEDED_EXPERIMENT_STATUS |
| `book_name` | Branchline PEACHES Book | SUPERSEDED_EXPERIMENT_PROPOSAL |
| `book_id` | `HUMAN_ADOPTION_PENDING` | OPTIONAL_EXPERIMENT_RESIDUAL |
| `profile_id` | `HUMAN_ADOPTION_PENDING` | OPTIONAL_EXPERIMENT_RESIDUAL |
| `protocol_version` | `HUMAN_ADOPTION_PENDING` | SUPERSEDED BY `peaches.floor/1` FOR THE FLOOR |
| `genesis_descriptor` | `HUMAN_ADOPTION_PENDING` | NOT SATISFIED; NO GENESIS |
| `claim_ceiling` | one identified checker registration event only | EXPERIMENT-LOCAL; NOT A FLOOR STAMP |
| `creates_genesis` | `false` | ENGINEERING_CHOICE |
| `creates_live_stamp` | `false` | ENGINEERING_CHOICE |

## Historical experiment checker and control

These fields are preserved because they explain the existing test code. None
is a PEACHES floor or Genesis requirement.

| Field | Historical value / decision | Current classification |
|---|---|---|
| `checker_id` | `HUMAN_ADOPTION_PENDING` | OPTIONAL_EXPERIMENT_RESIDUAL |
| `checker_designation_basis` | `HUMAN_ADOPTION_PENDING` | OPTIONAL_EXPERIMENT_RESIDUAL |
| `key_algorithm` | Ed25519 | EXPERIMENT ENGINEERING CHOICE |
| `key_custody` | `HUMAN_ADOPTION_PENDING` | OPTIONAL_EXPERIMENT_RESIDUAL |
| `succession_rule` | signed old/new control record effective at a named next sequence | OPTIONAL_EXPERIMENT MECHANISM |
| `compromise_recovery` | halt new append, preserve history, publish a separately adopted recovery/successor record | OPTIONAL_EXPERIMENT MECHANISM |
| `operator_accountability` | only accuracy of its own recorded event; no endorsement, supervision, authority, or downstream responsibility | SUPERSEDED REGISTRY PROPOSAL |

## Historical experiment record choices

| Field | Historical value / decision | Current classification |
|---|---|---|
| `encoding` | UTF-8 JSON, sorted keys, compact separators, finite values, bounded depth/items/bytes | EXPERIMENT ENGINEERING CHOICE |
| `digest` | SHA-256 over canonical bytes | EXPERIMENT ENGINEERING CHOICE |
| `signature_encoding` | Ed25519 signature over the unsigned canonical envelope; URL-safe base64 fixture transport | SYNTHETIC EXPERIMENT FIXTURE |
| `persistence` | SQLite WAL, `synchronous=FULL`, append-only `records` table, signed sequence and previous-head fields | EXPERIMENT ENGINEERING CHOICE |
| `canonical_append` | active checker only; human edits and mirror edits are noncanonical | SUPERSEDED; NOT THE PEACHES FLOOR |
| `correction` | append a new independent record; never mutate or backdate an earlier record | EXPERIMENT MECHANISM; NON-REWRITING PRINCIPLE RETAINED |

## Source and review attachments

| Attachment | Required state | Classification |
|---|---|---|
| `FOUNDING-MANIFEST.json` | exact version, public locator, observed hash and disposition for each source | SOURCE_DERIVED / ENGINEERING_CUSTODY |
| `SOURCE-CARDS.md` | independent cards with rules, nonclaims, tests, and open burdens | SOURCE_DERIVED |
| `SOURCE-CLAUSE-LEDGER.md` | mapped clauses distinguish source observations, Branchline choices, and superseded proposals | PROVENANCE MAPPING; NO SOURCE ADOPTION |
| `CONFLICT-RESIDUAL-REGISTER.md` | unresolved and experiment-local burdens remain visible and reopenable | PROVENANCE / RESIDUAL CUSTODY |
| `FOUNDING-BASIS-DRAFT.md` | superseded checker-centered proposal retained for provenance | SUPERSEDED EXPERIMENT DRAFT |
| `BOOK-RULES.md` | rules and result ceiling for the nonnormative offline test-book profile | EXPERIMENT ENGINEERING CHOICE |
| `FLOOR.md` | current minimal floor | BRANCHLINE SPECIFICATION; NO GENESIS EFFECT |
| `PREGENESIS-FREEZE.md` | exact frozen absence/presence boundary | PRE-GENESIS ALIGNMENT RECORD |

## Explicit non-events

- No Genesis or live floor stamp is present.
- No official stamper, official checker, privileged registry, live checker key,
  permanent operator, official channel, or human founding identity is supplied.
- No source is adopted merely because it appears in the manifest or has a matching hash.
- No PEACHES Stamp confers truth, integrity warranty, ethics, authority, consent, standing, ownership, permission, model lock, canon admission, or branch control.
- No test fixture, `test:` namespace, synthetic key, or successful local verification may be promoted into live state.
- No checker designation, checker key custody, succession rule, canonical append
  boundary, sequence, head, or mirror policy is required by the floor or by a
  future Genesis.

## Historical experiment checklist — retained, not active

The earlier proposal left the following centralized-registry decisions open.
They remain optional experiment residuals, not human adoption gates for the
PEACHES floor or Genesis.

```yaml
historical_experiment_followups:
  book_id: HUMAN_ADOPTION_PENDING
  profile_id: HUMAN_ADOPTION_PENDING
  checker_id: HUMAN_ADOPTION_PENDING
  checker_designation: HUMAN_ADOPTION_PENDING
  key_custody: HUMAN_ADOPTION_PENDING
  succession_and_compromise: HUMAN_ADOPTION_PENDING
  mirror_and_checkpoint_policy: HUMAN_ADOPTION_PENDING
  privacy_and_metadata_policy: HUMAN_ADOPTION_PENDING
```

This preserved checklist records what the experiment once proposed to decide.
It makes no choice and has no effect on the current floor. The repository
remains `FROZEN_PRE_GENESIS`; a later key turn and Genesis are separate human
acts outside this template.
