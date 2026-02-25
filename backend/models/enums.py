from enum import StrEnum


class AccessLevel(StrEnum):
    """Represents the access level of a user."""

    UNAUTHENTICATED = "unauthenticated"
    USER = "user"
    CLAP = "clap"
    MANAGER = "manager"
    ADMIN = "admin"


class Condition(StrEnum):
    """Represents the condition of an item in the inventory."""

    NEW = "new"
    GOOD = "good"
    DEGRADED = "degraded"


class Availability(StrEnum):
    """Represents the availability status of an item."""

    AVAILABLE = "available"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
