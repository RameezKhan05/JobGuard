import pytest
from pydantic import ValidationError
from app.schemas import ActionRequest

def test_hold_request():
    assert ActionRequest(action="HOLD", reason="Test in lower environment").action == "HOLD"

def test_reject_unsupported_action():
    with pytest.raises(ValidationError): ActionRequest(action="KILL", reason="Not in scope")

def test_reason_required():
    with pytest.raises(ValidationError): ActionRequest(action="RELEASE", reason="x")
