# GitHub commit retrieval method v1

Media type: `text/plain;charset=utf-8`.

The method ID is `derive_rubric_id(media_type, exact_method_file_bytes)` under
PEACHES Floor v1. This is an optional publication-evidence method for this
package, not an official Book service or mandatory stamp rubric.

## Evidence and checks

Evidence is a UTF-8 JSON receipt naming a repository, full commit hash, tree
hash, exact paths, byte lengths, and SHA-256 hashes of completed signed JSON
envelopes. It also names each envelope's Floor stamp ID and records the
retrieval workflow's local UTC observation time and the source of that time.

1. Retrieve the specified commit and file blobs from the named GitHub
   repository. Use the full commit hash, not a mutable branch or tag.
2. Confirm the commit's tree hash and compute the length and SHA-256 of each
   exact file blob. Require equality with the receipt. Hash the completed
   envelope bytes, including its signature, not just its unsigned-body ID.
3. Run a Floor checker on each retrieved envelope and require
   `VALID_FLOOR_STRUCTURE_AND_SIGNATURE` with the listed stamp ID.
4. Distinguish successful present retrieval and content verification from
   authentication of the receipt's historical observation time. Repeating
   retrieval later does not prove the earlier time claim.

The detached receipt is a publication report, not a Floor observation. It
does not supply an `observed_no_later_than` claim. This method supplies no
independent clock, signed hosting attestation, or timestamp authority. A
verifier must not report a verified no-later-than bound solely from this
receipt, Git author/committer dates, or a current successful download. An
authenticated time bound requires separate evidence and an explicitly
identified method that validates it.

## Limits and retention

Successful checks establish matching content retrieved from the named host
at the verifier's own observation, under that retrieval channel's trust
assumptions. GitHub can remove content; a URL or commit hash alone is not an
availability guarantee. Preserve copies of the exact records and receipt.

The receipt is an unsigned report by the publishing assistant workflow,
not a separate institutional witness or an issuer signature. Publication
does not prove creation time, firstness, declarant identity, originality,
ownership, legal effect, or authority. It does not change either signed
declaration or authorize future use of the signing key.
