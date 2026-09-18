# PEACHES conflict and residual register

Open items remain visible and reopenable. A residual is not a failure hidden by a successful local test.

| ID | Type | Current state | Impact | Reopening handle |
|---|---|---|---|---|
| RES-001 | version | PPP v0.6 and parts of PEA/PECAN use earlier PAL references | no blanket PAL 2.3 conformance claim | add a named compatibility record with source/version/hash |
| RES-002 | semantics | PEACHES naming and public claim ceiling are Branchline decisions | source corpus does not independently authorize them | human adoption checklist in founding template |
| RES-003 | identity | book ID, profile ID, checker designation, and founding identity are unset | no live book can be created | fill exact fields and re-run package review |
| RES-004 | key custody | test Ed25519 keys are synthetic and `test:` scoped | cannot issue live stamps | adopt custody, rotation, compromise, and recovery policy |
| RES-005 | succession | fixture cross-signatures model a next sequence only | no live checker succession exists | adopt control record schema and activation procedure |
| RES-006 | freshness | a valid local prefix does not prove mirror freshness | mirror status is relative/unknown without an independent checkpoint | adopt checkpoint source and conflict policy |
| RES-007 | lineage | PAL multi-parent and D-FIRST-OCCURRENCE questions remain open | ancestry cannot be globally certified | preserve quarantine and source-scoped ancestry |
| RES-008 | authority | a stamp is not a grant, consent, standing, or institutional review | downstream use requires separate basis | PECAN/PEA records supplied by the relying party |
| RES-009 | privacy | public fields and metadata minimization are not adopted | private roots/ledgers must not leak through a stamp | adopt disclosure and retention policy |
| RES-010 | Genesis | no Genesis package, key, or branch exists | repository is pre-Genesis | separate human approval followed by mechanical emission |
| RES-011 | source custody | public locators and observed digests identify sources but do not prove authorship or truth | source claims remain bounded | preserve exact source receipt and later re-fetch evidence |
| RES-012 | implementation | offline SQLite/Ed25519 choices are replaceable engineering decisions | current tests establish only bounded fixture behavior | version protocol and migration rules before live adoption |
