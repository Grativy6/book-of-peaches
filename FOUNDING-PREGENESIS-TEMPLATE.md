# PEACHES founding / pre-Genesis package template

**Status:** `PRE_GENESIS_TEMPLATE_ONLY` — this file is not a Genesis record, a live key, a checker designation, or a stamp.

The package below is a structured preparation surface. A blank or `HUMAN_ADOPTION_PENDING` field is a required decision, not an implied default. Test identities and `test:` records are fixtures only. No field in this template may be copied into live state without a separate human adoption act and a fresh checker emission.

## Package identity

| Field | Value / decision | Classification |
|---|---|---|
| `package_schema` | `branchline.peaches.pre-genesis/0.1` | ENGINEERING_CHOICE |
| `package_status` | `PRE_GENESIS_TEMPLATE_ONLY` | ENGINEERING_CHOICE |
| `book_name` | Branchline PEACHES Book | BRANCHLINE_ADOPTION_DECISION |
| `book_id` | `HUMAN_ADOPTION_PENDING` | HUMAN_ADOPTION_PENDING |
| `profile_id` | `HUMAN_ADOPTION_PENDING` | HUMAN_ADOPTION_PENDING |
| `protocol_version` | `HUMAN_ADOPTION_PENDING` | HUMAN_ADOPTION_PENDING |
| `genesis_descriptor` | `HUMAN_ADOPTION_PENDING` | HUMAN_ADOPTION_PENDING |
| `claim_ceiling` | one identified checker registration event only | BRANCHLINE_ADOPTION_DECISION |
| `creates_genesis` | `false` | ENGINEERING_CHOICE |
| `creates_live_stamp` | `false` | ENGINEERING_CHOICE |

## Checker and control

| Field | Value / decision | Classification |
|---|---|---|
| `checker_id` | `HUMAN_ADOPTION_PENDING` | HUMAN_ADOPTION_PENDING |
| `checker_designation_basis` | `HUMAN_ADOPTION_PENDING` | HUMAN_ADOPTION_PENDING |
| `key_algorithm` | Ed25519 | ENGINEERING_CHOICE; replaceable until adopted |
| `key_custody` | `HUMAN_ADOPTION_PENDING` | HUMAN_ADOPTION_PENDING |
| `succession_rule` | signed old/new control record effective at a named next sequence; live rule remains pending | ENGINEERING_CHOICE / HUMAN_ADOPTION_PENDING |
| `compromise_recovery` | halt new append, preserve history, publish a separately adopted recovery/successor record | ENGINEERING_CHOICE / HUMAN_ADOPTION_PENDING |
| `operator_accountability` | only accuracy of its own recorded event; no endorsement, supervision, authority, or downstream responsibility | BRANCHLINE_ADOPTION_DECISION |

## Canonical record choices

| Field | Value / decision | Classification |
|---|---|---|
| `encoding` | UTF-8 JSON, sorted keys, compact separators, finite values, bounded depth/items/bytes | ENGINEERING_CHOICE |
| `digest` | SHA-256 over canonical bytes | ENGINEERING_CHOICE |
| `signature_encoding` | Ed25519 signature over the unsigned canonical envelope; URL-safe base64 fixture transport | ENGINEERING_CHOICE |
| `persistence` | SQLite WAL, `synchronous=FULL`, append-only `records` table, signed sequence and previous-head fields | ENGINEERING_CHOICE |
| `canonical_append` | active checker only; human edits and mirror edits are noncanonical | BRANCHLINE_ADOPTION_DECISION |
| `correction` | append a new independent record; never mutate or backdate an earlier record | SOURCE_DERIVED + BRANCHLINE_ADOPTION_DECISION |

## Source and review attachments

| Attachment | Required state | Classification |
|---|---|---|
| `FOUNDING-MANIFEST.json` | exact version, public locator, observed hash and disposition for each source | SOURCE_DERIVED / ENGINEERING_CUSTODY |
| `SOURCE-CARDS.md` | independent cards with rules, nonclaims, tests, and open burdens | SOURCE_DERIVED |
| `SOURCE-CLAUSE-LEDGER.md` | every adopted clause traced to source or explicitly marked Branchline decision | SOURCE_DERIVED / BRANCHLINE_ADOPTION_DECISION |
| `CONFLICT-RESIDUAL-REGISTER.md` | unresolved version, terminology, authority, and reopening burdens | SOURCE_DERIVED / HUMAN_ADOPTION_PENDING |
| `FOUNDING-BASIS-DRAFT.md` | readable proposed basis; not adopted | BRANCHLINE_ADOPTION_DECISION DRAFT |
| `BOOK-RULES.md` | machine-facing rules and result ceiling; not live governance | ENGINEERING_CHOICE / BRANCHLINE_ADOPTION_DECISION |

## Explicit non-events

- No Genesis is present.
- No live checker key, permanent operator, official channel, or human founding identity is supplied.
- No source is adopted merely because it appears in the manifest or has a matching hash.
- No PEACHES Stamp confers truth, integrity warranty, ethics, authority, consent, standing, ownership, permission, model lock, canon admission, or branch control.
- No test fixture, `test:` namespace, synthetic key, or successful local verification may be promoted into live state.

## Human adoption checklist

```yaml
human_adoption:
  book_id: HUMAN_ADOPTION_PENDING
  profile_id: HUMAN_ADOPTION_PENDING
  protocol_version: HUMAN_ADOPTION_PENDING
  checker_id: HUMAN_ADOPTION_PENDING
  checker_designation: HUMAN_ADOPTION_PENDING
  key_custody: HUMAN_ADOPTION_PENDING
  succession_and_compromise: HUMAN_ADOPTION_PENDING
  mirror_and_checkpoint_policy: HUMAN_ADOPTION_PENDING
  privacy_and_metadata_policy: HUMAN_ADOPTION_PENDING
  genesis_procedure: HUMAN_ADOPTION_PENDING
  adopted_by: HUMAN_ADOPTION_PENDING
  adopted_at: HUMAN_ADOPTION_PENDING
```

This checklist records choices to be made. It does not itself make them.
