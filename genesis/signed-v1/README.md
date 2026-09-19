# Signed Genesis and Hearthline H1

Christopher Daniel Pang returned these two signed declarations for
publication. The exact signed JSON files, original checker reports, public
key record, signing receipt, checksums, and uploaded ZIP are preserved here.
No private key or passphrase is included.

| Record | Signed file | Stamp ID |
|---|---|---|
| Book of PEACHES Genesis | [genesis.floor.signed.json](genesis.floor.signed.json) | `peaches:stamp:v1:be8e384bbe1dacd2b2ae1b89ad0974742bb3bca8dbf07dc67ba8d4e1507a125c` |
| Hearthline lineage, `PEACHES:H1` | [h1.floor.signed.json](h1.floor.signed.json) | `peaches:stamp:v1:4aa5684ef76a88dd034ccae265bc2a67439194d5d74b7b319ef053afd99529cb` |

Both use issuer
`peaches:issuer:v1:85aa17713dba350e3544d0ec184589283ee60787e5397b5b6ce0cb3810690ac8`.
The [record index](record-index.json) retains the complete identifiers and
SHA-256 hashes of the exact completed envelopes. `PEACHES:H1` is the label
within the signed H1 declaration; this index is an unsigned convenience
mapping, not a registry, extra Floor field, or new signature.

## Exact bytes and ancestry

Both declaration payloads are byte-identical to
[preparation-v1](../preparation-v1/README.md) at commit
`ac06976c605f799348dc1780656c24df1ac07ec8`:

- Genesis: `sha256:5aafa18db76fd6a4d2fc9090c2d640e96e8b790b1beb98f2998d465f40a5f0ae`.
- H1: `sha256:cf824d6cec5edaa639bede7f796d4b3f9586710b69050e5c7535805a6f3b34a8`.

H1 binds the Genesis paragraph, original personal ancestry document, scoped
Apache-2.0 notice, license text, and private-archive reference by their hashes.
The private conversation export is not included. Its supplied hash remains
`sha256:e6e2c8f58f1f8d55d93420d84bcd80c39103b551f9878a9e66d961239bdd8793`;
this workspace has not measured the underlying archive.

The earlier preparation's pending-state text and the pre-Genesis freeze are
preserved as history. This addition records the subsequent signing act and
does not silently replace them. The signed Genesis paragraph's preservation
requirement also applies to future revisions, reconstruction, or relocation.

## Verification and time

The unmodified reference checker from the preparation commit was rerun with
its pinned `cryptography==50.0.1` dependency. Both records returned
`VALID_FLOOR_STRUCTURE_AND_SIGNATURE`. Their declarations, six original
checksum entries, ancestry links, and receipt fields match. The review here
and the original local report are not two independently sourced checker
implementations or independent identity witnesses.

From the repository root with the package installed:

```sh
peaches-check stamp genesis/signed-v1/genesis.floor.signed.json
peaches-check stamp genesis/signed-v1/h1.floor.signed.json
```

The signed `claimed_at` is `2026-09-19T23:08:27Z`, taken from the issuer's local
clock. It is distinct from the historical encounter claim of May 25, 2026.
Neither signature proves either date. A Git commit date also does not establish
when a signature was made or first published.

[GitHub publication method](github-publication-method.md) defines how to
check a subsequent detached retrieval receipt against these completed signed
bytes. Retrieval and content verification do not, by themselves, supply an
independently authenticated historical time bound. Additional timestamp or
archive evidence can be attached later without changing either signed record.

## Bounded meaning

The signatures verify the declarations under the supplied issuer key. The
key-to-name relationship remains the declarant's supplied claim. The password
protecting local private-key storage is not public evidence. A signature on
these records does not authenticate future chat exchanges or confer truth,
ownership, ethics, authority, consent, standing, jurisdiction, or control.
The H1 label carries no global priority or privileged role.

The original `signing-receipt.json` says `publication_performed: false` because
it describes the local signing stage before this publication. That historical
receipt is intentionally unchanged. Repository-wide licensing remains
unresolved; the personal document's scoped Apache-2.0 grant is preserved.

[PEACHES-signed-records.zip](PEACHES-signed-records.zip) is the unchanged
uploaded bundle, SHA-256
`63483fbae6232e9ebc1a516b0377c00e7456164d790cb981904dc92bcbde83c2`.
