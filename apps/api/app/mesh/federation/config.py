"""Federation configuration per tenant."""

from __future__ import annotations

from app.mesh.event_bus import MeshDomain
from pydantic import BaseModel, Field


class FederationPeerConfig(BaseModel):
    name: str
    url: str
    cert_path: str | None = None
    enabled: bool = True
    bidirectional: bool = True


class FederationSettings(BaseModel):
    federation_peers: list[FederationPeerConfig] = Field(default_factory=list)
    event_filter: list[MeshDomain] = Field(
        default_factory=lambda: [
            MeshDomain.SENSOR,
            MeshDomain.VISION,
            MeshDomain.MOTION,
            MeshDomain.ACTUATOR,
            MeshDomain.SECURITY,
            MeshDomain.UI,
        ]
    )
