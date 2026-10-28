"""Federation client for remote mesh peers."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from app.mesh.federation.messages import FederationMeshEvent


class FederationClient:
    def __init__(self, local_site: str) -> None:
        self._local_site = local_site
        self._remote_events: asyncio.Queue[FederationMeshEvent] = asyncio.Queue()

    async def connect(self, peer_url: str, peer_cert: Path) -> None:
        _ = peer_url, peer_cert

    async def publish_remote(self, event: FederationMeshEvent) -> None:
        await self._remote_events.put(event)

    async def subscribe_remote(self, filter_domains: list[str]) -> AsyncIterator[FederationMeshEvent]:
        while True:
            event = await self._remote_events.get()
            domain = event.payload().get("domain")
            if filter_domains and isinstance(domain, str) and domain not in filter_domains:
                continue
            yield event

    async def sync_devices_bidirectional(self, peer_events: list[FederationMeshEvent]) -> list[FederationMeshEvent]:
        merged: list[FederationMeshEvent] = []
        for event in peer_events:
            merged.append(event)
            await self.publish_remote(event)
        return merged
