from enum import StrEnum

MAVLINK_PROTOCOL_VERSION = "2.0"

SUPPORTED_INBOUND_TYPES = frozenset(
    {"HEARTBEAT", "GLOBAL_POSITION_INT", "SYS_STATUS", "ATTITUDE"}
)

SUPPORTED_COMMANDS = frozenset({"ARM", "DISARM", "RTL", "LAND", "WAYPOINT"})


class MavlinkCommandType(StrEnum):
    ARM = "ARM"
    DISARM = "DISARM"
    RTL = "RTL"
    LAND = "LAND"
    WAYPOINT = "WAYPOINT"
