"""Async LLM client for mesh workflow generation (Anthropic + mock fallback)."""

from __future__ import annotations

import json
import logging

import httpx

from app.config import settings
from app.mesh.ai_copilot.examples import workflow_for_prompt
from app.types.json_types import JsonObject

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Next-IOT Mesh Copilot. Convert user requests into JSON for MeshWorkflowDefinition.
Schema summary:
- name, description, enabled (bool)
- trigger: {type: mesh_event|schedule|manual, filter?: {domain, event_type, payload_match, schedule_cron, time_filter}}
- conditions: optional list with type, device_resolver {capability, zone, farm_id, device_id}, attribute/state_match
- actions: list of {id, type: dispatch_device|trigger_device|wait_for_event|notification|...}

Domains: sensor, vision, actuator, security, ui, workflow, motion.
Respond with ONLY valid JSON object matching MeshWorkflowDefinition (no markdown).
""".strip()


class LLMClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key.strip()
        self._model = model.strip() or "claude-sonnet-4-5"

    @classmethod
    def from_settings(cls) -> LLMClient:
        return cls(settings.anthropic_api_key, settings.llm_model)

    @property
    def mock_mode(self) -> bool:
        return not self._api_key

    async def generate_workflow(self, prompt: str, context: JsonObject) -> JsonObject:
        if self.mock_mode:
            wf = workflow_for_prompt(prompt)
            return {
                "workflow": wf.model_dump(mode="json"),
                "explanation": "Mock mode: matched prompt to canned mesh workflow template.",
                "confidence": 0.85,
                "context_applied": context,
            }

        user_body = json.dumps({"prompt": prompt, "context": context}, ensure_ascii=False)
        payload = {
            "model": self._model,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_body}],
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
        workflow_json = json.loads(text)
        return {
            "workflow": workflow_json,
            "explanation": "Generated via Anthropic Messages API.",
            "confidence": 0.9,
            "context_applied": context,
        }


def _extract_text(data: JsonObject) -> str:
    content = data.get("content")
    if not isinstance(content, list):
        raise ValueError("Unexpected LLM response shape")
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str):
                return text.strip()
    raise ValueError("No text block in LLM response")
