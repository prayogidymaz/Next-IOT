"""Federation client for remote mesh peers."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

import grpc
from app.mesh.federation import protocol_pb2
from app.mesh.federation.messages import FederationMeshEvent
from app.mesh.federation.protocol_pb2_grpc import MeshFederationStub


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

    def sync_devices_grpc(
        self,
        channel: grpc.Channel,
        origin_site: str,
        device_ids: list[str],
    ) -> list[FederationMeshEvent]:
        stub = MeshFederationStub(channel)
        response = stub.SyncDevices(
            protocol_pb2.SyncRequest(origin_site=origin_site, device_ids=device_ids),
        )
        return [FederationMeshEvent.from_proto(item) for item in response.events]
