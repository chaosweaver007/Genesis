"""UDS-AUTH receiver preview (offline, E0 only; not an executor).

The current SYN-RD-002 compiler emits no executable E1 descriptors. This
module binds exact plans to signed, scoped E0 review permits, verifies trusted
consent and possession at commit time, and atomically burns nonces. External
effects ALWAYS fail closed. No public route imports this module.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

try:
    from rtme_parser import IntentAST
except ImportError:
    from Genesis.rtme_parser import IntentAST

POLICY_VERSION = "UDS-AUTH-PREVIEW-0.1"
DOMAIN = b"SYNTHSARA/UDS-AUTH-PREVIEW/v1\x00"
PERMIT_FIELDS = frozenset({
    "version", "issuer", "key_id", "plan_digest", "step_id", "subject_id",
    "resource_scope", "requested_authority", "effect_class", "nonce",
    "issued_at", "expires_at",
})
_HEX64 = re.compile(r"[a-f0-9]{64}\Z", flags=re.ASCII)
_HEX32 = re.compile(r"[a-f0-9]{32}\Z", flags=re.ASCII)
_ALLOWED_AUTHORITIES = frozenset({"draft:review"})
_MAX_JSON_BYTES = 65536


class PermitError(ValueError):
    """Malformed or unauthorized permit data."""


def _utf16_key(value: str) -> bytes:
    return value.encode("utf-16-be", errors="strict")


def _canonical_fragment(obj: Any, depth: int = 0) -> str:
    """JCS serialization for the bounded I-JSON subset used by these contracts.

    Floats intentionally fail closed; all accepted numbers are safe integers.
    Strings are not Unicode-normalized, as required by RFC 8785.
    """
    if depth > 30:
        raise PermitError("JSON depth limit exceeded")
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if type(obj) is int:
        if abs(obj) > 9007199254740991:
            raise PermitError("integer outside safe IEEE-754 range")
        return str(obj)
    if type(obj) is str:
        try:
            obj.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise PermitError("invalid Unicode surrogate") from exc
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    if type(obj) is list:
        if len(obj) > 512:
            raise PermitError("array too large")
        return "[" + ",".join(_canonical_fragment(v, depth + 1) for v in obj) + "]"
    if type(obj) is dict:
        if len(obj) > 512 or any(type(k) is not str for k in obj):
            raise PermitError("invalid object keys")
        keys = sorted(obj, key=_utf16_key)
        return "{" + ",".join(
            _canonical_fragment(k, depth + 1) + ":" +
            _canonical_fragment(obj[k], depth + 1)
            for k in keys
        ) + "}"
    raise PermitError("unsupported JSON value type")


def jcs_bytes(value: Any) -> bytes:
    """RFC 8785-compatible bytes for this strict I-JSON subset, not floats."""
    data = _canonical_fragment(value).encode("utf-8")
    if len(data) > _MAX_JSON_BYTES:
        raise PermitError("canonical document too large")
    return data


def plan_digest(plan: IntentAST) -> str:
    """Bind complete user text, all nodes and all existing plan fields."""
    if not isinstance(plan, IntentAST):
        raise PermitError("expected typed SYN-RD-002 IntentAST")
    record = plan.to_dict()
    if (record.get("execution_permitted") is not False or
            record.get("execution_status") != "NOT_EXECUTED"):
        raise PermitError("plan must remain non-executing")
    return hashlib.sha256(jcs_bytes(record)).hexdigest()


def _token(value: Any, label: str, maximum: int = 128) -> str:
    if type(value) is not str or not (1 <= len(value) <= maximum):
        raise PermitError("invalid " + label)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9:_./-]*", value, flags=re.ASCII):
        raise PermitError("invalid " + label)
    return value


def _claims(value: Any) -> dict[str, Any]:
    if type(value) is not dict or value.keys() != PERMIT_FIELDS:
        raise PermitError("unexpected permit claims")
    if value["version"] != "1" or value["effect_class"] != "E0":
        raise PermitError("only E0 preview is supported")
    for label in ("issuer", "key_id", "subject_id", "resource_scope", "step_id"):
        _token(value[label], label)
    if not re.fullmatch(r"6:[123]", value["step_id"]):
        raise PermitError("unknown phase-six step")
    if type(value["plan_digest"]) is not str or not _HEX64.fullmatch(value["plan_digest"]):
        raise PermitError("invalid plan digest")
    if type(value["nonce"]) is not str or not _HEX32.fullmatch(value["nonce"]):
        raise PermitError("invalid nonce")
    authorities = value["requested_authority"]
    if (type(authorities) is not list or not authorities or len(authorities) > 12 or
            any(type(a) is not str or a not in _ALLOWED_AUTHORITIES for a in authorities) or
            authorities != sorted(set(authorities))):
        raise PermitError("invalid requested_authority")
    start, end = value["issued_at"], value["expires_at"]
    if type(start) is not int or type(end) is not int or end <= start or end - start > 300:
        raise PermitError("invalid permit lifetime")
    return value


@dataclass(frozen=True)
class Decision:
    decision_class: str
    permitted: bool
    receipt: dict[str, Any]


class PermitIssuer:
    """Trusted local signer; never expose to an untrusted request handler."""

    def __init__(self, *, issuer: str, key_id: str, secret: bytes):
        self.issuer = _token(issuer, "issuer")
        self.key_id = _token(key_id, "key_id")
        if type(secret) is not bytes or len(secret) < 32:
            raise PermitError("HMAC secret must have at least 32 random bytes")
        self._secret = secret

    def sign(self, claims: dict[str, Any]) -> dict[str, Any]:
        claims = _claims(claims)
        if claims["issuer"] != self.issuer or claims["key_id"] != self.key_id:
            raise PermitError("issuer mismatch")
        mac = hmac.new(self._secret, DOMAIN + jcs_bytes(claims), hashlib.sha256).hexdigest()
        return {"claims": dict(claims), "signature": mac}


class ReceiverBroker:
    """Server-side, local SQLite replay/consent broker, no actual executor.

    Trusted administration MUST authenticate calls to set_trusted_grant().
    On each decision, consent and possessed authority are loaded while
    holding the same SQLite write transaction that burns the nonce.
    """

    def __init__(self, db_path: str | Path, *,
                 trusted_keys: Mapping[tuple[str, str], bytes],
                 clock: Callable[[], float] = time.time):
        self.db_path = str(db_path)
        self.clock = clock
        self.keys = dict(trusted_keys)
        for key, secret in self.keys.items():
            if (type(key) is not tuple or len(key) != 2 or
                    type(secret) is not bytes or len(secret) < 32):
                raise PermitError("invalid trusted keyring")
        with closing(self._connect()) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS consent (
                    subject TEXT NOT NULL, scope TEXT NOT NULL, authority TEXT NOT NULL,
                    expires_at INTEGER NOT NULL, revoked INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY(subject, scope, authority)
                );
                CREATE TABLE IF NOT EXISTS possession (
                    subject TEXT NOT NULL, scope TEXT NOT NULL, authority TEXT NOT NULL,
                    expires_at INTEGER NOT NULL, revoked INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY(subject, scope, authority)
                );
                CREATE TABLE IF NOT EXISTS consumed (
                    issuer TEXT NOT NULL, nonce TEXT NOT NULL, consumed_at INTEGER NOT NULL,
                    PRIMARY KEY(issuer, nonce)
                );
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, isolation_level=None, timeout=5.0)
        db.execute("PRAGMA busy_timeout=5000")
        return db

    def set_trusted_grant(self, kind: str, *, subject: str, scope: str,
                          authority: str, expires_at: int,
                          revoked: bool = False) -> None:
        """Fixture/admin operation; MUST NOT be exposed as a public API."""
        if kind not in ("consent", "possession"):
            raise PermitError("unknown grant registry")
        _token(subject, "subject")
        _token(scope, "scope")
        if authority not in _ALLOWED_AUTHORITIES or type(expires_at) is not int:
            raise PermitError("invalid grant")
        with closing(self._connect()) as db:
            db.execute(
                f"INSERT INTO {kind} (subject,scope,authority,expires_at,revoked) VALUES (?,?,?,?,?) "
                "ON CONFLICT(subject,scope,authority) DO UPDATE SET "
                "expires_at=excluded.expires_at,revoked=excluded.revoked",
                (subject, scope, authority, expires_at, int(revoked)),
            )

    def authorize_preview(self, *, plan: IntentAST, permit: Any,
                          authenticated_subject: str, step_id: str,
                          resource_scope: str, requested_effect: str = "E0") -> Decision:
        """ALLOW_PREVIEW never grants authority to execute real-world actions."""
        try:
            digest = plan_digest(plan)
        except (PermitError, TypeError, ValueError, UnicodeError):
            digest = None
        timestamp = int(self.clock())
        receipt = {
            "plan_digest": digest,
            "decision_class": "DENY_INVALID",
            "policy_version": POLICY_VERSION,
            "timestamp_bucket": timestamp - timestamp % 3600,
            "zk_proof": None,
            "receipt_kind": "UNSIGNED_LOCAL_DECISION_METADATA",
            "executed": False,
        }

        def deny(code: str) -> Decision:
            receipt["decision_class"] = code
            return Decision(code, False, dict(receipt))

        if digest is None:
            return deny("DENY_PLAN")
        if requested_effect != "E0":
            return deny("DENY_EXTERNAL_EFFECT_UNAVAILABLE")
        try:
            _token(authenticated_subject, "subject")
            _token(resource_scope, "scope")
            if type(step_id) is not str or not re.fullmatch(r"6:[123]", step_id):
                raise PermitError("invalid step")
            if not any(n.phase == 6 and step_id == f"6:{n.ordinal}" for n in plan.nodes):
                raise PermitError("step absent from plan")
            if type(permit) is not dict or permit.keys() != {"claims", "signature"}:
                raise PermitError("invalid permit")
            claims = _claims(permit["claims"])
            signature = permit["signature"]
            if type(signature) is not str or not _HEX64.fullmatch(signature):
                raise PermitError("invalid signature")
            secret = self.keys.get((claims["issuer"], claims["key_id"]))
            if secret is None:
                raise PermitError("unknown issuer")
            expected = hmac.new(secret, DOMAIN + jcs_bytes(claims), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise PermitError("invalid signature")
            if (claims["plan_digest"] != digest or
                    claims["subject_id"] != authenticated_subject or
                    claims["step_id"] != step_id or
                    claims["resource_scope"] != resource_scope):
                raise PermitError("signed binding mismatch")
        except (PermitError, KeyError, ValueError, TypeError, UnicodeError):
            return deny("DENY_PERMIT")

        db = None
        try:
            db = self._connect()
            db.execute("BEGIN IMMEDIATE")
            now = int(self.clock())
            if claims["issued_at"] > now or claims["expires_at"] <= now:
                db.execute("ROLLBACK")
                return deny("DENY_EXPIRED")
            requested = set(claims["requested_authority"])
            granted = {r[0] for r in db.execute(
                "SELECT authority FROM consent WHERE subject=? AND scope=? "
                "AND revoked=0 AND expires_at>?",
                (authenticated_subject, resource_scope, now),
            )}
            possessed = {r[0] for r in db.execute(
                "SELECT authority FROM possession WHERE subject=? AND scope=? "
                "AND revoked=0 AND expires_at>?",
                (authenticated_subject, resource_scope, now),
            )}
            if not (requested <= granted <= possessed):
                db.execute("ROLLBACK")
                return deny("DENY_SCOPE_OR_CONSENT")
            try:
                db.execute(
                    "INSERT INTO consumed (issuer,nonce,consumed_at) VALUES (?,?,?)",
                    (claims["issuer"], claims["nonce"], now),
                )
            except sqlite3.IntegrityError:
                db.execute("ROLLBACK")
                return deny("DENY_REPLAY")
            db.execute("COMMIT")
        except sqlite3.Error:
            if db is not None:
                try:
                    db.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
            return deny("DENY_STORE_FAILURE")
        finally:
            if db is not None:
                db.close()
        receipt["decision_class"] = "ALLOW_PREVIEW"
        return Decision("ALLOW_PREVIEW", True, dict(receipt))
