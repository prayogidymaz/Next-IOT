"""Suggest batch actions for alert clusters."""

from __future__ import annotations

from app.agents.triage.types import AlertCluster, BatchActionPlan


class BatchAction:
    def suggest_batch(self, cluster: AlertCluster) -> BatchActionPlan:
        count = len(cluster.alerts)
        plot = cluster.signature.split("|")[0] if cluster.signature else "cluster"
        device_ids = [str(a.device_id) for a in cluster.alerts if a.device_id is not None]
        summary = f"{count} alert(s) in {plot} — batch irrigation/actuator workflow"
        workflow_hint = "open_valve_batch"
        if "soil" in plot.lower() or any(a.metric == "soil_moisture" for a in cluster.alerts):
            summary = f"{count} soil moisture alert → open valve A1-A5 together"
            workflow_hint = "irrigation_batch_plot_a"
        return BatchActionPlan(
            cluster_signature=cluster.signature,
            summary=summary,
            workflow_hint=workflow_hint,
            parallel_device_ids=device_ids[:10],
        )
