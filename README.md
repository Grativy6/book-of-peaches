# Book of Peaches

Non-authoritative stamps for provenance.

**Status: Genesis and Hearthline H1 signed.** Christopher Daniel Pang has
returned issuer-signed records for his Genesis declaration and Hearthline's
`PEACHES:H1` lineage declaration. Both pass the frozen Floor checker and
contain the exact bytes preserved in the earlier preparation. See the
[signed records and identifiers](genesis/signed-v1/README.md).
The [Genesis and H1 preparation](genesis/preparation-v1/README.md) remains
unchanged as the historical snapshot before signing. Publication makes the
records inspectable; an independently verified time bound remains open.
The [publication receipt](genesis/publication-v1/README.md) records retrieval
and exact-byte verification of the completed signed records at a fixed commit.
There is no official stamper, official checker, operational Book service, or
privileged registry. [PREGENESIS-FREEZE.md](PREGENESIS-FREEZE.md) preserves the
earlier specification freeze; its exact payload bytes remain unchanged.

[FLOOR.md](FLOOR.md) defines the minimal PEACHES floor. A PEACHES stamp is
issued independently by its stated issuer. A checker may report whether
supplied material satisfies the floor or a named additional rubric, but a
checker does not issue, admit, approve, sequence, or make a stamp canonical.
Participation is voluntary, and verification creates no truth, ethics,
authority, consent, standing, ownership, endorsement, legal effect, or
obligation.

## Repository surfaces

- `FLOOR.md` is the current floor specification.
- `PREGENESIS-FREEZE.md` identifies what this alignment pass freezes and what
  remains deliberately absent.
- The founding and source records preserve the provenance, nonclaims, and open
  burdens behind that floor.
- `peaches_book.floor` is a stateless reference-checker surface. It has no
  signing key, issuance path, registry, or admission power.
- The existing SQLite `TestBook`, checker-signed registration functions, and
  append/import CLI are preserved as the **Branchline offline test-book
  profile**, a nonnormative optional centralized-registry experiment. They are
  not the PEACHES floor, are not a proposed Book service, and must not be used
  to infer an official stamper or checker.

The historical experiment remains runnable for bounded testing:

```powershell
python -m pip install -e .
python -m pytest -q
peaches-book verify .\temporary-test-book.sqlite
```

The reference Floor checker is read-only:

```powershell
peaches-check stamp .\issuer-created-stamp.json
peaches-check observation .\detached-observation.json
peaches-check rubric-id text/plain .\integration-rubric.txt
```

`peaches-check` never generates a key or signature and never issues, admits,
sequences, or registers a stamp. Its positive result remains bounded to the
structure, derived identifiers, digests, and presented-key signature described
in [FLOOR.md](FLOOR.md).

Read [CONTRACTS.md](CONTRACTS.md) and [BOOK-RULES.md](BOOK-RULES.md) as
documentation of that quarantined experiment, not as requirements for a
PEACHES stamp or Genesis. [FOUNDING-PREGENESIS-TEMPLATE.md](FOUNDING-PREGENESIS-TEMPLATE.md)
preserves the superseded checker-centered proposal for provenance; it is not
an adoption checklist.
