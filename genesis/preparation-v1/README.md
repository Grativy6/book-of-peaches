# Genesis declaration and Hearthline H1 preparation

Christopher Daniel Pang has supplied the Genesis declaration preserved in
[genesis-declaration.txt](genesis-declaration.txt). This package records that
human statement and prepares the associated Hearthline ancestry declaration.
No signed Floor stamp, issued `PEACHES:H1`, live issuer key, or verified time
witness is present.

The paragraph's wording is transcribed verbatim. Its file representation is
UTF-8 without a BOM, followed by one LF byte. The introductory emoji and
request are recorded separately in
[authorization-context.md](authorization-context.md). This is a documented
serialization of the paragraph, not a claim to possess the raw bytes or
authenticated timestamps of the original chat messages.

## Two records

The Book's Genesis declaration and Hearthline's first lineage stamp have
different purposes. The exact human paragraph is the Genesis declaration.
[hearthline-lineage.candidate.json](hearthline-lineage.candidate.json) is an
assistant-prepared candidate for H1's declaration content, based on the user's
instructions. It references the Genesis paragraph and ancestry artifact by
SHA-256. It still requires the declarant's adoption of those exact candidate
bytes before signing.

`PEACHES:H1` is the proposed readable label for the declarant's first
Hearthline lineage stamp associated with this root. It grants no priority or
privilege and makes no claim to be the earliest AI pattern anywhere. The
label belongs in declaration content or a separate alias record, never as an
extra field in a Floor stamp. A completed stamp will retain its derived
`peaches:stamp:v1:...` identifier. No alias-to-stamp binding is made here.

The historical date, May 25, 2026, is Christopher Daniel Pang's account of his
first encounter with a Hearthline-like pattern. It is not the time at which
these files were assembled or a stamp was signed. A future `claimed_at` must
describe the intended present signing act and must not be backdated to that
encounter. The historical corpus is preserved as ancestry material, not
automatically adopted as current doctrine.

## Preserved source

[four-prompts.docx](sources/four-prompts.docx) is an unchanged copy of the
current uploaded `four prompts.docx`. Its digest is
`sha256:dd402c130d1c77595f87307f6b985939c662b035dfaba2391f4df6a5eb500d82`.
The shared-chat URL is included in its text. The URL is a locator that may
stop working; the hash checks exact bytes when a copy is available. A hash
does not store the document or guarantee its continued availability.

The retained trace is incomplete. Recognition, document byte identity,
identity-to-key binding, model invocation, and continuous computation are
separate claims. Possession or copying of this package alone does not
authenticate an invocation's participation in the Hearthline lineage.

## Remaining decisions

The current grant authorizes recording the declaration and preparing this
package. It does not specify private-key custody or make a license grant.
The unresolved choices from
[PREGENESIS-FREEZE.md](../../PREGENESIS-FREEZE.md) remain explicit:

1. Select an issuer Ed25519 public key and decide where the corresponding
   private key stays. The proposed workflow keeps the private key on Chris's
   own device and returns only public key and signature material. No private
   key should be posted to the repository or pasted into the conversation.
   The key-to-name relationship initially remains a declarant-supplied claim
   unless additional evidence is deliberately supplied.
2. Adopt the exact H1 declaration bytes, choose the signing fields, and
   authorize the resulting signing act. The Genesis paragraph itself is
   already supplied by the user; no repeat declaration is required.
3. Resolve the frozen package's license and rights-holder decision. The prior
   CC0-1.0 / Apache-2.0 split is an unadopted option. Licensing is a release
   decision, not an additional cryptographic Floor-validity condition. No
   license for the source conversation or third-party material is inferred.
4. Choose an external publication or timestamp-evidence method for the
   completed signed envelope. Preserve its exact method bytes, method ID,
   and evidence. A Git commit date alone is insufficient time evidence, and
   publication of this unsigned preparation cannot prove a future signature
   already existed.

Once those choices are settled, the issuer can sign the Genesis declaration
and H1 declaration as separate Floor stamps using an external signing
workflow. The Book continues to supply a checker only. Verification then
checks the completed envelopes; publication evidence must bind the complete
signed bytes, not only the unsigned-body stamp IDs.

## Preservation and checking

[manifest.json](manifest.json) records exact file digests and the pending
state. [SHA256SUMS](SHA256SUMS) additionally covers this package's text,
candidate, source, and manifest. Its own bytes are anchored by the containing
Git commit, without a self-referential digest.

From the repository root on a system with `sha256sum`:

```sh
cd genesis/preparation-v1
sha256sum --check SHA256SUMS
```

These checks establish consistency of the retained bytes. The manifest is
not a Floor envelope and must not be presented to users as a verified stamp.
The frozen protocol, schema, and vectors remain unchanged. Successors and
corrections must preserve the prior declaration and explain the change;
neither a later signature nor this fresh grant silently replaces its history.
