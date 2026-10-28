"""gRPC servicer bridging protobuf MeshEvent to FederationServer."""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from typing import TYPE_CHECKING

import grpc
from app.mesh.federation import protocol_pb2
from app.mesh.federation.messages import FederationMeshEvent
from app.mesh.federation.protocol_pb2_grpc import MeshFederationServicer

if TYPE_CHECKING:
    from app.mesh.federation.federation_server import FederationServer


class FederationGrpcServicer(MeshFederationServicer):
    def __init__(self, server: FederationServer) -> None:
        self._server = server

    def Peer(
        self,
        request_iterator: Iterator[protocol_pb2.MeshEvent],
        context: grpc.ServicerContext,
    ) -> Iterator[protocol_pb2.MeshEvent]:
        if not self._server.validate_peer_cert(None):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("invalid peer certificate")
            return iter(())
        for pb_event in request_iterator:
            event = FederationMeshEvent.from_proto(pb_event)
            tagged = FederationMeshEvent(
                origin_site=event.origin_site,
                event_type=event.event_type,
                device_id=event.device_id,
                payload_json=event.payload_json,
                timestamp=event.timestamp,
                ttl=max(0, event.ttl - 1),
            )
            yield FederationMeshEvent.to_proto(tagged)

    def SyncDevices(
        self,
        request: protocol_pb2.SyncRequest,
        context: grpc.ServicerContext,
    ) -> protocol_pb2.SyncResponse:
        _ = context
        event = FederationMeshEvent.from_local(
            request.origin_site,
            "sync.devices",
            uuid.uuid4(),
            {"device_ids": list(request.device_ids)},
        )
        return protocol_pb2.SyncResponse(events=[FederationMeshEvent.to_proto(event)])

    def QueryRemote(
        self,
        request: protocol_pb2.RemoteQuery,
        context: grpc.ServicerContext,
    ) -> protocol_pb2.RemoteQueryResult:
        _ = context
        filter_raw = json.loads(request.filter_json or "{}")
        filter_data = filter_raw if isinstance(filter_raw, dict) else {}
        event = FederationMeshEvent.from_local(
            request.origin_site,
            "query.remote",
            uuid.uuid4(),
            filter_data,
        )
        return protocol_pb2.RemoteQueryResult(events=[FederationMeshEvent.to_proto(event)])
