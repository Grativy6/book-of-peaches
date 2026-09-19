import json
import pytest
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from peaches_book import TestBook, TestSigner, prepare_registration, verify_bundle, transition, signed_key_transition, verify_key_transition
from peaches_book.core import b64, sign_registration
from peaches_book.core import PeachesError
from peaches_book.cli import main as cli_main

def payload(request="test:req/1", value="hello"):
    return {"profile_id":"test:branchline-profile/0.1", "object":{"value":value}, "request_id":request, "observed_at":"2026-09-17T00:00:00Z", "issuer_id":"test:issuer/demo"}

def process_register(args):
    path, request = args
    return TestBook(path).register(payload(request))["status"]

def process_register_intent(args):
    path, request, value = args
    return TestBook(path).register(payload(request, value))["status"]

def process_import(args):
    path, exported = args
    return TestBook(path).import_export(exported)["status"]

def test_append_chain_inclusion_and_idempotent(tmp_path):
    b=TestBook(tmp_path/"book.sqlite")
    first=b.register(payload()); assert first["status"]=="APPENDED_TEST_RECORD"
    again=b.register(payload()); assert again["status"]=="IDEMPOTENT_REPLAY"
    assert b.inclusion(first["bundle"]["registration_id"])["status"]=="BOOK_LOCAL_INCLUDED"
    assert b.verify()["status"]=="BOOK_LOCAL_VALIDATED"

def test_changed_payload_and_new_request_are_distinct(tmp_path):
    b=TestBook(tmp_path/"book.sqlite"); first=b.register(payload())
    assert b.register(payload(value="changed"))["status"]=="REQUEST_INTENT_CONFLICT"
    second=b.register(payload(request="test:req/2")); assert second["status"]=="APPENDED_TEST_RECORD"
    assert second["bundle"]["registration_id"] != first["bundle"]["registration_id"]

def test_tamper_and_wrong_checker_context_detected(tmp_path):
    b=TestBook(tmp_path/"book.sqlite"); b.register(payload())
    row=b.export()["records"][0]; row["object"]["value"]="tampered"
    assert verify_bundle(row, {"book_id":b.book_id,"profile_id":b.profile_id,"checker_id":b.signer.key_id,"sequence":1,"previous_head":"GENESIS:test:empty","inclusion":row["registration_id"]})["status"]=="INVALID_REGISTRATION"
    assert b.mirror_status({"schema":"peaches.test-book-export/0.2","book_id":"test:other","profile_id":b.profile_id,"records":[]})["status"]=="INVALID_MIRROR"

@pytest.mark.parametrize(("column","value"),[
    ("sequence",2),
    ("request_id","test:req/tampered"),
    ("intent_hash","sha256:tampered"),
    ("registration_id","sha256:tampered"),
    ("previous_head","sha256:tampered"),
])
def test_verify_rejects_redundant_record_column_tampering(tmp_path,column,value):
    book=TestBook(tmp_path/f"column-{column}.sqlite")
    book.register(payload())
    book._db.execute(f"UPDATE records SET {column}=? WHERE request_id=?",(value,"test:req/1"))
    result=book.verify()
    assert result["status"]=="INVALID_OR_CONFLICTING"
    assert result["trust_source"]=="none_invalid_test_storage"

def test_verify_rejects_control_column_tampering(tmp_path):
    book=TestBook(tmp_path/"control-column.sqlite")
    successor=TestSigner(b"control-column-successor"*2)
    book.apply_test_transition("test:p2",successor)
    book._db.execute("UPDATE controls SET sequence=2 WHERE sequence=1")
    result=book.verify()
    assert result["status"]=="INVALID_OR_CONFLICTING"
    assert result["trust_source"]=="none_invalid_test_storage"

def test_foreign_checker_cannot_self_anchor(tmp_path):
    b=TestBook(tmp_path/'book.sqlite'); first=b.register(payload())['bundle']; foreign=TestSigner(b'foreign'*5)
    forged=dict(first); forged['checker_id']=foreign.key_id; forged['signature']=None
    forged['signature']={"algorithm":"Ed25519","key_id":foreign.key_id,"value":""}
    b._db.execute("UPDATE records SET bundle=? WHERE sequence=1",(json.dumps(forged,separators=(',',':')),))
    assert b.verify()['status']=='INVALID_OR_CONFLICTING'

def test_signature_key_must_match_bundle_and_context_checker(tmp_path):
    b=TestBook(tmp_path/"checker-binding.sqlite")
    bundle=b.register(payload())["bundle"]
    foreign=TestSigner(b"foreign-checker"*3)
    mismatched=sign_registration({k:v for k,v in bundle.items() if k!="signature"}, foreign.key, foreign.key_id)
    unanchored=verify_bundle(mismatched)
    assert unanchored["status"]=="INVALID_REGISTRATION"
    assert "checker_signature_key_mismatch" in unanchored["errors"]
    declared={"book_id":b.book_id,"profile_id":b.profile_id,"checker_id":foreign.key_id,
              "sequence":1,"previous_head":"GENESIS:test:empty","inclusion":bundle["registration_id"]}
    anchored=verify_bundle(mismatched,declared)
    assert anchored["status"]=="INVALID_REGISTRATION"
    assert "checker_signature_key_mismatch" in anchored["errors"]
    assert "checker_role_mismatch" in anchored["errors"]

def test_experiment_signature_object_rejects_unsigned_authority_metadata(tmp_path):
    book=TestBook(tmp_path/"signature-shape.sqlite")
    bundle=book.register(payload())["bundle"]
    bundle["signature"]["authority"]="LIVE_OFFICIAL"
    result=verify_bundle(bundle)
    assert result["status"]=="INVALID_REGISTRATION"
    assert result["errors"]==["signature_fields_mismatch"]

def test_experiment_signature_rejects_noncanonical_base64url(tmp_path):
    book=TestBook(tmp_path/"signature-base64.sqlite")
    bundle=book.register(payload())["bundle"]
    bundle["signature"]["value"] += "="
    result=verify_bundle(bundle)
    assert result["status"]=="INVALID_REGISTRATION"
    assert result["errors"]==["noncanonical_base64url"]

def test_experiment_verifier_rejects_identity_key_universal_forgery():
    identity=b"\x01"+b"\x00"*31
    checker_id="test:"+b64(identity)
    context={"sequence":1,"previous_head":"GENESIS:test:empty","checker_id":checker_id,
             "checker_registered_at":"2026-09-17T00:00:01Z"}
    envelope=prepare_registration({**payload(),"book_id":"test:book/demo"},context)
    forged={**envelope,"signature":{"algorithm":"Ed25519","key_id":checker_id,
                                     "value":b64(identity+b"\x00"*32)}}
    result=verify_bundle(forged)
    assert result["status"]=="INVALID_REGISTRATION"
    assert any("identity_not_permitted" in error for error in result["errors"])

def test_unanchored_signature_is_not_registration(tmp_path):
    b=TestBook(tmp_path/"book.sqlite"); row=b.register(payload())["bundle"]
    assert verify_bundle(row)["status"]=="SIGNATURE_VALID_UNANCHORED"

def test_namespaces_and_canonical_limits():
    try: prepare_registration({**payload(),"book_id":"live:book"})
    except PeachesError: pass
    else: assert False
    for bad in ({"n":2**60}, {"n":1.2}, {"x":{"y":{"z":1}}}):
        if bad=={"x":{"y":{"z":1}}}: continue
        try: prepare_registration({**payload(),"object":bad})
        except PeachesError: pass
        else: assert False

def test_export_import_and_mirror_states(tmp_path):
    source=TestBook(tmp_path/"source.sqlite"); source.register(payload())
    target=TestBook(tmp_path/"target.sqlite")
    exported=source.export(); assert target.mirror_status(exported)["status"]=="AHEAD_MIRROR"
    assert target.import_export(exported)["status"]=="IMPORTED"
    assert target.mirror_status(exported)["status"]=="CURRENT_RELATIVE_TO_BOUND_HEAD"
    assert target.mirror_status({"schema":"peaches.test-book-export/0.2","book_id":target.book_id,"profile_id":target.profile_id,"records":["garbage"],"head":"x"})["status"]=="INVALID_MIRROR"

def test_concurrent_checker_calls_preserve_chain(tmp_path):
    b=TestBook(tmp_path/"book.sqlite")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda i: b.register(payload(request=f"test:req/{i}")), range(8)))
    assert sum(r["status"]=="APPENDED_TEST_RECORD" for r in results)==8
    assert b.verify()["count"]==8

def test_profile_transition_requires_named_successor(tmp_path):
    old={"book_id":"test:b","profile_id":"test:p/0.1","schema":"peaches.registration/0.2"}
    assert transition(old,old)["status"]=="COMPATIBLE_PROFILE"
    assert transition(old,{**old,"profile_id":"test:p/0.2"})["status"]=="INCOMPATIBLE_SUCCESSOR_REQUIRED"
    record=signed_key_transition("test:p/0.1","test:p/0.2",TestSigner(b"a"*32),TestSigner(b"b"*32),2,"test:b","sha256:"+"0"*64)
    assert verify_key_transition(record)
    record["new_signature"]="bad"
    assert not verify_key_transition(record)
    b=TestBook(tmp_path/'transition.sqlite')
    b.register(payload('test:before'))
    new_signer=TestSigner(b'c'*32)
    assert b.apply_test_transition('test:branchline-profile/0.2',new_signer)['status']=='TEST_TRANSITION_APPLIED'
    assert b.register({**payload('test:after'), 'profile_id':'test:branchline-profile/0.2'})['status']=='APPENDED_TEST_RECORD'
    assert b.verify()['status']=='BOOK_LOCAL_VALIDATED'
    exported=b.export(); mirror=TestBook(tmp_path/'mirror.sqlite',profile_id='test:branchline-profile/0.2',signer=new_signer)
    assert mirror.import_export(exported)['status']=='IMPORTED'
    assert mirror.verify()['status']=='BOOK_LOCAL_VALIDATED'
    restarted=TestBook(tmp_path/'mirror.sqlite',profile_id='test:branchline-profile/0.2',signer=new_signer)
    assert restarted.verify()['status']=='BOOK_LOCAL_VALIDATED'

def test_key_transition_requires_exact_schema_and_signed_binding_fields():
    old=TestSigner(b"d"*32); new=TestSigner(b"e"*32)
    record=signed_key_transition("test:p/0.1","test:p/0.2",old,new,1,"test:book","GENESIS:test:empty")
    for mutation in (
        {**record,"schema":"peaches.key-transition/999"},
        {k:v for k,v in record.items() if k!="book_id"},
        {k:v for k,v in record.items() if k!="previous_head"},
        {**record,"unsigned_extension":"not-allowed"},
    ):
        assert not verify_key_transition(mutation)
    try:
        signed_key_transition("test:p/0.1","test:p/0.2",old,new,1)
    except PeachesError: pass
    else: assert False

def test_key_transition_rejects_identity_key_universal_forgery():
    identity=b"\x01"+b"\x00"*31
    checker_id="test:"+b64(identity)
    identity_signature=b64(identity+b"\x00"*32)
    forged={"schema":"peaches.key-transition/0.1","book_id":"test:book",
            "previous_head":"GENESIS:test:empty","old_profile":"test:p/0.1",
            "new_profile":"test:p/0.2","old_checker_id":checker_id,
            "new_checker_id":checker_id,"effective_sequence":1,
            "old_signature":identity_signature,"new_signature":identity_signature}
    assert not verify_key_transition(forged)

def test_key_transition_rejects_noncanonical_base64url():
    old=TestSigner(b"canonical-old"*3); new=TestSigner(b"canonical-new"*3)
    record=signed_key_transition("test:p/0.1","test:p/0.2",old,new,1,"test:book","GENESIS:test:empty")
    record["old_signature"] += "=="
    assert not verify_key_transition(record)

def test_recovery_before_and_after_commit(tmp_path):
    b=TestBook(tmp_path/"book.sqlite")
    p=payload("test:recover")
    assert b.register(p, fault="before_commit")["status"]=="UNKNOWN_BEFORE_COMMIT"
    assert b.recover_request("test:recover")["status"]=="NOT_FOUND"
    assert b.register(p, fault="after_commit")["status"]=="UNKNOWN_AFTER_COMMIT"
    assert b.recover_request("test:recover")["status"]=="FOUND"

def test_full_intent_binds_external_stamp_and_book(tmp_path):
    b=TestBook(tmp_path/"intent.sqlite")
    original={**payload(), "institution_stamp":{"external_book":"test:institution","stamp":"test:s1"}}
    assert b.register(original)["status"]=="APPENDED_TEST_RECORD"
    changed={**original, "institution_stamp":{"external_book":"test:institution","stamp":"test:s2"}}
    assert b.register(changed)["status"]=="REQUEST_INTENT_CONFLICT"

def test_signed_noncanonical_schema_claim_or_intent_is_rejected(tmp_path):
    b=TestBook(tmp_path/"canonical.sqlite")
    bundle=b.register(payload())["bundle"]
    for field,value in (("schema","other/schema"),("claim_ceiling","grants_authority"),("request_intent_hash","fake"),("unknown_field","unbound")):
        changed={**bundle,field:value}
        signed=sign_registration({k:v for k,v in changed.items() if k!="signature"}, b.signer.key,b.signer.key_id)
        assert verify_bundle(signed)["status"]=="INVALID_REGISTRATION"

def test_stale_writer_cannot_append_but_can_replay_existing_request(tmp_path):
    live=TestBook(tmp_path/"stale.sqlite"); stale=TestBook(tmp_path/"stale.sqlite")
    first=live.register(payload("test:stale")); assert first["status"]=="APPENDED_TEST_RECORD"
    assert live.apply_test_transition("test:branchline-profile/0.2",TestSigner(b"z"*32))["status"]=="TEST_TRANSITION_APPLIED"
    assert stale.register(payload("test:new"))["status"]=="STALE_CHECKER"
    assert stale.register(payload("test:stale"))["status"]=="IDEMPOTENT_REPLAY"

def test_multiple_transition_replay_and_successor_import(tmp_path):
    book=TestBook(tmp_path/"multi.sqlite")
    book.register(payload("test:a")); s2=TestSigner(b"b"*32); s3=TestSigner(b"c"*32)
    book.apply_test_transition("test:p2",s2)
    book.register({**payload("test:b"),"profile_id":"test:p2"})
    book.apply_test_transition("test:p3",s3)
    book.register({**payload("test:c"),"profile_id":"test:p3"})
    assert book.verify()["status"]=="BOOK_LOCAL_VALIDATED"
    exported=book.export(); mirror=TestBook(tmp_path/"mirror.sqlite",profile_id="test:p3",signer=s3)
    assert mirror.import_export(exported)["status"]=="IMPORTED"
    assert mirror.verify()["status"]=="BOOK_LOCAL_VALIDATED"

def test_compromised_checker_freezes_append_until_cross_signed_recovery(tmp_path):
    book=TestBook(tmp_path/"compromised.sqlite")
    assert book.mark_checker_compromised()["status"]=="CHECKER_COMPROMISED"
    assert book.register(payload("test:frozen"))["status"]=="CHECKER_COMPROMISED"
    successor=TestSigner(b"successor"*4)
    assert book.apply_test_transition("test:branchline-profile/0.2",successor)["status"]=="TEST_TRANSITION_APPLIED"
    assert book.register({**payload("test:recovered"),"profile_id":"test:branchline-profile/0.2"})["status"]=="APPENDED_TEST_RECORD"

def test_compromised_experiment_can_restart_before_cross_signed_recovery(tmp_path):
    path=tmp_path/"compromised-restart.sqlite"
    original=TestBook(path)
    assert original.mark_checker_compromised()["status"]=="CHECKER_COMPROMISED"
    reopened=TestBook(path)
    assert reopened.register(payload("test:still-frozen"))["status"]=="CHECKER_COMPROMISED"
    successor=TestSigner(b"restart-successor"*2)
    assert reopened.apply_test_transition("test:branchline-profile/0.2",successor)["status"]=="TEST_TRANSITION_APPLIED"
    assert reopened.register({**payload("test:after-restart"),"profile_id":"test:branchline-profile/0.2"})["status"]=="APPENDED_TEST_RECORD"

def test_independent_process_writers_preserve_chain(tmp_path):
    path=str(tmp_path/"process.sqlite")
    with ProcessPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(process_register, [(path,f"test:process/{i}") for i in range(6)]))
    assert set(results) <= {"APPENDED_TEST_RECORD","HEAD_CHANGED_RETRY"}
    book=TestBook(path)
    assert book.verify()["status"]=="BOOK_LOCAL_VALIDATED"
    assert book.verify()["count"]==results.count("APPENDED_TEST_RECORD")

def test_independent_process_same_request_is_transactionally_idempotent(tmp_path):
    path=str(tmp_path/"same-request.sqlite")
    args=[(path,"test:shared","same") for _ in range(8)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(process_register_intent,args))
    assert results.count("APPENDED_TEST_RECORD")==1
    assert results.count("IDEMPOTENT_REPLAY")==7
    book=TestBook(path)
    assert book.verify()["status"]=="BOOK_LOCAL_VALIDATED"
    assert book.verify()["count"]==1

def test_independent_process_same_request_conflicting_intents_are_rejected(tmp_path):
    path=str(tmp_path/"conflicting-request.sqlite")
    args=[(path,"test:shared",f"value-{i}") for i in range(8)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(process_register_intent,args))
    assert results.count("APPENDED_TEST_RECORD")==1
    assert results.count("REQUEST_INTENT_CONFLICT")==7
    book=TestBook(path)
    assert book.verify()["status"]=="BOOK_LOCAL_VALIDATED"
    assert book.verify()["count"]==1

def test_empty_book_is_explicitly_unanchored(tmp_path):
    result=TestBook(tmp_path/"empty.sqlite").verify()
    assert result["status"]=="EMPTY_TEST_BOOK"
    assert result["claim"]=="no_registration_claim"
    assert result["trust_source"]=="none_unanchored_empty_test_store"

def test_empty_book_validates_or_rejects_full_control_timeline(tmp_path):
    book=TestBook(tmp_path/"empty-controls.sqlite")
    successor=TestSigner(b"empty-successor"*3)
    assert book.apply_test_transition("test:p2",successor)["status"]=="TEST_TRANSITION_APPLIED"
    assert book.verify()["status"]=="EMPTY_TEST_BOOK_WITH_VALID_CONTROLS"
    bad=signed_key_transition("test:p2","test:p3",successor,TestSigner(b"future"*6),2,
                              book.book_id,"GENESIS:test:empty")
    book._db.execute("INSERT INTO controls(sequence,control_json) VALUES(?,?)",
                     (2,json.dumps(bad,separators=(",",":"))))
    assert book.verify()["status"]=="INVALID_OR_CONFLICTING"

def test_import_rejects_non_object_without_crashing(tmp_path):
    book=TestBook(tmp_path/"import.sqlite")
    for exported in (None,[]):
        result=book.import_export(exported)
        assert result["status"]=="IMPORT_REJECTED"
        assert result["reason"]=="export_not_object"

def test_concurrent_identical_import_is_exactly_idempotent(tmp_path):
    source=TestBook(tmp_path/"source-identical.sqlite")
    source.register(payload("test:import-identical"))
    exported=source.export(); target=str(tmp_path/"target-identical.sqlite")
    with ProcessPoolExecutor(max_workers=2) as pool:
        statuses=list(pool.map(process_import,[(target,exported),(target,exported)]))
    assert sorted(statuses)==["IDEMPOTENT_IMPORT","IMPORTED"]
    assert TestBook(target).export()["records"]==exported["records"]

def test_concurrent_conflicting_import_never_reports_false_idempotence(tmp_path):
    first=TestBook(tmp_path/"source-a.sqlite"); first.register(payload("test:import-a","a"))
    second=TestBook(tmp_path/"source-b.sqlite"); second.register(payload("test:import-b","b"))
    exports=[first.export(),second.export()]; target=str(tmp_path/"target-conflict.sqlite")
    with ProcessPoolExecutor(max_workers=2) as pool:
        statuses=list(pool.map(process_import,[(target,exports[0]),(target,exports[1])]))
    assert statuses.count("IMPORTED")==1
    assert statuses.count("IMPORT_CONFLICT")==1
    assert "IDEMPOTENT_IMPORT" not in statuses
    rows=TestBook(target).export()["records"]
    assert rows in ([exports[0]["records"],exports[1]["records"]])

def test_control_only_export_rejects_duplicate_or_discontinuous_timeline(tmp_path):
    old=TestSigner(); second=TestSigner(b"second"*6); third=TestSigner(b"third"*7)
    first_control=signed_key_transition("test:branchline-profile/0.1","test:p2",old,second,1,"test:book/demo","GENESIS:test:empty")
    duplicate_control=signed_key_transition("test:p2","test:p3",second,third,1,"test:book/demo","GENESIS:test:empty")
    exported={"schema":"peaches.test-book-export/0.2","book_id":"test:book/demo",
              "profile_id":"test:p3","checker_id":third.key_id,
              "genesis_profile_id":"test:branchline-profile/0.1",
              "genesis_checker_id":old.key_id,"controls":[first_control,duplicate_control],
              "records":[],"head":"GENESIS:test:empty"}
    target=TestBook(tmp_path/"control-only.sqlite",profile_id="test:p3",signer=third)
    result=target.import_export(exported)
    assert result=={"status":"IMPORT_REJECTED","reason":"invalid_control_timeline"}
    assert target.mirror_status(exported)["status"]=="INVALID_MIRROR"

def test_valid_control_only_import_reports_mutation_then_exact_idempotence(tmp_path):
    source=TestBook(tmp_path/"control-source.sqlite")
    successor=TestSigner(b"control-successor"*2)
    assert source.apply_test_transition("test:p2",successor)["status"]=="TEST_TRANSITION_APPLIED"
    exported=source.export()
    target=TestBook(tmp_path/"control-target.sqlite",profile_id="test:p2",signer=successor)
    first=target.import_export(exported)
    assert first["status"]=="IMPORTED" and first["count"]==0 and first["controls"]==1
    assert target.import_export(exported)["status"]=="IDEMPOTENT_IMPORT"
    assert target.verify()["status"]=="EMPTY_TEST_BOOK_WITH_VALID_CONTROLS"

def test_empty_export_into_identical_empty_book_is_idempotent(tmp_path):
    source=TestBook(tmp_path/"empty-source.sqlite")
    target=TestBook(tmp_path/"empty-target.sqlite")
    assert target.import_export(source.export())=={
        "status":"IDEMPOTENT_IMPORT","count":0,"controls":0
    }

def test_mirror_status_rejects_nondict_rows_without_crashing(tmp_path):
    source=TestBook(tmp_path/"row-source.sqlite")
    successor=TestSigner(b"row-successor"*3)
    source.apply_test_transition("test:p2",successor)
    exported=source.export()
    exported["records"]=["not-an-object"]
    exported["head"]="not-an-object"
    target=TestBook(tmp_path/"row-target.sqlite",profile_id="test:p2",signer=successor)
    assert target.mirror_status(exported)["status"]=="INVALID_MIRROR"

def test_export_wrapper_rejects_authority_shaped_extra_fields(tmp_path):
    source=TestBook(tmp_path/"export-source.sqlite"); exported=source.export()
    exported["official_authority"]=True
    target=TestBook(tmp_path/"export-target.sqlite")
    assert target.import_export(exported)=={"status":"IMPORT_REJECTED","reason":"export_fields_mismatch"}
    assert target.mirror_status(exported)["status"]=="INVALID_MIRROR"

def test_cli_returns_nonzero_for_empty_or_invalid_verification(tmp_path,capsys):
    path=tmp_path/"cli.sqlite"; book=TestBook(path)
    assert cli_main(["verify",str(path)])==1
    book.register(payload())
    assert cli_main(["verify",str(path)])==0
    row=book.export()["records"][0]; row["object"]["value"]="tampered"
    book._db.execute("UPDATE records SET bundle=? WHERE sequence=1",(json.dumps(row,separators=(",",":")),))
    assert cli_main(["verify",str(path)])==1
    capsys.readouterr()
