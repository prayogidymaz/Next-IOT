from app.automation.xyflow_adapter import is_xyflow_graph, normalize_xyflow_graph
from app.rules.pipeline_validation import validate_pipeline_document


def test_normalize_biofloc_xyflow_graph():
    nodes = [
        {
            "id": "trigger-1",
            "type": "automation",
            "data": {"kind": "trigger", "label": "Biofloc", "sensorId": "pond-a/temp"},
        },
        {
            "id": "condition-1",
            "type": "automation",
            "data": {"kind": "condition", "label": "Hot", "operator": ">", "threshold": 30},
        },
        {
            "id": "action-1",
            "type": "automation",
            "data": {"kind": "action", "label": "Aerator", "relayPin": "aerator-main/ch1"},
        },
    ]
    edges = [
        {"id": "e1", "source": "trigger-1", "target": "condition-1"},
        {"id": "e2", "source": "condition-1", "target": "action-1"},
    ]
    assert is_xyflow_graph(nodes)
    normalized_nodes, normalized_edges = normalize_xyflow_graph(nodes, edges)
    errors, _ = validate_pipeline_document(normalized_nodes, normalized_edges)
    assert not errors
    assert normalized_nodes[0]["subtype"] == "TELEMETRY_THRESHOLD"
    assert normalized_nodes[2]["subtype"] == "DEVICE_COMMAND"
    assert normalized_edges[0] == {"from": "trigger-1", "to": "condition-1"}
