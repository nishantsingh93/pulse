import json
from pathlib import Path
from openapi_spec_validator import validate_spec
from pulse.api.main import app


def test_exported_openapi_matches_runtime_and_is_valid():
    exported = json.loads(Path("docs/api/openapi.json").read_text())
    assert exported == app.openapi()
    assert exported["openapi"] == "3.0.3"
    validate_spec(exported)
