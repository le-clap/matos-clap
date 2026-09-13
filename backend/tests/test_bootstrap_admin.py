"""Tests for the admin bootstrap script."""

from sqlmodel import select

from db.bootstrap_admin import DEFAULT_EMAIL_DOMAIN, create_admin, promote_to_admin
from models.enums import AccessLevel
from models.models import User
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


def test_create_admin_makes_an_admin_account(session):
    user = create_admin(session, "david")

    assert user.id is not None
    assert user.username == "david"
    assert user.access_level == AccessLevel.ADMIN


def test_create_admin_derives_name_and_email_from_username(session):
    user = create_admin(session, "david")

    assert user.name == "david"
    assert user.email == f"david@{DEFAULT_EMAIL_DOMAIN}"


def test_create_admin_is_findable_by_username(session):
    create_admin(session, "david")

    found = session.exec(select(User).where(User.username == "david")).first()
    assert found is not None
    assert found.access_level == AccessLevel.ADMIN
