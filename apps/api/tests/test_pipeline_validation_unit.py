from app.rules.pipeline_validation import validate_pipeline_document


def test_logic_and_missing_conditions_is_error():
    nodes = [
        {"id": "t1", "type": "TRIGGER", "subtype": "TELEMETRY_THRESHOLD", "config": {"metric": "temperature", "operator": ">", "threshold": 1}},
        {"id": "c1", "type": "CONDITION", "subtype": "LOGIC_AND", "config": {}},
    ]
    errors, _ = validate_pipeline_document(nodes, [])
    assert any("LOGIC_AND" in e for e in errors)
