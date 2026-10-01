import csv
import io
import json

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, ValidationError


class BulkDeviceImportRow(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    device_type: str = Field(min_length=1, max_length=100)
    device_category: str | None = Field(default=None, max_length=64)
    metadata: dict[str, str] = Field(default_factory=dict)


class BulkImportRequest(BaseModel):
    devices: list[BulkDeviceImportRow] = Field(min_length=1, max_length=500)


def parse_bulk_import_payload(raw: bytes, content_type: str, filename: str | None) -> BulkImportRequest:
    lowered = (filename or "").lower()
    is_csv = "csv" in content_type.lower() or lowered.endswith(".csv")
    is_json = "json" in content_type.lower() or lowered.endswith(".json")

    if is_csv or (not is_json and b"," in raw[:256] and raw.strip().startswith(b"name")):
        return _parse_csv(raw)
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid bulk import file: expected JSON or CSV",
        ) from exc

    if isinstance(data, dict) and "devices" in data:
        try:
            return BulkImportRequest.model_validate(data)
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc
    if isinstance(data, list):
        try:
            return BulkImportRequest(devices=[BulkDeviceImportRow.model_validate(row) for row in data])
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="JSON must be { devices: [...] } or an array of device rows",
    )


def _parse_csv(raw: bytes) -> BulkImportRequest:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "name" not in reader.fieldnames or "device_type" not in reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CSV must include columns: name, device_type (optional: device_category)",
        )
    rows: list[BulkDeviceImportRow] = []
    for idx, row in enumerate(reader, start=2):
        name = (row.get("name") or "").strip()
        device_type = (row.get("device_type") or "").strip()
        if not name or not device_type:
            continue
        metadata: dict[str, str] = {}
        category = (row.get("device_category") or "").strip() or None
        for key, value in row.items():
            if key in {"name", "device_type", "device_category"}:
                continue
            if value is not None and str(value).strip():
                metadata[key] = str(value).strip()
        try:
            rows.append(
                BulkDeviceImportRow(
                    name=name,
                    device_type=device_type,
                    device_category=category,
                    metadata=metadata,
                )
            )
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"CSV row {idx}: {exc.errors()}",
            ) from exc
    if not rows:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="CSV contained no valid rows")
    if len(rows) > 500:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Maximum 500 devices per import")
    return BulkImportRequest(devices=rows)
