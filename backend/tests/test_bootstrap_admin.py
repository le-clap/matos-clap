"""Tests for the admin bootstrap script."""

from db.bootstrap_admin import promote_to_admin
from models.enums import AccessLevel
from tests.conftest import make_user


def test_promote_to_admin_sets_access_level(session):
    user = make_user(session, AccessLevel.USER, 0)

    promoted = promote_to_admin(session, user)

    assert promoted.access_level == AccessLevel.ADMIN
    session.refresh(user)
    assert user.access_level == AccessLevel.ADMIN


def test_promote_to_admin_is_idempotent(session):
    user = make_user(session, AccessLevel.ADMIN, 1)

    promoted = promote_to_admin(session, user)

    assert promoted.access_level == AccessLevel.ADMIN
