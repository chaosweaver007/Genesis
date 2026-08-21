"""Atomic in-process authorization state for UDS-AUTH-005 and single-use permits."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Dict, Tuple


@dataclass(frozen=True)
class ExecutionJournalEntry:
    permit_id: str
    idempotency_key: str
    request_hash: str
    status: str
    result_digest: str | None = None


class AuthorizationStateRegistry:
    """Thread-safe epoch and execution journal.

    This is a reference in-process registry, not a distributed consensus store.
    Production multi-node deployment must provide equivalent atomic semantics in
    durable storage.
    """

    def __init__(
        self,
        *,
        consent_epoch: int = 1,
        broker_key_epoch: int = 1,
        authority_epoch: int = 1,
        policy_digest: str = "",
    ) -> None:
        self._lock = RLock()
        self.consent_epoch = consent_epoch
        self.broker_key_epoch = broker_key_epoch
        self.authority_epoch = authority_epoch
        self.policy_digest = policy_digest
        self._journal: Dict[str, ExecutionJournalEntry] = {}

    def assert_current(
        self,
        *,
        consent_epoch: int,
        broker_key_epoch: int,
        authority_epoch: int,
        policy_digest: str,
    ) -> None:
        with self._lock:
            if consent_epoch != self.consent_epoch:
                raise PermissionError("Stale consent epoch.")
            if broker_key_epoch != self.broker_key_epoch:
                raise PermissionError("Stale broker key epoch.")
            if authority_epoch != self.authority_epoch:
                raise PermissionError("Stale authority epoch.")
            if policy_digest != self.policy_digest:
                raise PermissionError("Policy digest is no longer current.")

    def begin_execution(
        self,
        *,
        permit_id: str,
        idempotency_key: str,
        request_hash: str,
    ) -> Tuple[str, ExecutionJournalEntry]:
        if not idempotency_key:
            raise ValueError("idempotency_key is required.")
        with self._lock:
            existing = self._journal.get(permit_id)
            if existing is None:
                entry = ExecutionJournalEntry(
                    permit_id=permit_id,
                    idempotency_key=idempotency_key,
                    request_hash=request_hash,
                    status="EXECUTION_STARTED",
                )
                self._journal[permit_id] = entry
                return "STARTED", entry

            if (
                existing.idempotency_key == idempotency_key
                and existing.request_hash == request_hash
            ):
                if existing.status == "COMMITTED":
                    return "ALREADY_COMMITTED", existing
                return "IN_PROGRESS", existing

            raise PermissionError("Permit replay conflicts with the original execution.")

    def commit(self, *, permit_id: str, result_digest: str) -> ExecutionJournalEntry:
        with self._lock:
            existing = self._journal.get(permit_id)
            if existing is None:
                raise RuntimeError("Cannot commit an execution that was never started.")
            if existing.status == "COMMITTED":
                if existing.result_digest != result_digest:
                    raise PermissionError("Committed permit cannot be rebound to another result.")
                return existing
            committed = ExecutionJournalEntry(
                permit_id=existing.permit_id,
                idempotency_key=existing.idempotency_key,
                request_hash=existing.request_hash,
                status="COMMITTED",
                result_digest=result_digest,
            )
            self._journal[permit_id] = committed
            return committed
