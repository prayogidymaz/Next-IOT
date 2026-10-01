from __future__ import annotations

import csv
import io
from datetime import datetime

from app.models.audit_log import AuditLog


def render_audit_csv(rows: list[AuditLog]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "timestamp",
            "actor_id",
            "actor_email",
            "tenant_id",
            "action",
            "resource_target",
            "ip_address",
            "status",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.timestamp.isoformat() if isinstance(row.timestamp, datetime) else row.timestamp,
                str(row.actor_id) if row.actor_id else "",
                row.actor_email,
                str(row.tenant_id) if row.tenant_id else "",
                row.action,
                row.resource_target,
                row.ip_address or "",
                row.status,
            ]
        )
    return buffer.getvalue()
