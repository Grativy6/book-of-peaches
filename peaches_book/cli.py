import argparse, json
from .book import TestBook
def main():
 p=argparse.ArgumentParser(description="PEACHES offline test-book checker")
 sub=p.add_subparsers(dest="cmd",required=True)
 v=sub.add_parser("verify"); v.add_argument("path")
 a=sub.add_parser("export"); a.add_argument("path")
 r=sub.add_parser("append"); r.add_argument("path"); r.add_argument("payload", help="JSON payload file")
 i=sub.add_parser("import"); i.add_argument("path"); i.add_argument("export_file")
 m=sub.add_parser("mirror"); m.add_argument("path"); m.add_argument("export_file")
 ns=p.parse_args(); book=TestBook(ns.path)
 if ns.cmd=="verify": out=book.verify()
 elif ns.cmd=="export": out=book.export()
 elif ns.cmd=="append": out=book.register(json.load(open(ns.payload,encoding="utf-8")))
 else:
  exported=json.load(open(ns.export_file,encoding="utf-8"))
  out=book.import_export(exported) if ns.cmd=="import" else book.mirror_status(exported)
 print(json.dumps(out, indent=2))

if __name__ == "__main__":
 main()
