from sqlmodel import Session, select
from db.database import engine
from models.models import Condition, Availability, Access

def seed_data():
    with Session(engine) as session:
        # 1. Seed Conditions
        if not session.exec(select(Condition)).first():
            conditions = [
                Condition(name="NEW", description="Brand new equipment"),
                Condition(name="GOOD", description="Used but fully functional"),
                Condition(name="DEGRADED", description="Functional but has visible wear")
            ]
            session.add_all(conditions)

        # 2. Seed Availability
        if not session.exec(select(Availability)).first():
            statuses = [
                Availability(name="Available"),
                Availability(name="On Loan"),
                Availability(name="Maintenance"),
                Availability(name="Retired")
            ]
            session.add_all(statuses)

        # 3. Seed Access Roles
        if not session.exec(select(Access)).first():
            roles = [
                Access(name="Admin"),
                Access(name="Manager"),
                Access(name="User")
            ]
            session.add_all(roles)

        session.commit()
        print("Database seeded successfully!")