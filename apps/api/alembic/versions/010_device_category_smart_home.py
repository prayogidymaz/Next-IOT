"""Device category column + SMART_HOME taxonomy

Revision ID: 010
Revises: 009
Create Date: 2026-09-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "device_category",
            sa.String(length=64),
            nullable=False,
            server_default="FIELD_SENSORS_LORA",
        ),
    )
    op.execute(
        """
        UPDATE devices
        SET device_category = CASE
            WHEN lower(device_type) IN ('smart_home', 'smart_home_building', 'smarthome')
                THEN 'SMART_HOME'
            WHEN lower(device_type) IN ('drone', 'robot', 'uav', 'ugv')
                THEN 'DRONE_UNMANNED'
            WHEN lower(device_type) IN ('lorawan', 'lora', 'lora_sensor')
                THEN 'FIELD_SENSORS_LORA'
            WHEN lower(device_type) IN ('cyberdeck', 'modbus_gateway', 'industrial_gateway')
                THEN 'INDUSTRIAL_TELEMETRY'
            WHEN lower(device_type) IN ('sensor', 'multi_sensor', 'aquaculture', 'agriculture')
                THEN 'AGRICULTURE_AQUACULTURE'
            WHEN lower(device_type) IN ('fleet', 'vehicle', 'asset_tracker')
                THEN 'SMART_ASSET_FLEET'
            ELSE 'FIELD_SENSORS_LORA'
        END
        """
    )
    op.create_index("ix_devices_device_category", "devices", ["device_category"])


def downgrade() -> None:
    op.drop_index("ix_devices_device_category", table_name="devices")
    op.drop_column("devices", "device_category")
