from urllib.parse import quote_plus, urlparse, urlunparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _url_has_unexpanded_placeholders(url: str) -> bool:
    return "${" in url or "$POSTGRES" in url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Next-IOT"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "next_iot"
    postgres_user: str = "next_iot"
    postgres_password: str = "changeme"

    database_url: str = "postgresql+asyncpg://next_iot:changeme@localhost:5432/next_iot"
    database_url_sync: str = "postgresql://next_iot:changeme@localhost:5432/next_iot"
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

    mqtt_broker_host: str = ""
    mqtt_broker_port: int = 1883
    mqtt_broker_timeout_seconds: float = 2.0

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


settings = Settings()
