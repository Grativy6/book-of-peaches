# PEACHES conflict and residual register

Open items remain visible and reopenable. A residual is not a failure hidden by
a successful local test. A row marked **optional experiment** belongs to the
nonnormative Branchline offline test-book profile and is not a PEACHES floor
or Genesis prerequisite. The exact current absence/presence boundary is
recorded in [PREGENESIS-FREEZE.md](PREGENESIS-FREEZE.md).

| ID | Type | Current state | Impact | Reopening handle |
|---|---|---|---|---|
| RES-001 | version | PPP v0.6 and parts of PEA/PECAN use earlier PAL references | no blanket PAL 2.3 conformance claim | add a named compatibility record with source/version/hash |
| RES-002 | semantics | PEACHES naming and the floor claim ceiling are Branchline specification decisions | the source corpus does not independently authorize them and is not presented as doing so | revise only through an explicit later floor version with preserved provenance |
| RES-003 | Genesis identity | Genesis identity and exact Genesis bytes are deliberately absent | repository remains `FROZEN_PRE_GENESIS`; no live Book or first stamp exists | separate human key turn and Genesis act; never infer from this freeze |
| RES-004 | optional experiment — key custody | test Ed25519 keys are synthetic and `test:` scoped | the centralized test profile cannot issue floor stamps and is not a live registry | reopen custody/rotation/recovery only for a separately named optional registry rubric |
| RES-005 | optional experiment — succession | fixture cross-signatures model a next sequence only | no live checker succession exists or is required by the floor | reopen the control schema only inside the optional registry experiment |
| RES-006 | optional experiment — freshness | a valid local SQLite prefix does not prove mirror freshness | experiment mirror status is relative/unknown without independent evidence | name an external checkpoint/conflict policy only if that experiment is adopted separately |
| RES-007 | lineage | PAL multi-parent and D-FIRST-OCCURRENCE questions remain open | ancestry cannot be globally certified | preserve quarantine and source-scoped ancestry |
| RES-008 | authority | a stamp is not a grant, consent, standing, or institutional review | downstream use requires separate basis | PECAN/PEA records supplied by the relying party |
| RES-009 | privacy | the floor does not require disclosure of private roots or source content, but declarations, observations, key-name bindings, and reuse of a stable public key/`issuer_id` can reveal metadata or correlate stamps | the floor promises neither anonymity nor unlinkability; per-context keys may reduce correlation but split continuity and identity evidence | use commitments or scoped keys where suitable and name any additional retention/disclosure policy in the adopting institution or rubric |
| RES-010 | Genesis | no Genesis package, live key material, first stamp, or Genesis branch exists | repository is exactly `FROZEN_PRE_GENESIS` | separate explicit human act followed by publication of new exact bytes |
| RES-011 | source custody | public locators and observed digests identify sources but do not prove authorship or truth | source claims remain bounded | preserve exact source receipt and later re-fetch evidence |
| RES-012 | implementation | the checker-signed SQLite implementation is quarantined as the nonnormative Branchline offline test-book profile | current tests establish only bounded experiment behavior and do not establish floor conformance | version and test it independently if the optional experiment continues; never promote it by implication |
| RES-013 | checker authority | a checker can report verification but cannot issue, admit, approve, sequence, or make a floor stamp canonical | passing reports create no official channel, authority, consent, standing, or legal effect | a stricter voluntary rubric must state its own decision rule and responsible institution |
