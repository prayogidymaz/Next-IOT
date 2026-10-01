from app.config import Settings


def test_assembles_database_url_when_env_has_placeholders():
    settings = Settings(
        postgres_host="postgres",
        postgres_port=5432,
        postgres_db="next_iot",
        postgres_user="next_iot",
        postgres_password="changeme",
        database_url="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}",
        database_url_sync="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}",
    )
    assert "asyncpg://next_iot:changeme@postgres:5432/next_iot" in settings.database_url
    assert settings.database_url_sync == "postgresql://next_iot:changeme@postgres:5432/next_iot"
