"""Natural-language → WorkflowDraft generator (Anthropic + regex mock fallback)."""

from __future__ import annotations

import json
import re
import uuid
from re import Pattern

import httpx

from app.config import settings
from app.mesh.ai_copilot.nl_examples import few_shot_block, match_example_prompt
from app.mesh.ai_copilot.workflow_draft import (
    DraftAction,
    DraftTrigger,
    DraftTriggerKind,
    WorkflowDraft,
)

_ID_SYSTEM = """
Anda adalah Next-IOT Copilot untuk petani Indonesia. Ubah permintaan bahasa alami menjadi JSON WorkflowDraft.
Schema:
- name, description (string)
- trigger: {kind: sensor_threshold|cron|event, sensor?, operator?: lt|lte|gt|gte|eq,
  threshold?, device?, cron?, event_type?, domain?}
- actions: [{actuator?, action, duration_minutes?, channels?, template?, webhook_url?, severity?}]

Contoh trigger sensor: soil_moisture, soil_ph, lux, temperature, ndvi, humidity, co2.
Jawab HANYA JSON object WorkflowDraft tanpa markdown (tanpa draft_id/tenant_id).
""".strip()


_MOCK_PATTERNS: list[tuple[Pattern[str], DraftTriggerKind, str]] = [
    (re.compile(r"(pagi|jam\s*\d|schedule|cron|setiap hari|every morning)", re.I), DraftTriggerKind.CRON, "cron"),
    (re.compile(r"(siram|irigasi|sirami|water|irrigate)", re.I), DraftTriggerKind.SENSOR_THRESHOLD, "irrigation"),
    (re.compile(r"(notif|whatsapp|wa\b|telegram|email|alert)", re.I), DraftTriggerKind.SENSOR_THRESHOLD, "alert"),
    (re.compile(r"(lampu|lux|cahaya|light|greenhouse)", re.I), DraftTriggerKind.SENSOR_THRESHOLD, "light"),
    (re.compile(r"(ph\b|asam)", re.I), DraftTriggerKind.SENSOR_THRESHOLD, "ph"),
    (re.compile(r"(suhu|temperature|panas)", re.I), DraftTriggerKind.SENSOR_THRESHOLD, "temp"),
    (re.compile(r"(webhook|erp|integrasi)", re.I), DraftTriggerKind.EVENT, "webhook"),
    (re.compile(r"(hujan|rain)", re.I), DraftTriggerKind.EVENT, "rain"),
    (re.compile(r"(baterai|battery)", re.I), DraftTriggerKind.EVENT, "battery"),
    (re.compile(r"(ndvi|tanaman stress)", re.I), DraftTriggerKind.SENSOR_THRESHOLD, "ndvi"),
]


class WorkflowGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key.strip()
        self._model = model.strip() or "claude-sonnet-4-5"

    @classmethod
    def from_settings(cls) -> WorkflowGenerator:
        return cls(settings.anthropic_api_key, settings.llm_model)

    @property
    def mock_mode(self) -> bool:
        return not self._api_key

    async def generate_from_nl(self, prompt: str, tenant_id: uuid.UUID, locale: str = "id") -> WorkflowDraft:
        if self.mock_mode:
            draft = self._mock_from_nl(prompt, locale)
        else:
            draft = await self._llm_from_nl(prompt, locale)
        return draft.model_copy(
            update={
                "draft_id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "locale": locale,
            }
        )

    async def _llm_from_nl(self, prompt: str, locale: str) -> WorkflowDraft:
        few_shot = few_shot_block(locale, limit=5)
        user_content = json.dumps(
            {"prompt": prompt, "locale": locale, "few_shot": few_shot},
            ensure_ascii=False,
        )
        payload = {
            "model": self._model,
            "max_tokens": 2048,
            "system": _ID_SYSTEM,
            "messages": [{"role": "user", "content": user_content}],
        }
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        text = _extract_text(data)
        parsed = json.loads(text)
        base = WorkflowDraft.model_validate(
            {
                **parsed,
                "draft_id": str(uuid.uuid4()),
                "tenant_id": str(uuid.uuid4()),
                "source": "llm",
            }
        )
        return base

    def _mock_from_nl(self, prompt: str, locale: str) -> WorkflowDraft:
        matched = match_example_prompt(prompt)
        if matched is not None:
            return matched.model_copy(update={"source": "few_shot", "locale": locale})

        category = "irrigation"
        for pattern, _kind, cat in _MOCK_PATTERNS:
            if pattern.search(prompt):
                category = cat
                break

        normalized = prompt.lower()
        minutes = _extract_int(normalized, r"(\d+)\s*menit", default=15)
        threshold = float(_extract_int(normalized, r"(\d+)\s*(%|persen)?", default=40))
        plot = _extract_plot(normalized)

        if category == "cron":
            hour = _extract_int(normalized, r"jam\s*(\d+)", default=6)
            return WorkflowDraft(
                draft_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                locale=locale,
                name=f"Scheduled {plot}",
                description="Mock cron workflow from NL.",
                trigger=DraftTrigger(kind=DraftTriggerKind.CRON, cron=f"0 {hour} * * *"),
                actions=[DraftAction(actuator=f"valve_{plot}", action="open", duration_minutes=minutes)],
                source="mock",
            )
        if category == "alert":
            return WorkflowDraft(
                draft_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                locale=locale,
                name="Alert workflow",
                description="Mock alert from NL.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.SENSOR_THRESHOLD,
                    sensor="soil_ph" if "ph" in normalized else "soil_moisture",
                    operator="lt",
                    threshold=5.5 if "ph" in normalized else threshold,
                    device=f"{plot}_sensor",
                ),
                actions=[
                    DraftAction(
                        action="notify",
                        channels=["whatsapp"],
                        template="Alert otomatis dari copilot mock.",
                    ),
                ],
                source="mock",
            )
        if category == "light":
            lux = float(_extract_int(normalized, r"(\d+)\s*lux", default=300))
            return WorkflowDraft(
                draft_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                locale=locale,
                name="Greenhouse lighting",
                description="Mock lux-triggered lights.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.SENSOR_THRESHOLD,
                    sensor="lux",
                    operator="lt",
                    threshold=lux,
                    device="greenhouse_light_sensor",
                ),
                actions=[DraftAction(actuator="greenhouse_lamp", action="turn_on")],
                source="mock",
            )
        if category == "webhook":
            return WorkflowDraft(
                draft_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                locale=locale,
                name="Webhook integration",
                description="Mock webhook action.",
                trigger=DraftTrigger(kind=DraftTriggerKind.EVENT, domain="sensor", event_type="reading_update"),
                actions=[DraftAction(action="webhook", webhook_url="https://hooks.example/next-iot")],
                source="mock",
            )
        return WorkflowDraft(
            draft_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            locale=locale,
            name=f"Irrigation {plot}",
            description="Mock irrigation from NL.",
            trigger=DraftTrigger(
                kind=DraftTriggerKind.SENSOR_THRESHOLD,
                sensor="soil_moisture",
                operator="lt",
                threshold=threshold,
                device=f"{plot}_sensor",
            ),
            actions=[DraftAction(actuator=f"valve_{plot}", action="open", duration_minutes=minutes)],
            source="mock",
        )


def _extract_text(data: dict[str, object]) -> str:
    content = data.get("content")
    if not isinstance(content, list):
        raise ValueError("Unexpected LLM response shape")
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str):
                return text.strip()
    raise ValueError("No text block in LLM response")


def _extract_int(text: str, pattern: str, default: int) -> int:
    match = re.search(pattern, text)
    if match is None:
        return default
    return int(match.group(1))


def _extract_plot(text: str) -> str:
    match = re.search(r"plot\s*([a-z0-9_]+)", text, re.I)
    if match:
        return f"plot_{match.group(1).upper().replace('-', '_')}"
    if "plot a" in text or "plot_a" in text:
        return "plot_A"
    if "plot b" in text:
        return "plot_B"
    return "plot_A"
