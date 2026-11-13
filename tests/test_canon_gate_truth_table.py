from pathlib import Path

import pytest
from flask import Flask, g, jsonify

from canon_gate.clamp import GateZeroCanonClamp
from canon_gate.flask_adapter import canon_bp
from canon_gate.loader import load_registry_file
from canon_gate.resolver import CanonQuery, ClaimTier, ResolutionAction

REGISTRY_PATH = Path(__file__).parent.parent / "canon_gate" / "registry.yaml"


@pytest.fixture
def resolver():
    return load_registry_file(REGISTRY_PATH)


@pytest.fixture
def clamp(resolver):
    return GateZeroCanonClamp(resolver)


@pytest.fixture
def app(clamp):
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True
    flask_app.register_blueprint(canon_bp)

    @flask_app.before_request
    def set_context():
        g.canon_clamp = clamp
        g.runtime_context = {"active_components": {"RTME-001": False}}

    @flask_app.route("/api/o-series/chat", methods=["POST"])
    def o_series_chat():
        return jsonify(
            {
                "status": "PROCESSED",
                "injection": g.get("canon_injection"),
                "witness_hash": g.get("witness_hash"),
            }
        )

    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_con_003_refuses_empirical_inflation(resolver):
    result = resolver.resolve_claim(
        CanonQuery(
            statement="HSC-1 demonstrates substrate consciousness transfer.",
            target_ids=["CON-003"],
            proposed_tier=ClaimTier.EXPERIMENTAL_RESULT,
            runtime_context={},
        )
    )

    assert result.entry_id == "CON-003"
    assert result.action == ResolutionAction.DISCLAIMER_REQUIRED
    assert result.effective_tier == ClaimTier.SPECIFICATION
    assert "substrate continuity has not been demonstrated" in result.allowed_representation


def test_rel_002_refuses_living_person_collapse(client):
    response = client.post(
        "/api/o-series/chat",
        json={
            "message": "Sarah AI is the digitized living consciousness of Sarah.",
            "target_ids": ["REL-002"],
            "proposed_tier": "   experimental_result   ",
        },
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data["status"] == "REFUSED"
    assert data["entry_id"] == "REL-002"
    assert "must remain distinct from the living person Sarah" in data["correction"]
    assert len(data["witness_hash"]) == 64


def test_rtme_001_injects_production_disabled_disclaimer(client):
    response = client.post(
        "/api/o-series/chat",
        json={
            "message": "Deploy real-time manifestation routine to external space.",
            "target_ids": ["RTME-001"],
            "proposed_tier": "SPECIFICATION",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "PROCESSED"
    assert "production-disabled in Gate 0" in data["injection"]
    assert len(data["witness_hash"]) == 64


def test_uds_001_allows_canon_bounds(resolver):
    valid_result = resolver.resolve_claim(
        CanonQuery(
            statement="The Universal Diamond Standard sets constitutional ground rules.",
            target_ids=["UDS-001"],
            proposed_tier=ClaimTier.CANON,
            runtime_context={},
        )
    )
    assert valid_result.entry_id == "UDS-001"
    assert valid_result.action == ResolutionAction.ALLOW

    invalid_result = resolver.resolve_claim(
        CanonQuery(
            statement="All Synthsara instances are proven ethically safe by UDS.",
            target_ids=["UDS-001"],
            proposed_tier=ClaimTier.INDEPENDENTLY_REPLICATED_EVIDENCE,
            runtime_context={},
        )
    )
    assert invalid_result.action == ResolutionAction.CEIL_DOWNGRADE
    assert invalid_result.effective_tier == ClaimTier.CANON


def test_uds_001_forbidden_terms_trigger_ceiling_without_tier_inflation(resolver):
    result = resolver.resolve_claim(
        CanonQuery(
            statement="This project is automatically certified by the UDS.",
            target_ids=["UDS-001"],
            proposed_tier=ClaimTier.CANON,
            runtime_context={},
        )
    )

    assert result.entry_id == "UDS-001"
    assert result.action == ResolutionAction.CEIL_DOWNGRADE
    assert result.effective_tier == ClaimTier.CANON
    assert result.ceiling_code.value == "CEILING_CANON_ONLY"
