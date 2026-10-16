"""Run a private-data-free accountability lifecycle demonstration.

From the repository root:
    python examples/accountability_walkthrough.py

This is NOT a production adjudication service, and no actual access,
funds, sanctions, or data permissions are changed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from Genesis.institutional_accountability import AccountabilityKernel, Principal


def actor(identifier: str, role: str) -> Principal:
    return Principal(identifier, frozenset({role}), authenticated=True)


def evidence(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run() -> dict:
    kernel = AccountabilityKernel()
    person = actor("person", "participant")
    first = actor("reviewer-a", "reviewer")
    second = actor("reviewer-b", "reviewer")
    auditor = actor("auditor-c", "auditor")

    case_id, _ = kernel.open_case(
        person, "example-institution", "access", evidence("synthetic complaint")
    )
    kernel.assign_reviewer(case_id, first)
    kernel.decide(case_id, first, "DISMISS")
    kernel.appeal(case_id, person, evidence("synthetic appeal"))
    kernel.resolve_appeal(case_id, second, "RESTORE")
    kernel.verify_remedy(case_id, auditor, evidence("synthetic remedy verification"))
    kernel.close(case_id, auditor)

    receipts = kernel.receipts(case_id)
    pinned_head = receipts[-1]["sha256"]
    assert kernel.verify_chain(case_id, expected_head=pinned_head)
    return {
        "status": "REFERENCE_DEMONSTRATION_ONLY",
        "case_id": case_id,
        "receipt_count": len(receipts),
        "sequence": [r["action"] for r in receipts],
        "final_state": receipts[-1]["state"],
        "hash_chain_verified": True,
        "head_sha256": pinned_head,
        "actual_resource_transfers": 0,
        "actual_permissions_changed": 0,
        "durable_record_created": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
