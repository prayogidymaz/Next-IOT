"""gRPC federation server (JSON payload handlers + mTLS hook)."""

from __future__ import annotations

import asyncio
import hashlib
import logging
from collections.abc import AsyncIterator
from typing import Protocol

from app.mesh.federation.messages import FederationMeshEvent

logger = logging.getLogger(__name__)


class PeerAuthenticator(Protocol):
    def validate_peer(self, cert_pem: bytes | None) -> bool: ...


class AllowlistAuthenticator:
    def __init__(self, allowed_fingerprints: set[str]) -> None:
        self._allowed = allowed_fingerprints

    def validate_peer(self, cert_pem: bytes | None) -> bool:
        if cert_pem is None:
            return False
        fingerprint = hashlib.sha256(cert_pem).hexdigest()
        return fingerprint in self._allowed


class FederationServer:
    def __init__(self, site_name: str, authenticator: PeerAuthenticator) -> None:
        self._site_name = site_name
        self._authenticator = authenticator
        self._inbound: asyncio.Queue[FederationMeshEvent] = asyncio.Queue()
        self._server: object | None = None

    @property
    def inbound(self) -> asyncio.Queue[FederationMeshEvent]:
        return self._inbound

    async def handle_peer_stream(self, events: AsyncIterator[FederationMeshEvent], peer_cert: bytes | None) -> None:
        if not self._authenticator.validate_peer(peer_cert):
            raise PermissionError("invalid peer certificate")
        async for event in events:
            tagged = FederationMeshEvent(
                origin_site=event.origin_site,
                event_type=event.event_type,
                device_id=event.device_id,
                payload_json=event.payload_json,
                timestamp=event.timestamp,
                ttl=max(0, event.ttl - 1),
            )
            await self._inbound.put(tagged)

    async def serve(self, port: int = 50051) -> None:
        try:
            import grpc
            from grpc import aio
        except ImportError:
            logger.warning("grpcio not installed; federation server running in-process only")
            return
        server = aio.server()
        self._server = server
        server.add_insecure_port(f"[::]:{port}")
        await server.start()
        logger.info("Federation gRPC server listening on %s", port)

    async def stop(self) -> None:
        if self._server is not None:
            stop = getattr(self._server, "stop", None)
            if stop is not None:
                await stop(5)
