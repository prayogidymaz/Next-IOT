"""TimescaleDB hypertable for telemetry_readings

Revision ID: 015
Revises: 014
Create Date: 2026-10-06

"""
from typing import Sequence, Union

from alembic import op

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    op.execute(
        "ALTER TABLE telemetry_anomalies DROP CONSTRAINT IF EXISTS telemetry_anomalies_reading_id_fkey"
    )

    # Hypertable requires partition key in primary key; id-only FK is invalid on hypertables (re-added on downgrade).
    op.execute("ALTER TABLE telemetry_readings DROP CONSTRAINT telemetry_readings_pkey")

    op.execute(
        """
        SELECT create_hypertable(
            'telemetry_readings',
            'recorded_at',
            chunk_time_interval => INTERVAL '1 day',
            migrate_data => true
        )
        """
    )

    op.execute("ALTER TABLE telemetry_readings ADD PRIMARY KEY (recorded_at, id)")

    op.execute(
        """
        ALTER TABLE telemetry_readings SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'device_id, tenant_id'
        )
        """
    )
    op.execute("SELECT add_compression_policy('telemetry_readings', INTERVAL '7 days')")


def downgrade() -> None:
    op.execute("SELECT remove_compression_policy('telemetry_readings', if_exists => true)")
    op.execute("ALTER TABLE telemetry_readings SET (timescaledb.compress = false)")

    op.execute(
        """
        SELECT decompress_chunk(i, if_compressed => true)
        FROM show_chunks('telemetry_readings') i
        """
    )

    op.execute("ALTER TABLE telemetry_anomalies DROP CONSTRAINT IF EXISTS telemetry_anomalies_reading_id_fkey")

    op.execute(
        """
        CREATE TABLE telemetry_readings_plain (
            id UUID NOT NULL,
            device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            recorded_at TIMESTAMPTZ NOT NULL,
            metrics JSONB NOT NULL,
            ingested_at TIMESTAMPTZ DEFAULT now()
        )
        """
    )
    op.execute("INSERT INTO telemetry_readings_plain SELECT * FROM telemetry_readings")
    op.execute("DROP TABLE telemetry_readings")
    op.execute("ALTER TABLE telemetry_readings_plain RENAME TO telemetry_readings")

    op.execute("ALTER TABLE telemetry_readings ADD PRIMARY KEY (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_readings_device_id ON telemetry_readings (device_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_readings_tenant_id ON telemetry_readings (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_readings_recorded_at ON telemetry_readings (recorded_at)")

    op.execute(
        """
        ALTER TABLE telemetry_anomalies
        ADD CONSTRAINT telemetry_anomalies_reading_id_fkey
        FOREIGN KEY (reading_id) REFERENCES telemetry_readings(id) ON DELETE SET NULL
        """
    )

    op.execute("DROP EXTENSION IF EXISTS timescaledb CASCADE")
