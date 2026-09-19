# PEACHES pre-Genesis freeze

**Status:** `FROZEN_PRE_GENESIS`

**Protocol frozen:** `peaches.floor/1`

**Creates Genesis:** no

**Creates `PEACHES:H1`:** no

**Creates a key or live signature:** no

## Frozen scope

This freeze closes the alignment pass around a decentralized PEACHES floor.
The exact protocol payload consists of the files listed below. Their hashes
were computed from the final bytes before the freeze commit. The repository
commit containing this file anchors the complete tree; this file intentionally
does not attempt a self-referential digest.

| Path | SHA-256 |
|---|---|
| `FLOOR.md` | `c401e3dfc03e2bb87d841287d5847e16f5fda9a3b9346918d42d758bcbfcf276` |
| `schemas/peaches-floor-v1.schema.json` | `f88e63ea52096bcaae6db5d4e7abfd5e162d2cb4c16e97bc76ee63a102a0c30b` |
| `vectors/floor-v1/unsigned-stamp-body.json` | `a98a68f122f4d09801935881322414b36281b788cf0b942ee52334c2f7b15483` |
| `vectors/floor-v1/observation-core.json` | `782f1f2729f1f27f8c53f410551e3e63628e4f0221c67947d8b2e349587e7d45` |
| `vectors/floor-v1/calculation-expectations.json` | `c8677b601f981eea0c8890126a85c5d0e5b3931bef1fce52eabf9cf2410712fd` |
| `vectors/floor-v1/invalid-duplicate-key.json` | `2deacecfda69914559c06c696a4dbeb643d93f6da0ba2f5da6aa289b63bcf97d` |

The alignment decisions now frozen are:

- stamps are created and signed by their issuers;
- no PEACHES-operated stamper, signer, clock, append boundary, registry, or
  privileged checker exists;
- base verification is local and stateless;
- the exact declaration bytes, their digest, claimed time, issuer key, nonce,
  and optional content-addressed rubric are bound into the stamp;
- `claimed_at` is an issuer claim, while `observed_no_later_than` is detached
  evidence with its own content-addressed verification method;
- a Floor result does not confer truth, ethics, authority, consent, standing,
  jurisdiction, legal effect, or obligation;
- stricter integration rules are optional content-addressed rubrics; and
- two independent machine checkers are required only when a selected rubric
  says so, with disagreement preventing that rubric's integration result.

The older SQLite checker-registration implementation remains a nonnormative
Branchline offline test-book profile. It is not the Floor and is not a
canonical append path for PEACHES.

## Deliberately absent

No file in this freeze is a Genesis declaration, lineage stamp, live
stamp, key pair, signature, timestamp witness, checker designation,
institutional agreement, or legal act. Test vectors contain no private key or
signature and MUST NOT be promoted into live use. The 32 zero octets occupying
the vector's `public_key` field are inert calculation input, not a generated or
adopted key; no corresponding private material is supplied.

No human-readable special identifier is created or reserved by this freeze.
In particular, `PEACHES:H1` remains an unissued proposed label until the later
human act supplies its exact meaning and bytes.

## Remaining human gates

Only the following gates remain before a Genesis and first lineage stamp can
be prepared. Each requires an explicit later human act; none is supplied or
inferred here.

1. **Exact Genesis and H1 bytes.** Freeze the declaration that distinguishes
   the structural Genesis object from the proposed first Hearthline lineage
   stamp, including the exact bounded meaning of `PEACHES:H1`.
2. **Issuer proof and live key.** Choose or create the issuer key outside this
   pre-Genesis package, decide what evidence binds it to the declarant, protect
   its private material, and authorize the exact signing act.
3. **License and rights-holder identity.** Identify the party or parties able
   to license each repository component and enact explicit license text.
   A possible later split is CC0-1.0 for normative prose, schema, and vectors,
   with Apache-2.0 for code; this note grants neither license.
4. **Publication anchor.** Select at least one independently checkable
   publication or timestamp method, freeze its method document and
   content-addressed `method_id`, and preserve the resulting detached evidence.
   For Genesis chronology, the method MUST bind the exact completed signed
   envelope, or the exact signature bytes together with its `stamp_id`; binding
   only `stamp_id` establishes at most observability of the unsigned body.

## Stop rule

The floor needs no further conceptual expansion before the key turn. Changes
to the frozen files require an explicit successor or a reopened pre-Genesis
freeze with a recorded reason. The later key turn may fill the remaining gates
but MUST NOT silently rewrite this freeze or treat it as prior authorization.
