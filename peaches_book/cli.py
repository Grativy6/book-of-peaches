"""CLI for the EXPERIMENTAL/NONNORMATIVE centralized test registry.

This command is not an official PEACHES checker and does not implement the
PEACHES floor.
"""
import argparse, json
from .book import TestBook

def main(argv=None):
 p=argparse.ArgumentParser(description="Experimental, nonnormative offline test-registry checker")
 sub=p.add_subparsers(dest="cmd",required=True)
 v=sub.add_parser("verify"); v.add_argument("path")
 a=sub.add_parser("export"); a.add_argument("path")
 r=sub.add_parser("append"); r.add_argument("path"); r.add_argument("payload", help="JSON payload file")
 i=sub.add_parser("import"); i.add_argument("path"); i.add_argument("export_file")
 m=sub.add_parser("mirror"); m.add_argument("path"); m.add_argument("export_file")
 ns=p.parse_args(argv); book=TestBook(ns.path)
 if ns.cmd=="verify": out=book.verify()
 elif ns.cmd=="export": out=book.export()
 elif ns.cmd=="append": out=book.register(json.load(open(ns.payload,encoding="utf-8")))
 else:
  with open(ns.export_file,encoding="utf-8") as stream:
   exported=json.load(stream)
  out=book.import_export(exported) if ns.cmd=="import" else book.mirror_status(exported)
 print(json.dumps(out, indent=2))
 if ns.cmd=="verify": return 0 if out.get("status")=="BOOK_LOCAL_VALIDATED" else 1
 if ns.cmd=="append": return 0 if out.get("status") in {"APPENDED_TEST_RECORD","IDEMPOTENT_REPLAY"} else 1
 if ns.cmd=="import": return 0 if out.get("status") in {"IMPORTED","IDEMPOTENT_IMPORT"} else 1
 if ns.cmd=="mirror": return 0 if out.get("status") in {"CURRENT_RELATIVE_TO_BOUND_HEAD","STALE_MIRROR","AHEAD_MIRROR"} else 1
 return 0

if __name__ == "__main__":
 raise SystemExit(main())
