from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Next-IOT"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    database_url: str = "postgresql+asyncpg://next_iot:changeme@localhost:5432/next_iot"
    database_url_sync: str = "postgresql://next_iot:changeme@localhost:5432/next_iot"
    test_database_name: str = "next_iot_test"

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-this-to-a-random-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    device_provisioning_token_expire_hours: int = 24
    device_heartbeat_offline_threshold_seconds: int = 300
    device_offline_check_interval_seconds: int = 60

    telemetry_timestamp_max_future_minutes: int = 5
    telemetry_timestamp_max_past_hours: int = 24

    cors_allow_origins: str = "*"
    cors_allow_credentials: bool = False

    seed_default_admin: bool = True
    seed_admin_email: str = "admin@nextiot.com"
    seed_admin_password: str = "admin123"
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

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.cors_allow_origins.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()
