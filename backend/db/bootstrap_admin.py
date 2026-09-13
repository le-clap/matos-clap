"""Standalone CLI to create or promote a user to admin."""

import argparse
import sys

from sqlmodel import Session, select

from db.database import engine
from models.enums import AccessLevel
from models.models import User

DEFAULT_EMAIL_DOMAIN = "centralelille.fr"


def promote_to_admin(session: Session, user: User) -> User:
    user.access_level = AccessLevel.ADMIN
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_admin(session: Session, username: str) -> User:
    user = User(
        username=username,
        name=username,
        email=f"{username}@{DEFAULT_EMAIL_DOMAIN}",
        access_level=AccessLevel.ADMIN,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="uv run python -m db.bootstrap_admin",
        description="Create or promote a user to admin.",
    )
    parser.add_argument("username", help="CLA SSO username of the account")
    parser.add_argument(
        "--create",
        action="store_true",
        help="create the account as admin if it does not exist yet",
    )
    parser.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    return parser.parse_args(argv)


def _confirm(question: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    return input(f"{question} (y/N): ").strip().lower() == "y"


def main() -> None:
    args = _parse_args()
    username = args.username

    try:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()

            if not user:
                if not args.create:
                    print(
                        f"No user found with username '{username}'.\n"
                        f"Have them log in once through the CLA SSO, or pass --create to make the account now.",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                if not _confirm(f"Create '{username}' as a new admin?", args.yes):
                    print("Operation cancelled.")
                    sys.exit(0)

                user = create_admin(session, username)
                print(f"\n'{username}' ({user.email}) created as an admin.")
                sys.exit(0)

            if user.access_level == AccessLevel.ADMIN:
                print(f"'{username}' ({user.name}) is already an admin. Nothing to do.")
                sys.exit(0)

            print(f"Found user: {user.name} (current role: {user.access_level})")
            if not _confirm(f"Promote '{username}' to admin?", args.yes):
                print("Operation cancelled.")
                sys.exit(0)

            promote_to_admin(session, user)
            print(f"\n'{username}' is now an admin.")
    except Exception as e:
        print(f"\nFailed to bootstrap admin: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
