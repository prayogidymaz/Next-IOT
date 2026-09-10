from enum import IntEnum, StrEnum


class SecurityTier(StrEnum):
    """Security tiers mapped from Executive_Master_Plan_Security_Tiering.pdf."""

    FREE = "free"  # Tier 1
    PRO = "pro"  # Tier 2
    ENTERPRISE = "enterprise"  # Tier 3


class TierLevel(IntEnum):
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


TIER_TO_LEVEL: dict[SecurityTier, TierLevel] = {
    SecurityTier.FREE: TierLevel.TIER_1,
    SecurityTier.PRO: TierLevel.TIER_2,
    SecurityTier.ENTERPRISE: TierLevel.TIER_3,
}

# Requests per minute (sliding window)
TIER_RATE_LIMITS: dict[SecurityTier, int] = {
    SecurityTier.FREE: 60,
    SecurityTier.PRO: 300,
    SecurityTier.ENTERPRISE: 1000,
}

VALID_TIERS = frozenset(SecurityTier)


def parse_tier(value: str) -> SecurityTier:
    try:
        tier = SecurityTier(value.lower())
    except ValueError as exc:
        raise ValueError(f"Invalid security tier: {value}") from exc
    return tier


def rate_limit_for_tier(tier: SecurityTier) -> int:
    return TIER_RATE_LIMITS[tier]
