"""RACE-001: forced revocation between freshness check and journal admission.

Baseline: 7bc864f192ae17f9ef013a5721d55c92a5d2986c.
Run: python -m pytest -q tests/test_race_001.py
Expected baseline failure: STARTED after consent epoch advancement.
No external execution or real credentials are involved.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from test_uds_v1_1_authority import NOW, consent, evidence, harness, request


def test_race_001_revocation_before_journal_admission(monkeypatch):
    _, broker, registry, verifier = harness()
    req = request()
    permit = broker.issue_permit(
        consent=consent(), authority_evidence=evidence(),
        request=req, state=registry, now=NOW,
    )
    entered = Event()
    revoked = Event()
    original = registry.assert_current

    def pause_after_check(**kwargs):
        original(**kwargs)
        entered.set()
        if not revoked.wait(5):
            raise TimeoutError("Revocation barrier timed out")

    monkeypatch.setattr(registry, "assert_current", pause_after_check)

    def authorize():
        return verifier.authorize_execution(
            permit=permit, request=req, expected_audience=req.audience,
            idempotency_key="race-001", state=registry, now=NOW,
        )

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(authorize)
        try:
            assert entered.wait(5), "Worker did not reach freshness barrier"
            # Baseline exposes epoch as a public attribute; synchronize the
            # test mutation with the registry lock.
            with registry._lock:
                registry.consent_epoch += 1
        finally:
            revoked.set()
        try:
            status, entry = future.result(timeout=5)
        except PermissionError as exc:
            assert "Stale consent epoch" in str(exc)
        else:
            pytest.fail(f"RACE-001: stale permit admitted: {status}, {entry!r}")
