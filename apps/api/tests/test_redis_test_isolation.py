import pytest
from app.config import Settings


def test_assert_test_redis_isolated_raises_when_same_endpoint() -> None:
    cfg = Settings(
        redis_url="redis://redis:6379/0",
        redis_url_test="redis://redis:6379/0",
    )
    with pytest.raises(RuntimeError, match="Refusing to FLUSHDB: test Redis points to application Redis"):
        cfg.assert_test_redis_isolated()


def test_assert_test_redis_isolated_allows_separate_db_index() -> None:
    cfg = Settings(
        redis_url="redis://redis:6379/0",
        redis_url_test="",
        redis_test_db_index=15,
    )
    cfg.assert_test_redis_isolated()
