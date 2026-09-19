import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from peaches_book.floor import (
    issuer_signature_message,
    prepare_floor_stamp,
    prepare_unsigned_stamp,
)
from peaches_book.floor_cli import main


def _stamp():
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public = private.public_key().public_bytes_raw()
    body = prepare_unsigned_stamp(
        public_key=public,
        declaration=b"CLI test only",
        media_type="text/plain;charset=utf-8",
        claimed_at="2000-01-01T00:00:00Z",
        nonce=bytes(reversed(range(32))),
    )
    return prepare_floor_stamp(body, private.sign(issuer_signature_message(body)))


def test_stamp_cli_is_read_only_and_uses_failure_exit_codes(tmp_path, capsys):
    path = tmp_path / "stamp.json"
    path.write_text(json.dumps(_stamp()), encoding="utf-8")

    assert main(["stamp", str(path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "VALID_FLOOR_STRUCTURE_AND_SIGNATURE"

    path.write_text('{"schema":"not-a-stamp"}', encoding="utf-8")
    assert main(["stamp", str(path)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "INVALID_FLOOR_STAMP"


def test_rubric_id_cli_derives_only_content_identity(tmp_path, capsys):
    path = tmp_path / "rubric.txt"
    path.write_bytes(b"bounded test rubric")
    assert main(["rubric-id", "text/plain", str(path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "DERIVED_CONTENT_IDENTIFIER"
    assert report["rubric_id"].startswith("peaches:rubric:v1:")
    assert report["claim"] == "content_identity_only"
