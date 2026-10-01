import pytest
from app.config import Settings


def test_assert_test_database_name_rejects_live_db() -> None:
    cfg = Settings()
    with pytest.raises(RuntimeError, match="Refusing to truncate non-test database: next_iot"):
        cfg.assert_test_database_name("next_iot")


def test_assert_test_database_name_allows_test_suffix() -> None:
    cfg = Settings()
    cfg.assert_test_database_name("next_iot_test")


def test_database_url_for_tests_derives_suffix() -> None:
    cfg = Settings(
        postgres_db="next_iot",
        database_url="postgresql+asyncpg://u:p@postgres:5432/next_iot",
        database_url_sync="postgresql://u:p@postgres:5432/next_iot",
        test_database_name="next_iot_test",
    )
    assert cfg.database_url_for_tests().endswith("/next_iot_test")
    assert cfg.database_url_sync_for_tests().endswith("/next_iot_test")


def test_database_url_test_override() -> None:
    cfg = Settings(
        database_url_test="postgresql+asyncpg://u:p@postgres:5432/custom_test",
        database_url="postgresql+asyncpg://u:p@postgres:5432/next_iot",
        database_url_sync="postgresql://u:p@postgres:5432/next_iot",
    )
    assert cfg.database_url_for_tests() == "postgresql+asyncpg://u:p@postgres:5432/custom_test"
    assert cfg.database_url_sync_for_tests() == "postgresql://u:p@postgres:5432/custom_test"
