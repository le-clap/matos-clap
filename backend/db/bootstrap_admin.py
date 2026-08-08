"""Standalone CLI to promote an existing user to admin."""

import sys

from sqlmodel import Session, select

from db.database import engine
from models.enums import AccessLevel
from models.models import User


def promote_to_admin(session: Session, user: User) -> User:
    user.access_level = AccessLevel.ADMIN
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run python -m db.bootstrap_admin <username>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]

    try:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                print(f"No user found with username '{username}'.", file=sys.stderr)
                sys.exit(1)

            if user.access_level == AccessLevel.ADMIN:
                print(f"'{username}' ({user.name}) is already an admin. Nothing to do.")
                sys.exit(0)

            print(f"Found user: {user.name} (current role: {user.access_level})")
            confirmation = input(f"Promote '{username}' to admin? (y/N): ").strip().lower()
            if confirmation != "y":
                print("Operation cancelled.")
                sys.exit(0)

            promote_to_admin(session, user)
            print(f"\n'{username}' is now an admin.")
    except Exception as e:
        print(f"\nFailed to promote user: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
