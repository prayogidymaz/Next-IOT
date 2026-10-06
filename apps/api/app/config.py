import os
from urllib.parse import quote_plus, urlparse, urlunparse

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, model_validator


def _url_has_unexpanded_placeholders(url: str) -> bool:
    return "${" in url or "$POSTGRES" in url


def _environment() -> dict[str, object]:
    merged = {**dotenv_values(".env"), **os.environ}
    normalized: dict[str, object] = {}
    for key, value in merged.items():
        if value is None:
            continue
        normalized[key.lower()] = value
    return normalized


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    app_name: str = "Next-IOT"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    db_echo: bool = False
    run_background_workers: bool = True

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "next_iot"
    postgres_user: str = "next_iot"
    postgres_password: str = "changeme"

    database_url: str = "postgresql+asyncpg://next_iot:changeme@localhost:5432/next_iot"
    database_url_sync: str = "postgresql://next_iot:changeme@localhost:5432/next_iot"
    database_url_test: str = ""
    test_database_name: str = "next_iot_test"

    redis_url: str = "redis://localhost:6379/0"
    redis_url_test: str = ""
    redis_test_db_index: int = 15

    jwt_secret_key: str = "change-this-to-a-random-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    device_provisioning_token_expire_hours: int = 24
    device_heartbeat_offline_threshold_seconds: int = 300
    device_offline_check_interval_seconds: int = 60

    firmware_upload_dir: str = "data/firmware_uploads"
    firmware_max_upload_bytes: int = 16_777_216

    telemetry_timestamp_max_future_minutes: int = 5
    telemetry_timestamp_max_past_hours: int = 24

    cors_allow_origins: str = "*"
    cors_allow_credentials: bool = True

    mqtt_broker_host: str = "emqx"
    mqtt_broker_port: int = 1883
    mqtt_broker_timeout_seconds: float = 2.0
    mqtt_broker_url_external: str = "mqtt://localhost:1883"
    mqtt_auth_cache_ttl_seconds: int = 60
    mqtt_webhook_shared_secret: str = "dev-mqtt-webhook-secret"
    emqx_dashboard_url: str = "http://emqx:18083"
    emqx_dashboard_user: str = "admin"
    emqx_dashboard_password: str = ""
    emqx_dashboard_timeout_seconds: float = 10.0
    emqx_telemetry_rule_setup_enabled: bool = True
    emqx_ingest_webhook_url: str = "http://api:8000/api/v1/mqtt/ingest/telemetry"
    device_credential_token_length: int = 36
    device_claim_token_default_ttl_hours: int = 24
    device_claim_token_max_ttl_hours: int = 168

    seed_default_admin: bool = True
    seed_admin_email: str = "admin@nextiot.com"
    seed_admin_password: str = "admin123"
    seed_admin_display_name: str = "System Admin"
    seed_tenant_name: str = "Next-IOT Platform"
    seed_tenant_slug: str = "nextiot"
    seed_demo_telemetry: bool = True

    notification_dispatcher_enabled: bool = True
    notification_poll_interval_seconds: float = 1.0
    notification_max_retries: int = 3
    notification_retry_delay_seconds: float = 0.5

    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    default_telegram_chat_id: str = ""
    telegram_parse_mode: str = "HTML"

    webhook_enabled: bool = False
    webhook_url: str = ""
    webhook_secret: str = ""
    webhook_timeout_seconds: float = 10.0
    webhook_signature_header: str = "X-NextIOT-Signature"

    drone_simulator_tick_seconds: float = 1.0
    drone_simulator_default_altitude_m: float = 60.0
    drone_simulator_default_latitude: float = -6.2088
    drone_simulator_default_longitude: float = 106.8456
    drone_simulator_min_steps: int = 5
    drone_simulator_max_steps: int = 20

    lora_bridge_serial_port: str = "COM3"
    lora_bridge_baud_rate: int = 115200
    lora_bridge_api_base_url: str = "http://localhost:8000"
    lora_bridge_default_node_id: str = "DRONE-01"
    lora_bridge_demo_device_name: str = "Demo Sensor Node"
    lora_bridge_default_client_id: str = ""
    lora_bridge_default_client_secret: str = ""
    lora_gateway_status_ttl_seconds: int = 30
    lora_encryption_key: str = ""
    lora_encryption_enabled: bool = False
    lora_encryption_mode: str = "AES-128-CBC"
    drone_simulator_lora_encrypt_mock: bool = False

    telemetry_compression_after_days: int = 7
    telemetry_retention_free_days: int = 7
    telemetry_retention_pro_days: int = 90
    telemetry_retention_enterprise_days: int = 730
    telemetry_validation_strict_mode: bool = False

    tile_server_url: str = "http://tile-server:8080"
    tile_server_service: str = "offline-map"
    tile_server_port: int = 8080
    tile_proxy_timeout_seconds: float = 5.0

    def redis_url_for_tests(self) -> str:
        """Isolated Redis for pytest (separate DB index or explicit REDIS_URL_TEST)."""
        explicit = self.redis_url_test.strip()
        if explicit:
            return explicit
        parsed = urlparse(self.redis_url)
        return urlunparse(parsed._replace(path=f"/{self.redis_test_db_index}"))

    @staticmethod
    def redis_location_from_url(url: str) -> tuple[str, int, int]:
        """Return (host, port, db_index) for comparing Redis endpoints."""
        parsed = urlparse(url)
        host = (parsed.hostname or "localhost").lower()
        port = parsed.port if parsed.port is not None else 6379
        path_segment = parsed.path.lstrip("/").split("/", 1)[0]
        db_index = int(path_segment) if path_segment.isdigit() else 0
        return (host, port, db_index)

    def assert_test_redis_isolated(self) -> None:
        """Refuse pytest FLUSHDB when test Redis targets the same DB as the application."""
        app_location = self.redis_location_from_url(self.redis_url)
        test_location = self.redis_location_from_url(self.redis_url_for_tests())
        if app_location == test_location:
            raise RuntimeError("Refusing to FLUSHDB: test Redis points to application Redis")

    @staticmethod
    def database_name_from_url(url: str) -> str:
        segment = urlparse(url).path.lstrip("/").split("/", 1)[0]
        return segment

    def resolved_test_database_name(self) -> str:
        explicit = self.test_database_name.strip()
        if explicit:
            return explicit
        base = self.postgres_db.strip() or self.database_name_from_url(self.database_url_sync)
        if base.endswith("_test"):
            return base
        return f"{base}_test"

    @staticmethod
    def _replace_url_database(url: str, db_name: str) -> str:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(path=f"/{db_name}"))

    def database_url_for_tests(self) -> str:
        """Async SQLAlchemy URL for pytest (DATABASE_URL_TEST or <app_db>_test)."""
        explicit = self.database_url_test.strip()
        if explicit:
            return explicit
        return self._replace_url_database(self.database_url, self.resolved_test_database_name())

    def database_url_sync_for_tests(self) -> str:
        """Psycopg2 / Alembic URL for pytest."""
        explicit = self.database_url_test.strip()
        if explicit:
            return explicit.replace("postgresql+asyncpg://", "postgresql://", 1)
        return self._replace_url_database(self.database_url_sync, self.resolved_test_database_name())

    def admin_postgres_url(self) -> str:
        return self._replace_url_database(self.database_url_sync, "postgres")

    def assert_test_database_name(self, db_name: str) -> None:
        if not db_name.endswith("_test"):
            raise RuntimeError(f"Refusing to truncate non-test database: {db_name}")

    def assert_test_database_url(self, sync_url: str) -> None:
        self.assert_test_database_name(self.database_name_from_url(sync_url))

    def build_database_url(self, *, async_driver: bool) -> str:
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        host = self.postgres_host
        port = self.postgres_port
        db = self.postgres_db
        if async_driver:
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    @model_validator(mode="after")
    def assemble_database_urls(self) -> "Settings":
        if _url_has_unexpanded_placeholders(self.database_url):
            self.database_url = self.build_database_url(async_driver=True)
        if _url_has_unexpanded_placeholders(self.database_url_sync):
            self.database_url_sync = self.build_database_url(async_driver=False)
        return self

    @property
    def cors_allow_origin_regex(self) -> str | None:
        """Match any localhost port (Flutter Web uses ephemeral ports e.g. 55921)."""
        raw = self.cors_allow_origins.strip()
        if raw == "*" and self.app_env == "development":
            return r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
        return None

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.cors_allow_origins.strip()
        if raw == "*":
            if self.cors_allow_origin_regex:
                return []
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings.model_validate(_environment())
