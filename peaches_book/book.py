"""EXPERIMENTAL/NONNORMATIVE centralized SQLite test registry.

This is a legacy, ``test:``-namespace-only implementation experiment.  It is
not the PEACHES floor, an official stamper or checker, or a source of authority.
The internal ``GENESIS:test:empty`` marker is only a chain sentinel; it is not a
PEACHES Genesis or an external trust anchor.
"""
from __future__ import annotations
import base64, json, os, sqlite3, threading, time
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from .core import canonical_bytes, digest, prepare_registration, sign_registration, verify_bundle, b64
from .profiles import signed_key_transition, verify_key_transition

_EXPORT_FIELDS={"schema","book_id","profile_id","checker_id","genesis_profile_id",
                "genesis_checker_id","controls","records","head"}

class TestSigner:
    __test__=False
    def __init__(self, seed: bytes=b"peaches-test-key-0000000000000000"):
        self.key=Ed25519PrivateKey.from_private_bytes(seed[:32].ljust(32,b"0"))
    @property
    def key_id(self): return "test:"+b64(self.key.public_key().public_bytes_raw())

class TestBook:
    """A transactional registry experiment constrained to test identities."""
    __test__=False
    def __init__(self, path, book_id="test:book/demo", profile_id="test:branchline-profile/0.1", signer=None):
        if not book_id.startswith("test:"): raise ValueError("TestBook requires test: book_id")
        self.path=Path(path); self.book_id=book_id; self.profile_id=profile_id; self.signer=signer or TestSigner(); self._lock=threading.RLock()
        self.path.parent.mkdir(parents=True,exist_ok=True); self._db=sqlite3.connect(self.path,check_same_thread=False,isolation_level=None)
        self._db.execute("PRAGMA busy_timeout=30000")
        # journal_mode conversion can return SQLITE_BUSY immediately even
        # with busy_timeout when independent processes open a new database.
        deadline=time.monotonic()+10
        while True:
            try:
                self._db.execute("PRAGMA journal_mode=WAL")
                break
            except sqlite3.OperationalError as exc:
                if (getattr(exc,"sqlite_errorcode",0) & 255) not in (sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED) or time.monotonic() >= deadline:
                    self._db.close()
                    raise
                time.sleep(0.02)
        self._db.execute("PRAGMA synchronous=FULL"); self._init()
    def _init(self):
        self._db.executescript("""CREATE TABLE IF NOT EXISTS metadata (k TEXT PRIMARY KEY,v TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS records (sequence INTEGER PRIMARY KEY, request_id TEXT NOT NULL, intent_hash TEXT NOT NULL, registration_id TEXT UNIQUE NOT NULL, previous_head TEXT NOT NULL, bundle TEXT NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS request_identity ON records(request_id,intent_hash);
        CREATE UNIQUE INDEX IF NOT EXISTS request_id_unique ON records(request_id);
        CREATE TABLE IF NOT EXISTS controls (sequence INTEGER PRIMARY KEY, control_json TEXT NOT NULL);""")
        vals={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
        expected={"book_id":self.book_id,"profile_id":self.profile_id,"checker_id":self.signer.key_id,
                  "genesis_profile_id":self.profile_id,"genesis_checker_id":self.signer.key_id,
                  "checker_status":"ACTIVE",
                  "genesis_descriptor":"test:genesis-template/0.1"}
        if not vals:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                vals={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
                if not vals: self._db.executemany("INSERT INTO metadata(k,v) VALUES(?,?)",expected.items())
                self._db.commit()
                vals={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
            except Exception:
                self._db.rollback(); raise
        if (any(vals.get(k)!=v for k,v in expected.items() if k not in ("genesis_profile_id","genesis_checker_id","checker_status"))
                or vals.get("checker_status") not in ("ACTIVE","COMPROMISED")):
            raise ValueError("test book metadata mismatch")
    def _rows(self): return [json.loads(x[0]) for x in self._db.execute("SELECT bundle FROM records ORDER BY sequence")]
    def _controls(self): return [json.loads(x[0]) for x in self._db.execute("SELECT control_json FROM controls ORDER BY sequence")]
    @staticmethod
    def _validate_control_chain(controls, rows, genesis_profile, genesis_checker, book_id, current_profile, current_checker):
        """Validate the full experiment control timeline, even with no records."""
        if (not isinstance(controls, list) or not isinstance(rows, list)
                or any(not isinstance(control, dict) for control in controls)
                or any(not isinstance(row, dict) for row in rows)):
            return False
        profile, checker = genesis_profile, genesis_checker
        previous_effective=0
        for control in controls:
            effective=control.get("effective_sequence")
            if (not isinstance(effective,int) or isinstance(effective,bool)
                    or effective <= previous_effective or effective > len(rows)+1
                    or not verify_key_transition(control)
                    or control.get("book_id") != book_id
                    or control.get("old_profile") != profile
                    or control.get("old_checker_id") != checker):
                return False
            expected_head=("GENESIS:test:empty" if effective==1 else rows[effective-2].get("registration_id"))
            if control.get("previous_head") != expected_head:
                return False
            previous_effective=effective
            profile, checker = control["new_profile"], control["new_checker_id"]
        return profile == current_profile and checker == current_checker
    @staticmethod
    def _timeline(sequence, controls, genesis_profile, genesis_checker, book_id=None):
        profile, checker = genesis_profile, genesis_checker
        seen=set()
        for control in sorted(controls, key=lambda c:c.get("effective_sequence",0)):
            effective=control.get("effective_sequence")
            if (not isinstance(effective,int) or effective < 1 or effective in seen
                    or not verify_key_transition(control)
                    or (book_id is not None and control.get("book_id") != book_id)
                    or control.get("old_profile") != profile
                    or control.get("old_checker_id") != checker):
                return None
            seen.add(effective)
            if effective <= sequence:
                profile, checker = control["new_profile"], control["new_checker_id"]
            else:
                break
        return profile, checker
    def _head(self):
        row=self._db.execute("SELECT sequence,registration_id FROM records ORDER BY sequence DESC LIMIT 1").fetchone()
        return (row[0],row[1]) if row else (0,"GENESIS:test:empty")
    def register(self,payload, fault=None):
        with self._lock:
            if "book_id" in payload and payload["book_id"] != self.book_id: return {"status":"BOOK_ID_CONFLICT"}
            if "profile_id" in payload and payload["profile_id"] != self.profile_id: return {"status":"PROFILE_ID_CONFLICT"}
            request_id=payload.get("request_id"); intent=prepare_registration({**payload,"book_id":self.book_id,"profile_id":self.profile_id,"issuer_id":payload.get("issuer_id","test:issuer")})["request_intent_hash"]
            self._db.execute("BEGIN IMMEDIATE")
            try:
                # The request lookup must occur after acquiring the database
                # write lock.  Otherwise independent processes can both see a
                # missing request and race into duplicate/conflicting inserts.
                old=self._db.execute("SELECT bundle,intent_hash FROM records WHERE request_id=?",(request_id,)).fetchone()
                if old:
                    self._db.rollback()
                    return {"status":"IDEMPOTENT_REPLAY" if old[1]==intent else "REQUEST_INTENT_CONFLICT","bundle":json.loads(old[0])}
                metadata={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
                if metadata["profile_id"]!=self.profile_id or metadata["checker_id"]!=self.signer.key_id:
                    self._db.rollback(); return {"status":"STALE_CHECKER"}
                if metadata.get("checker_status")!="ACTIVE":
                    self._db.rollback(); return {"status":"CHECKER_COMPROMISED"}
                seq,head=self._head()
                env=prepare_registration({**payload,"book_id":self.book_id,"profile_id":self.profile_id,"issuer_id":payload.get("issuer_id","test:issuer")},{"sequence":seq+1,"previous_head":head,"checker_id":self.signer.key_id,"checker_registered_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")})
                env["checker_registered_at"]=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
                env["registration_id"]=digest({k:env[k] for k in env if k!="registration_id"})
                bundle=sign_registration(env,self.signer.key,self.signer.key_id)
                if fault=="before_commit":
                    self._db.rollback(); return {"status":"UNKNOWN_BEFORE_COMMIT","request_id":request_id}
                self._db.execute("INSERT INTO records(sequence,request_id,intent_hash,registration_id,previous_head,bundle) VALUES(?,?,?,?,?,?)",(seq+1,request_id,env["request_intent_hash"],env["registration_id"],head,json.dumps(bundle,separators=(",",":"))))
                self._db.commit()
            except Exception:
                self._db.rollback(); raise
            if fault=="after_commit": return {"status":"UNKNOWN_AFTER_COMMIT","request_id":request_id}
            return {"status":"APPENDED_TEST_RECORD","bundle":bundle,"position":seq+1,"inclusion":env["registration_id"]}
    def recover_request(self, request_id, intent_hash=None):
        rows=self._db.execute("SELECT bundle,intent_hash FROM records WHERE request_id=?",(request_id,)).fetchall()
        if not rows: return {"status":"NOT_FOUND","request_id":request_id}
        if intent_hash is not None and any(r[1]!=intent_hash for r in rows): return {"status":"CONFLICT","request_id":request_id}
        if len(rows)>1: return {"status":"CONFLICT","request_id":request_id}
        return {"status":"FOUND","request_id":request_id,"bundle":json.loads(rows[0][0])}
    def mark_checker_compromised(self):
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                metadata={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
                if metadata["checker_id"]!=self.signer.key_id: self._db.rollback(); return {"status":"STALE_CHECKER"}
                self._db.execute("UPDATE metadata SET v='COMPROMISED' WHERE k='checker_status'")
                self._db.commit()
            except Exception:
                self._db.rollback(); raise
        return {"status":"CHECKER_COMPROMISED"}
    def verify(self):
        stored_rows=list(self._db.execute(
            "SELECT sequence,request_id,intent_hash,registration_id,previous_head,bundle "
            "FROM records ORDER BY sequence"
        ))
        stored_controls=list(self._db.execute(
            "SELECT sequence,control_json FROM controls ORDER BY sequence"
        ))
        rows=[]; controls=[]; storage_errors=[]
        for position,(sequence,request_id,intent_hash,registration_id,previous_head,encoded) in enumerate(stored_rows,1):
            try:
                row=json.loads(encoded)
            except (TypeError,ValueError):
                row=None
            if (not isinstance(row,dict) or sequence != position
                    or row.get("sequence") != sequence
                    or row.get("request_id") != request_id
                    or row.get("request_intent_hash") != intent_hash
                    or row.get("registration_id") != registration_id
                    or row.get("previous_head") != previous_head):
                storage_errors.append(f"record_storage_mismatch:{position}")
            rows.append(row)
        for position,(sequence,encoded) in enumerate(stored_controls,1):
            try:
                control=json.loads(encoded)
            except (TypeError,ValueError):
                control=None
            if (not isinstance(control,dict) or sequence != control.get("effective_sequence")):
                storage_errors.append(f"control_storage_mismatch:{position}")
            controls.append(control)
        prev="GENESIS:test:empty"; results=[]; ok=True
        metadata={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
        if storage_errors:
            return {"status":"INVALID_OR_CONFLICTING","count":len(stored_rows),"results":[],"head":prev,
                    "trust_source":"none_invalid_test_storage","errors":storage_errors,
                    "claim":"no_registration_claim"}
        if not self._validate_control_chain(controls,rows,metadata["genesis_profile_id"],metadata["genesis_checker_id"],self.book_id,metadata["profile_id"],metadata["checker_id"]):
            return {"status":"INVALID_OR_CONFLICTING","count":len(rows),"results":[],"head":prev,
                    "trust_source":"none_invalid_test_control_timeline","errors":["invalid_control_timeline"],
                    "claim":"no_registration_claim"}
        if not rows:
            if controls:
                return {"status":"EMPTY_TEST_BOOK_WITH_VALID_CONTROLS","count":0,"results":[],"head":prev,
                        "trust_source":"configured_test_anchor_and_verified_control_chain",
                        "claim":"test_control_timeline_only_no_registration"}
            return {"status":"EMPTY_TEST_BOOK","count":0,"results":[],"head":prev,
                    "trust_source":"none_unanchored_empty_test_store","claim":"no_registration_claim"}
        for n,row in enumerate(rows,1):
            timeline=self._timeline(n,controls,metadata["genesis_profile_id"],metadata["genesis_checker_id"],self.book_id)
            if timeline is None:
                ok=False; results.append({"status":"INVALID_REGISTRATION","errors":["invalid_control_timeline"],"claim":"no_registration_claim"}); prev=row.get("registration_id"); continue
            expected_profile, expected_checker=timeline
            result=verify_bundle(row,{"book_id":self.book_id,"profile_id":expected_profile,"checker_id":expected_checker,"sequence":n,"previous_head":prev,"inclusion":row.get("registration_id")})
            results.append(result); ok &= result["status"]=="VALID_UNDER_DECLARED_CONTEXT" and row.get("profile_id")==expected_profile and row.get("checker_id")==expected_checker and row.get("previous_head")==prev and row.get("sequence")==n; prev=row.get("registration_id")
        return {"status":"BOOK_LOCAL_VALIDATED" if ok else "INVALID_OR_CONFLICTING","count":len(rows),"results":results,"head":prev,"trust_source":"configured_test_anchor_and_verified_control_chain"}
    def apply_test_transition(self, new_profile, new_signer):
        """Apply a fixture-only cross-signed transition at the next sequence."""
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                metadata={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
                if metadata["profile_id"]!=self.profile_id or metadata["checker_id"]!=self.signer.key_id:
                    self._db.rollback(); return {"status":"STALE_CHECKER"}
                if metadata.get("checker_status") not in ("ACTIVE","COMPROMISED"):
                    self._db.rollback(); return {"status":"CHECKER_COMPROMISED"}
                seq,head=self._head()
                effective=seq+1
                record=signed_key_transition(self.profile_id,new_profile,self.signer,new_signer,effective,self.book_id,head)
                if not verify_key_transition(record): self._db.rollback(); return {"status":"TRANSITION_REJECTED"}
                self._db.execute("INSERT INTO controls(sequence,control_json) VALUES(?,?)",(effective,json.dumps(record,separators=(",",":"))))
                self._db.execute("UPDATE metadata SET v=? WHERE k=?",(new_profile,"profile_id"))
                self._db.execute("UPDATE metadata SET v=? WHERE k=?",(new_signer.key_id,"checker_id"))
                self._db.execute("UPDATE metadata SET v='ACTIVE' WHERE k='checker_status'")
                self._db.commit()
            except Exception:
                self._db.rollback(); raise
            self.profile_id=new_profile; self.signer=new_signer
            return {"status":"TEST_TRANSITION_APPLIED","effective_sequence":effective,"control":record}
    def inclusion(self, registration_id):
        row=self._db.execute("SELECT sequence,bundle FROM records WHERE registration_id=?",(registration_id,)).fetchone()
        if not row: return {"status":"NOT_INCLUDED"}
        checked=self.verify()
        if checked["status"]!="BOOK_LOCAL_VALIDATED": return {"status":"INCLUSION_UNVERIFIED","sequence":row[0],"registration_id":registration_id}
        return {"status":"BOOK_LOCAL_INCLUDED","sequence":row[0],"registration_id":registration_id,"head":checked["head"]}
    def export(self):
        metadata={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
        return {"schema":"peaches.test-book-export/0.2","book_id":self.book_id,"profile_id":metadata["profile_id"],"checker_id":metadata["checker_id"],"genesis_profile_id":metadata["genesis_profile_id"],"genesis_checker_id":metadata["genesis_checker_id"],"controls":self._controls(),"records":self._rows(),"head":self._head()[1]}
    def import_export(self, exported):
        if not isinstance(exported,dict): return {"status":"IMPORT_REJECTED","reason":"export_not_object"}
        if set(exported) != _EXPORT_FIELDS: return {"status":"IMPORT_REJECTED","reason":"export_fields_mismatch"}
        if exported.get("schema")!="peaches.test-book-export/0.2" or exported.get("book_id")!=self.book_id: return {"status":"IMPORT_REJECTED"}
        candidate=exported.get("records",[]); controls=exported.get("controls",[])
        if not isinstance(candidate,list): return {"status":"IMPORT_REJECTED","reason":"records_not_list"}
        if not isinstance(controls,list): return {"status":"IMPORT_REJECTED","reason":"controls_not_list"}
        if any(not isinstance(row,dict) for row in candidate): return {"status":"IMPORT_REJECTED","reason":"invalid_record"}
        if any(not isinstance(control,dict) for control in controls): return {"status":"IMPORT_REJECTED","reason":"invalid_transition"}
        if any(not verify_key_transition(c) for c in controls): return {"status":"IMPORT_REJECTED","reason":"invalid_transition"}
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                def stop(status, **fields):
                    self._db.rollback()
                    return {"status":status, **fields}

                # Every decision involving local state occurs after the write
                # lock.  This prevents two importers from validating the same
                # stale empty prefix and both reporting success.
                metadata={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
                local_rows=self._rows(); local_controls=self._controls()
                empty=not local_rows and not local_controls
                local_genesis=(metadata["genesis_profile_id"],metadata["genesis_checker_id"])
                exported_genesis=(exported.get("genesis_profile_id"),exported.get("genesis_checker_id"))
                if exported_genesis != local_genesis:
                    if not empty or exported.get("profile_id")!=self.profile_id or exported.get("checker_id")!=self.signer.key_id:
                        return stop("IMPORT_REJECTED",reason="genesis_anchor_mismatch")
                    genesis_profile,genesis_checker=exported_genesis
                else:
                    genesis_profile,genesis_checker=local_genesis
                if exported.get("profile_id")!=self.profile_id or exported.get("checker_id")!=self.signer.key_id:
                    return stop("IMPORT_REJECTED",reason="current_state_mismatch")

                if not self._validate_control_chain(controls,candidate,genesis_profile,genesis_checker,self.book_id,exported.get("profile_id"),exported.get("checker_id")):
                    return stop("IMPORT_REJECTED",reason="invalid_control_timeline")
                expected_head="GENESIS:test:empty"
                for n,row in enumerate(candidate,1):
                    if row.get("previous_head") != expected_head:
                        return stop("IMPORT_REJECTED",reason="chain_gap")
                    timeline=self._timeline(n,controls,genesis_profile,genesis_checker,self.book_id)
                    if timeline is None:
                        return stop("IMPORT_REJECTED",reason="untrusted_checker_timeline")
                    profile, checker=timeline
                    if row.get("profile_id")!=profile or row.get("checker_id")!=checker:
                        return stop("IMPORT_REJECTED",reason="untrusted_checker_timeline")
                    if verify_bundle(row,{"book_id":self.book_id,"profile_id":profile,"checker_id":checker,"sequence":n,"previous_head":expected_head,"inclusion":row.get("registration_id")})["status"]!="VALID_UNDER_DECLARED_CONTEXT":
                        return stop("IMPORT_REJECTED")
                    expected_head=row.get("registration_id")
                if exported.get("head") != expected_head:
                    return stop("IMPORT_REJECTED",reason="head_mismatch")

                if candidate[:len(local_rows)] != local_rows:
                    return stop("IMPORT_CONFLICT",reason="prefix_mismatch")
                if controls[:len(local_controls)] != local_controls:
                    return stop("IMPORT_CONFLICT",reason="control_prefix_mismatch")
                for row in candidate[len(local_rows):]:
                    old=self._db.execute("SELECT intent_hash,bundle FROM records WHERE request_id=?",(row["request_id"],)).fetchone()
                    if old and (old[0]!=row["request_intent_hash"] or old[1]!=json.dumps(row,separators=(",",":"))):
                        return stop("IMPORT_CONFLICT",request_id=row["request_id"])

                genesis_changed=exported_genesis != local_genesis
                if genesis_changed:
                    self._db.execute("UPDATE metadata SET v=? WHERE k='genesis_profile_id'",(genesis_profile,))
                    self._db.execute("UPDATE metadata SET v=? WHERE k='genesis_checker_id'",(genesis_checker,))
                controls_inserted=0
                for control in controls[len(local_controls):]:
                    encoded=json.dumps(control,separators=(",",":"))
                    self._db.execute("INSERT INTO controls(sequence,control_json) VALUES(?,?)",(control["effective_sequence"],encoded))
                    controls_inserted += 1
                inserted=0
                for row in candidate[len(local_rows):]:
                    seq=len(local_rows)+inserted+1
                    if row.get("sequence")!=seq:
                        return stop("IMPORT_REJECTED",reason="sequence_gap")
                    self._db.execute("INSERT INTO records VALUES(?,?,?,?,?,?)",(seq,row["request_id"],row["request_intent_hash"],row["registration_id"],row["previous_head"],json.dumps(row,separators=(",",":"))))
                    inserted += 1
                self._db.commit()
            except Exception:
                self._db.rollback(); raise
        if not (genesis_changed or controls_inserted or inserted):
            return {"status":"IDEMPOTENT_IMPORT","count":0,"controls":0}
        return {"status":"IMPORTED","count":inserted,"controls":controls_inserted}
    def _validate_export(self, exported):
        metadata={k:v for k,v in self._db.execute("SELECT k,v FROM metadata")}
        if (not isinstance(exported,dict) or set(exported) != _EXPORT_FIELDS
                or exported.get("schema")!="peaches.test-book-export/0.2" or exported.get("book_id")!=self.book_id
                or exported.get("profile_id")!=self.profile_id or exported.get("checker_id")!=self.signer.key_id):
            return False, "schema_or_identity"
        if exported.get("genesis_profile_id")!=metadata["genesis_profile_id"] or exported.get("genesis_checker_id")!=metadata["genesis_checker_id"]:
            return False, "genesis_anchor_mismatch"
        controls=exported.get("controls",[])
        if not isinstance(controls,list) or any(not verify_key_transition(c) for c in controls): return False, "invalid_transition"
        rows=exported.get("records")
        if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows):
            return False, "records_not_list"
        if not self._validate_control_chain(controls,rows,metadata["genesis_profile_id"],metadata["genesis_checker_id"],self.book_id,exported.get("profile_id"),exported.get("checker_id")):
            return False, "invalid_control_timeline"
        prev="GENESIS:test:empty"; seen_req=set(); seen_reg=set()
        for n,row in enumerate(rows,1):
            if not isinstance(row,dict) or row.get("sequence")!=n or row.get("previous_head")!=prev: return False, "chain_mismatch"
            if row.get("request_id") in seen_req or row.get("registration_id") in seen_reg: return False, "duplicate_identity"
            timeline=self._timeline(n,controls,metadata["genesis_profile_id"],metadata["genesis_checker_id"],self.book_id)
            if timeline is None: return False, "untrusted_checker_timeline"
            profile,checker=timeline
            if row.get("profile_id")!=profile or row.get("checker_id")!=checker: return False, "untrusted_checker_timeline"
            result=verify_bundle(row,{"book_id":self.book_id,"profile_id":profile,"checker_id":checker,"sequence":n,"previous_head":prev,"inclusion":row.get("registration_id")})
            if result["status"]!="VALID_UNDER_DECLARED_CONTEXT": return False, "invalid_record"
            seen_req.add(row.get("request_id")); seen_reg.add(row.get("registration_id")); prev=row.get("registration_id")
        if exported.get("head")!=prev: return False, "head_mismatch"
        return True, "ok"
    def mirror_status(self, exported):
        valid,reason=self._validate_export(exported)
        if not valid: return {"status":"INVALID_MIRROR","reason":reason,"freshness":"UNKNOWN"}
        local=self._rows(); remote=exported.get("records",[])
        if remote==local and exported.get("head")==self._head()[1]: return {"status":"CURRENT_RELATIVE_TO_BOUND_HEAD","freshness":"UNKNOWN_WITHOUT_SIGNED_CHECKPOINT"}
        if local[:len(remote)]==remote: return {"status":"STALE_MIRROR","freshness":"UNKNOWN_WITHOUT_SIGNED_CHECKPOINT"}
        if remote[:len(local)]==local: return {"status":"AHEAD_MIRROR","freshness":"UNKNOWN"}
        return {"status":"CONFLICTING_MIRROR","freshness":"UNKNOWN"}
