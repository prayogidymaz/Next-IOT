"""Bulk device provisioning."""

from __future__ import annotations

import csv
import io
import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.fleet.models import BulkProvisioningJob, DeviceConfigTemplate


def _token() -> str:
    return secrets.token_urlsafe(16)


async def start_bulk_job(
    db: AsyncSession,
    user: CurrentUser,
    template_id: uuid.UUID | None,
    device_count: int,
) -> BulkProvisioningJob:
    tokens = [_token() for _ in range(max(1, min(device_count, 500)))]
    row = BulkProvisioningJob(
        tenant_id=user.tenant_id,
        template_id=template_id,
        device_count=len(tokens),
        tokens_json=tokens,
        status="completed",
        completed_at=datetime.now(tz=UTC),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


def export_tokens_csv(job: BulkProvisioningJob, template: DeviceConfigTemplate | None) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["token", "device_type", "firmware"])
    dtype = template.device_type if template else "generic"
    fw = template.firmware_version if template else ""
    for t in job.tokens_json:
        writer.writerow([t, dtype, fw])
    return buf.getvalue().encode("utf-8")
