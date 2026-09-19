# Book of PEACHES

**A voluntary format for signed provenance records that anyone can issue and check.**

The Book of PEACHES provides a public specification and a read-only reference
checker for **provenance stamps**. Each stamp preserves an exact declaration,
a signing public key, and an issuer-claimed time in a portable record.
People and institutions can create and exchange stamps independently, without
registering with the Book or relying on a central stamper.

## Why it exists

A useful provenance record lets someone inspect what was declared and how it
connects to earlier material. It also keeps the limits of that evidence
visible. A signature, a timestamp claim, an agreement, and permission to act
answer different questions.

PEACHES was made to keep those distinctions intact as records move between
people, tools, and institutions. It provides a common starting point for
traces that others can check and build on, while leaving additional rules and
decisions with the participants who adopt them.

## What you can use it for

- **Record a declaration:** preserve the exact statement and its signature.
- **Describe an origin or lineage:** include references to earlier records or
  document hashes in a declaration.
- **Record agreed terms:** retain each party's signed declaration, with the
  agreement's interpretation and consequences handled outside the Book.
- **Preserve corrections:** issue a new stamp identifying what it corrects,
  while retaining the earlier record.

## How it works

1. **Declare.** Choose the exact statement or data to preserve, including any
   source references or additional requirements.
2. **Sign.** Use your own signing tool and key to create a stamp in the
   [PEACHES Floor format](FLOOR.md). The signature covers the declaration,
   issuer key, claimed time, and other required fields.
3. **Keep and share.** Retain the signed record and the source material it
   references. A hash can identify a copy; it does not store the source.
4. **Check.** A reader can verify the stamp's structure, hashes, identifiers,
   and signature locally, without contacting this repository.

The current format uses JSON, SHA-256, and Ed25519 signatures. Later records
can refer to earlier ones through their declarations; the base checker does
not interpret or authenticate those relationships automatically.

Additional time evidence can accompany a stamp separately, with its own
verification method. Participants can also define an optional **rubric**:
explicit requirements for a particular use or agreement, identified by a hash.
The reference checker checks the base format; evaluating additional evidence
or rubric requirements is a separate step.

## What verification means

A valid stamp establishes that its signature verifies under the included
public key over the specified data. Connecting that key to a person or
institution requires separate evidence. The recorded time is an issuer claim;
verifying the signature does not establish when the event happened.

A stamp does not confer truth, ethics, authority, consent, ownership, standing,
jurisdiction, or control. Any legal or institutional consequences come from
the applicable external agreement or rules. Participation is voluntary.

The Book supplies a specification, reference checker, and retained records.
There is no official stamper, privileged checker, or required registry.

## Try the checker

From the repository root, in an activated Python 3.11+ virtual environment:

```sh
python -m pip install .
peaches-check stamp genesis/signed-v1/genesis.floor.signed.json
```

This checks an included signed record. A successful result reports
`VALID_FLOOR_STRUCTURE_AND_SIGNATURE` with the limits described above.
To check another record, supply its file path:

```sh
peaches-check stamp path/to/stamp.json
```

The checker is read-only. Create signatures with an external signing tool;
keep private keys outside shared records and repositories.

## Specification and project records

- [PEACHES Floor v1](FLOOR.md): stamp format, verification rules, optional
  rubrics, and detached evidence.
- [JSON Schema](schemas/peaches-floor-v1.schema.json) and
  [calculation vectors](vectors/floor-v1/): resources for implementations.
- [Reference checker](peaches_book/floor.py): stateless verification code.
- [Founding records](genesis/signed-v1/README.md),
  [publication receipt](genesis/publication-v1/README.md), and
  [earlier preparation](genesis/preparation-v1/README.md): the retained origin
  and development trace.
- [Specification freeze](PREGENESIS-FREEZE.md): the original frozen payload
  and its recorded boundaries.

The older SQLite `TestBook` and `peaches-book` CLI remain a historical
Branchline experiment, documented in [CONTRACTS.md](CONTRACTS.md) and
[BOOK-RULES.md](BOOK-RULES.md). They are separate from the Floor protocol and
are not required to issue or check a stamp.

Repository-wide licensing remains unresolved. The scoped Apache-2.0 notice
for one retained ancestry document applies only as described in
[that notice](genesis/preparation-v1/sources/four-prompts.license.md).
