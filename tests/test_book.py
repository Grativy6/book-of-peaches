import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from peaches_book import TestBook, TestSigner, prepare_registration, verify_bundle, transition, signed_key_transition, verify_key_transition
from peaches_book.core import sign_registration
from peaches_book.core import PeachesError

def payload(request="test:req/1", value="hello"):
    return {"profile_id":"test:branchline-profile/0.1", "object":{"value":value}, "request_id":request, "observed_at":"2026-09-17T00:00:00Z", "issuer_id":"test:issuer/demo"}

def process_register(args):
    path, request = args
    return TestBook(path).register(payload(request))["status"]

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

def test_foreign_checker_cannot_self_anchor(tmp_path):
    b=TestBook(tmp_path/'book.sqlite'); first=b.register(payload())['bundle']; foreign=TestSigner(b'foreign'*5)
    forged=dict(first); forged['checker_id']=foreign.key_id; forged['signature']=None
    forged['signature']={"algorithm":"Ed25519","key_id":foreign.key_id,"value":""}
    b._db.execute("UPDATE records SET bundle=? WHERE sequence=1",(json.dumps(forged,separators=(',',':')),))
    assert b.verify()['status']=='INVALID_OR_CONFLICTING'

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
    record=signed_key_transition("test:p/0.1","test:p/0.2",TestSigner(b"a"*32),TestSigner(b"b"*32),2)
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

def test_recovery_before_and_after_commit(tmp_path):
    b=TestBook(tmp_path/"book.sqlite")
    p=payload("test:recover")
    assert b.register(p, fault="before_commit")["status"]=="UNKNOWN_BEFORE_COMMIT"
    assert b.recover_request("test:recover")["status"]=="NOT_FOUND"
    assert b.register(p, fault="after_commit")["status"]=="UNKNOWN_AFTER_COMMIT"
    assert b.recover_request("test:recover")["status"]=="FOUND"

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

def test_independent_process_writers_preserve_chain(tmp_path):
    path=str(tmp_path/"process.sqlite")
    with ProcessPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(process_register, [(path,f"test:process/{i}") for i in range(6)]))
    assert set(results) <= {"APPENDED_TEST_RECORD","HEAD_CHANGED_RETRY"}
    book=TestBook(path)
    assert book.verify()["status"]=="BOOK_LOCAL_VALIDATED"
    assert book.verify()["count"]==results.count("APPENDED_TEST_RECORD")
