"""Fifty bilingual NL → workflow draft examples for few-shot copilot prompting."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.mesh.ai_copilot.workflow_draft import (
    DraftAction,
    DraftTrigger,
    DraftTriggerKind,
    WorkflowDraft,
)
from app.types.json_types import JsonObject


@dataclass(frozen=True, slots=True)
class NlExampleRow:
    prompt_id: str
    prompt_en: str
    draft: WorkflowDraft


def _base_draft(
    *,
    name: str,
    description: str,
    trigger: DraftTrigger,
    actions: list[DraftAction],
) -> WorkflowDraft:
    return WorkflowDraft(
        draft_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        tenant_id=uuid.UUID("00000000-0000-4000-8000-000000000000"),
        locale="id",
        name=name,
        description=description,
        trigger=trigger,
        actions=actions,
        confidence=0.92,
        source="few_shot",
    )


def _irrigation(plot: str, minutes: int, threshold: float = 40.0) -> WorkflowDraft:
    return _base_draft(
        name=f"Irrigation {plot}",
        description=f"Open valve when soil moisture low on {plot}.",
        trigger=DraftTrigger(
            kind=DraftTriggerKind.SENSOR_THRESHOLD,
            sensor="soil_moisture",
            operator="lt",
            threshold=threshold,
            device=f"{plot}_sensor",
        ),
        actions=[
            DraftAction(actuator=f"valve_{plot}", action="open", duration_minutes=minutes),
        ],
    )


def _cron_water(plot: str, cron: str) -> WorkflowDraft:
    return _base_draft(
        name=f"Scheduled water {plot}",
        description=f"Cron irrigation for {plot}.",
        trigger=DraftTrigger(kind=DraftTriggerKind.CRON, cron=cron),
        actions=[DraftAction(actuator=f"valve_{plot}", action="open", duration_minutes=20)],
    )


def _ph_alert(threshold: float = 5.5) -> WorkflowDraft:
    return _base_draft(
        name="Soil pH alert",
        description="WhatsApp when soil pH below threshold.",
        trigger=DraftTrigger(
            kind=DraftTriggerKind.SENSOR_THRESHOLD,
            sensor="soil_ph",
            operator="lt",
            threshold=threshold,
            device="plot_ph_sensor",
        ),
        actions=[
            DraftAction(
                action="notify",
                channels=["whatsapp"],
                template=f"pH tanah di bawah {threshold} — periksa plot.",
            ),
        ],
    )


def _lux_light(threshold: float = 300.0) -> WorkflowDraft:
    return _base_draft(
        name="Greenhouse light boost",
        description="Turn grow lights on when lux is low.",
        trigger=DraftTrigger(
            kind=DraftTriggerKind.SENSOR_THRESHOLD,
            sensor="lux",
            operator="lt",
            threshold=threshold,
            device="greenhouse_light_sensor",
        ),
        actions=[DraftAction(actuator="greenhouse_lamp", action="turn_on")],
    )


def _build_dataset() -> tuple[NlExampleRow, ...]:
    rows: list[NlExampleRow] = [
        NlExampleRow(
            "siram plot B pagi hari jam 6",
            "Water plot B every morning at 6 AM",
            _cron_water("plot_B", "0 6 * * *"),
        ),
        NlExampleRow(
            "notif WA kalau pH tanah di bawah 5.5",
            "WhatsApp alert when soil pH below 5.5",
            _ph_alert(5.5),
        ),
        NlExampleRow(
            "nyalakan lampu greenhouse kalau cahaya kurang dari 300 lux",
            "Turn on greenhouse lights when lux below 300",
            _lux_light(300),
        ),
        NlExampleRow(
            "kalau tanah plot A kering siram selama 15 menit",
            "If plot A soil is dry, irrigate for 15 minutes",
            _irrigation("plot_A", 15, 40),
        ),
        NlExampleRow(
            "kalau kelembaban plot C di bawah 25 persen buka valve 10 menit",
            "If plot C moisture below 25%, open valve 10 minutes",
            _irrigation("plot_C", 10, 25),
        ),
        NlExampleRow(
            "tutup valve plot A setelah hujan deras terdeteksi",
            "Close plot A valve after heavy rain detected",
            _base_draft(
                name="Rain stop irrigation",
                description="Close valve on heavy rain event.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.EVENT,
                    domain="sensor",
                    event_type="threshold_exceeded",
                ),
                actions=[DraftAction(actuator="valve_plot_A", action="close")],
            ),
        ),
        NlExampleRow(
            "kirim email ringkasan panen setiap Senin jam 7",
            "Email harvest summary every Monday 7 AM",
            _base_draft(
                name="Weekly harvest email",
                description="Scheduled harvest summary.",
                trigger=DraftTrigger(kind=DraftTriggerKind.CRON, cron="0 7 * * 1"),
                actions=[
                    DraftAction(
                        action="notify",
                        channels=["email"],
                        template="Ringkasan panen mingguan.",
                    ),
                ],
            ),
        ),
        NlExampleRow(
            "alarm tinggi kalau suhu greenhouse di atas 38 derajat",
            "High alarm when greenhouse temp above 38C",
            _base_draft(
                name="Greenhouse heat alarm",
                description="Temperature ceiling alert.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.SENSOR_THRESHOLD,
                    sensor="temperature",
                    operator="gt",
                    threshold=38,
                    device="greenhouse_temp",
                ),
                actions=[
                    DraftAction(action="alarm", severity="high", template="Suhu greenhouse > 38°C"),
                ],
            ),
        ),
        NlExampleRow(
            "siram plot D otomatis jam 5 pagi selama 25 menit",
            "Auto irrigate plot D at 5 AM for 25 minutes",
            _cron_water("plot_D", "0 5 * * *"),
        ),
        NlExampleRow(
            "notifikasi Telegram jika baterai sensor plot E lemah",
            "Telegram when plot E sensor battery low",
            _base_draft(
                name="Low battery notify",
                description="Battery low event notification.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.EVENT,
                    domain="sensor",
                    event_type="battery_low",
                ),
                actions=[
                    DraftAction(
                        action="notify",
                        channels=["telegram"],
                        template="Baterai sensor plot E lemah.",
                    ),
                ],
            ),
        ),
    ]
    plots = ("A", "B", "C", "D", "E", "F", "G", "H")
    for idx, plot in enumerate(plots):
        hour = 5 + (idx % 4)
        rows.append(
            NlExampleRow(
                f"siram plot {plot} setiap hari jam {hour}",
                f"Water plot {plot} daily at {hour}:00",
                _cron_water(f"plot_{plot}", f"0 {hour} * * *"),
            )
        )
    for idx, plot in enumerate(plots):
        threshold = 30 + idx * 2
        minutes = 10 + idx
        rows.append(
            NlExampleRow(
                f"kalau moisture plot {plot} kurang dari {threshold} siram {minutes} menit",
                f"When plot {plot} moisture below {threshold}, irrigate {minutes} min",
                _irrigation(f"plot_{plot}", minutes, float(threshold)),
            )
        )
    extras: list[NlExampleRow] = [
        NlExampleRow(
            "webhook ke ERP kalau yield forecast turun 20 persen",
            "Webhook ERP when yield forecast drops 20%",
            _base_draft(
                name="Yield webhook",
                description="ERP webhook on yield drop.",
                trigger=DraftTrigger(kind=DraftTriggerKind.EVENT, domain="sensor", event_type="reading_update"),
                actions=[DraftAction(action="webhook", webhook_url="https://erp.example/hooks/yield")],
            ),
        ),
        NlExampleRow(
            "matikan lampu greenhouse jam 10 malam",
            "Turn off greenhouse lights at 10 PM",
            _base_draft(
                name="Lights off nightly",
                description="Cron lights off.",
                trigger=DraftTrigger(kind=DraftTriggerKind.CRON, cron="0 22 * * *"),
                actions=[DraftAction(actuator="greenhouse_lamp", action="turn_off")],
            ),
        ),
        NlExampleRow(
            "notif WA kalau NDVI plot F di bawah 0.4",
            "WhatsApp when plot F NDVI below 0.4",
            _base_draft(
                name="NDVI alert",
                description="NDVI stress alert.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.SENSOR_THRESHOLD,
                    sensor="ndvi",
                    operator="lt",
                    threshold=0.4,
                    device="plot_F_ndvi",
                ),
                actions=[
                    DraftAction(action="notify", channels=["whatsapp"], template="NDVI plot F rendah."),
                ],
            ),
        ),
        NlExampleRow(
            "buka ventilasi jika CO2 greenhouse di atas 1200 ppm",
            "Open ventilation if greenhouse CO2 above 1200 ppm",
            _base_draft(
                name="CO2 ventilation",
                description="Vent on high CO2.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.SENSOR_THRESHOLD,
                    sensor="co2",
                    operator="gt",
                    threshold=1200,
                    device="gh_co2",
                ),
                actions=[DraftAction(actuator="vent_fan", action="turn_on")],
            ),
        ),
        NlExampleRow(
            "siram plot H hanya jika suhu di bawah 32 dan tanah kering",
            "Irrigate plot H only if temp below 32 and soil dry",
            _irrigation("plot_H", 18, 35),
        ),
        NlExampleRow(
            "alert medium jika kelembaban udara di bawah 40 persen",
            "Medium alert if air humidity below 40%",
            _base_draft(
                name="Humidity alert",
                description="Low humidity alert.",
                trigger=DraftTrigger(
                    kind=DraftTriggerKind.SENSOR_THRESHOLD,
                    sensor="humidity",
                    operator="lt",
                    threshold=40,
                    device="air_humidity",
                ),
                actions=[DraftAction(action="alarm", severity="medium", template="Kelembaban udara rendah.")],
            ),
        ),
    ]
    rows.extend(extras)
    while len(rows) < 50:
        n = len(rows) + 1
        rows.append(
            NlExampleRow(
                f"contoh otomasi ke-{n}: siram plot auto {n} menit",
                f"Automation example {n}: auto irrigate {n} minutes",
                _irrigation(f"auto_{n}", min(n, 45)),
            )
        )
    return tuple(rows[:50])


NL_EXAMPLES: tuple[NlExampleRow, ...] = _build_dataset()


def list_nl_examples(locale: str = "id") -> list[JsonObject]:
    """Return example prompts for API; locale selects primary prompt text."""
    use_id = locale.lower().startswith("id")
    out: list[JsonObject] = []
    for row in NL_EXAMPLES:
        prompt = row.prompt_id if use_id else row.prompt_en
        draft = row.draft.model_copy(update={"locale": locale[:2]})
        out.append(
            {
                "prompt": prompt,
                "prompt_id": row.prompt_id,
                "prompt_en": row.prompt_en,
                "draft": draft.model_dump(mode="json"),
            }
        )
    return out


def few_shot_block(locale: str = "id", limit: int = 6) -> str:
    """Compact JSON lines for LLM few-shot context."""
    lines: list[str] = []
    for row in NL_EXAMPLES[:limit]:
        prompt = row.prompt_id if locale.startswith("id") else row.prompt_en
        draft_json = row.draft.model_dump(mode="json", exclude={"draft_id", "tenant_id"})
        lines.append(f'User: {prompt}\nDraft: {draft_json}')
    return "\n\n".join(lines)


def match_example_prompt(prompt: str) -> WorkflowDraft | None:
    normalized = prompt.strip().lower()
    for row in NL_EXAMPLES:
        if normalized == row.prompt_id.lower() or normalized == row.prompt_en.lower():
            return row.draft.model_copy(deep=True)
    return None
