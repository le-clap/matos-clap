from enum import StrEnum


class AccessLevel(StrEnum):
    """Represents the access level of a user."""

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


class LoanStatus(StrEnum):
    """Represents the status of a loan."""

    SCHEDULED = "scheduled"
    ACTIVE = "active"
    RETURNED = "returned"


class RequestStatus(StrEnum):
    """Represents the status of a request."""

    PENDING = "pending"
    REFUSED = "refused"
    APPROVED = "approved"
