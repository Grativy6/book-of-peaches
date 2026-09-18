# Book of Peaches

Non-authoritative stamps for provenance.

This repository is the project home for the PEACHES stamp specification and offline book infrastructure. Version 0.1.0 supplies a working, local-only `peaches_book` package and a test-book CLI. It creates no Genesis, operational book, checker designation, or live stamp.

```powershell
python -m pip install -e .
python -m pytest -q
peaches-book verify .\temporary-test-book.sqlite
```

Read [CONTRACTS.md](CONTRACTS.md) for the common stamp API and Branchline profile boundary. [FOUNDING-PREGENESIS-TEMPLATE.md](FOUNDING-PREGENESIS-TEMPLATE.md) is deliberately incomplete: live identity, governance, keys and adoption remain human decisions.
