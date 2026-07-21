import sys
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, text

from db.database import engine
from models.enums import AccessLevel, Availability, Condition, RequestStatus
from models.models import Catalog, Category, Item, Loan, LoanedItem, Request, RequestedCatalog, User, UserSession


def seed_db(session: Session) -> None:
    """Deletes the existing data and loads test data into the database."""
    print("Cleaning database tables...")

    tables_to_truncate = [
        "loaned_item",
        "loan",
        "requested_catalog",
        "request",
        "user_session",
        "item",
        "catalog",
        "category",
        "matos_user",
    ]

    for table in tables_to_truncate:
        session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))  # ty: ignore[deprecated]

    print("Injecting new seed data...")
    now = datetime.now(UTC)

    users = [
        User(
            username="admin_alice",
            name="Alice Martin",
            email="alice.martin@le-clap.fr",
            access_level=AccessLevel.ADMIN,
            created_at=now - timedelta(days=180),
            updated_at=now - timedelta(days=1),
        ),
        User(
            username="clap_marie",
            name="Marie Dupont",
            email="marie.dupont@le-clap.fr",
            access_level=AccessLevel.CLAP,
            created_at=now - timedelta(days=220),
            updated_at=now - timedelta(days=1),
        ),
        User(
            username="clap_lucas",
            name="Lucas Bernard",
            email="lucas.bernard@le-clap.fr",
            access_level=AccessLevel.CLAP,
            created_at=now - timedelta(days=140),
            updated_at=now - timedelta(days=3),
        ),
        User(
            username="manager_nora",
            name="Nora Petit",
            email="nora.petit@le-clap.fr",
            access_level=AccessLevel.MANAGER,
            created_at=now - timedelta(days=260),
            updated_at=now - timedelta(days=2),
        ),
        User(
            username="manager_omar",
            name="Omar Leroy",
            email="omar.leroy@le-clap.fr",
            access_level=AccessLevel.MANAGER,
            created_at=now - timedelta(days=120),
            updated_at=now - timedelta(days=4),
        ),
        User(
            username="user_zoe",
            name="Zoe Richard",
            email="zoe.richard@centrale.centralelille.fr",
            access_level=AccessLevel.USER,
            created_at=now - timedelta(days=90),
            updated_at=now - timedelta(days=1),
        ),
        User(
            username="user_hugo",
            name="Hugo Garcia",
            email="hugo.garcia@centrale.centralelille.fr",
            access_level=AccessLevel.USER,
            created_at=now - timedelta(days=95),
            updated_at=now - timedelta(days=6),
        ),
        User(
            username="user_lina",
            name="Lina Moreau",
            email="lina.moreau@iteem.centralelille.fr",
            access_level=AccessLevel.USER,
            created_at=now - timedelta(days=70),
            updated_at=now - timedelta(days=5),
        ),
        User(
            username="user_noah",
            name="Noah Simon",
            email="noah.simon@enscl.centralelille.fr",
            access_level=AccessLevel.USER,
            created_at=now - timedelta(days=40),
            updated_at=now - timedelta(days=2),
        ),
    ]
    session.add_all(users)
    session.flush()

    sessions = [
        UserSession(
            token="sess_admin_alice_active_01",
            user_id=1,
            expires_at=now + timedelta(days=20),
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=1),
        ),
        UserSession(
            token="sess_clap_marie_active_01",
            user_id=2,
            expires_at=now + timedelta(days=15),
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=1),
        ),
        UserSession(
            token="sess_clap_lucas_bearer_01",
            user_id=3,
            expires_at=now + timedelta(days=7),
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=2),
        ),
        UserSession(
            token="sess_user_zoe_active_01",
            user_id=6,
            expires_at=now + timedelta(days=12),
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=1),
        ),
        UserSession(
            token="sess_user_hugo_expired_01",
            user_id=7,
            expires_at=now - timedelta(days=2),
            created_at=now - timedelta(days=25),
            updated_at=now - timedelta(days=2),
        ),
    ]
    session.add_all(sessions)
    session.flush()

    categories = [
        Category(
            name="Camera",
            description="Boitiers et optiques cinema",
            created_at=now - timedelta(days=300),
            updated_at=now - timedelta(days=20),
        ),
        Category(
            name="Sound",
            description="Prise de son et accessoires",
            created_at=now - timedelta(days=300),
            updated_at=now - timedelta(days=20),
        ),
        Category(
            name="Lighting",
            description="Projecteurs et accessoires lumiere",
            created_at=now - timedelta(days=300),
            updated_at=now - timedelta(days=20),
        ),
        Category(
            name="Grip",
            description="Supports, stabilisation, machinerie",
            created_at=now - timedelta(days=300),
            updated_at=now - timedelta(days=20),
        ),
        Category(
            name="Monitoring",
            description="Enregistrement et monitoring plateau",
            created_at=now - timedelta(days=300),
            updated_at=now - timedelta(days=20),
        ),
    ]
    session.add_all(categories)
    session.flush()

    catalogs = [
        Catalog(
            name="Sony A7S III",
            description="Boitier plein format orienté faible lumière",
            category_id=1,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=12),
        ),
        Catalog(
            name="Blackmagic Pocket 6K Pro",
            description="Boitier Super35 avec ND intégrés",
            category_id=1,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=15),
        ),
        Catalog(
            name="Zoom H6",
            description="Enregistreur portable 6 pistes",
            category_id=2,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=6),
        ),
        Catalog(
            name="Rode NTG3 Kit",
            description="Micro canon + perche + bonnette",
            category_id=2,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=8),
        ),
        Catalog(
            name="Aputure 300D II",
            description="Projecteur LED daylight puissant",
            category_id=3,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=9),
        ),
        Catalog(
            name="Nanlite PavoTube 30C",
            description="Tube RGB pour ambiances",
            category_id=3,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=5),
        ),
        Catalog(
            name="Manfrotto 504HD",
            description="Trépied vidéo avec tête fluide",
            category_id=4,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=10),
        ),
        Catalog(
            name="DJI RS 3",
            description="Stabilisateur 3 axes",
            category_id=4,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=7),
        ),
        Catalog(
            name="Atomos Ninja V",
            description="Moniteur enregistreur HDMI",
            category_id=5,
            created_at=now - timedelta(days=280),
            updated_at=now - timedelta(days=3),
        ),
    ]
    session.add_all(catalogs)
    session.flush()

    items = [
        Item(
            name="CAM-A7S-01",
            catalog_id=1,
            condition=Condition.NEW,
            availability=Availability.AVAILABLE,
            deposit_cents=250000,
            deleted_at=None,
            created_at=now - timedelta(days=260),
            updated_at=now - timedelta(days=2),
        ),
        Item(
            name="CAM-A7S-02",
            catalog_id=1,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=250000,
            deleted_at=None,
            created_at=now - timedelta(days=250),
            updated_at=now - timedelta(days=3),
        ),
        Item(
            name="CAM-A7S-03",
            catalog_id=1,
            condition=Condition.DEGRADED,
            availability=Availability.MAINTENANCE,
            deposit_cents=220000,
            deleted_at=None,
            created_at=now - timedelta(days=240),
            updated_at=now - timedelta(days=1),
        ),
        Item(
            name="CAM-BMP-01",
            catalog_id=2,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=230000,
            deleted_at=None,
            created_at=now - timedelta(days=220),
            updated_at=now - timedelta(days=3),
        ),
        Item(
            name="CAM-BMP-02",
            catalog_id=2,
            condition=Condition.DEGRADED,
            availability=Availability.RETIRED,
            deposit_cents=180000,
            deleted_at=None,
            created_at=now - timedelta(days=210),
            updated_at=now - timedelta(days=10),
        ),
        Item(
            name="SND-H6-01",
            catalog_id=3,
            condition=Condition.NEW,
            availability=Availability.AVAILABLE,
            deposit_cents=30000,
            deleted_at=None,
            created_at=now - timedelta(days=200),
            updated_at=now - timedelta(days=5),
        ),
        Item(
            name="SND-H6-02",
            catalog_id=3,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=30000,
            deleted_at=None,
            created_at=now - timedelta(days=195),
            updated_at=now - timedelta(days=6),
        ),
        Item(
            name="SND-NTG3-01",
            catalog_id=4,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=45000,
            deleted_at=None,
            created_at=now - timedelta(days=190),
            updated_at=now - timedelta(days=4),
        ),
        Item(
            name="SND-NTG3-02",
            catalog_id=4,
            condition=Condition.DEGRADED,
            availability=Availability.AVAILABLE,
            deposit_cents=35000,
            deleted_at=None,
            created_at=now - timedelta(days=185),
            updated_at=now - timedelta(days=8),
        ),
        Item(
            name="LGT-300D-01",
            catalog_id=5,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=90000,
            deleted_at=None,
            created_at=now - timedelta(days=180),
            updated_at=now - timedelta(days=3),
        ),
        Item(
            name="LGT-300D-02",
            catalog_id=5,
            condition=Condition.DEGRADED,
            availability=Availability.MAINTENANCE,
            deposit_cents=70000,
            deleted_at=None,
            created_at=now - timedelta(days=175),
            updated_at=now - timedelta(days=1),
        ),
        Item(
            name="LGT-TUBE-01",
            catalog_id=6,
            condition=Condition.NEW,
            availability=Availability.AVAILABLE,
            deposit_cents=20000,
            deleted_at=None,
            created_at=now - timedelta(days=170),
            updated_at=now - timedelta(days=2),
        ),
        Item(
            name="LGT-TUBE-02",
            catalog_id=6,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=20000,
            deleted_at=None,
            created_at=now - timedelta(days=169),
            updated_at=now - timedelta(days=2),
        ),
        Item(
            name="LGT-TUBE-03",
            catalog_id=6,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=20000,
            deleted_at=None,
            created_at=now - timedelta(days=168),
            updated_at=now - timedelta(days=2),
        ),
        Item(
            name="GRP-504-01",
            catalog_id=7,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=15000,
            deleted_at=None,
            created_at=now - timedelta(days=165),
            updated_at=now - timedelta(days=4),
        ),
        Item(
            name="GRP-504-02",
            catalog_id=7,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=15000,
            deleted_at=None,
            created_at=now - timedelta(days=164),
            updated_at=now - timedelta(days=4),
        ),
        Item(
            name="GRP-RS3-01",
            catalog_id=8,
            condition=Condition.NEW,
            availability=Availability.AVAILABLE,
            deposit_cents=80000,
            deleted_at=None,
            created_at=now - timedelta(days=160),
            updated_at=now - timedelta(days=2),
        ),
        Item(
            name="GRP-RS3-02",
            catalog_id=8,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=80000,
            deleted_at=None,
            created_at=now - timedelta(days=158),
            updated_at=now - timedelta(days=3),
        ),
        Item(
            name="MON-NINJA-01",
            catalog_id=9,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=60000,
            deleted_at=None,
            created_at=now - timedelta(days=150),
            updated_at=now - timedelta(days=2),
        ),
        Item(
            name="MON-NINJA-02",
            catalog_id=9,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=60000,
            deleted_at=None,
            created_at=now - timedelta(days=149),
            updated_at=now - timedelta(days=2),
        ),
        Item(
            name="MON-NINJA-03",
            catalog_id=9,
            condition=Condition.DEGRADED,
            availability=Availability.RETIRED,
            deposit_cents=40000,
            deleted_at=None,
            created_at=now - timedelta(days=148),
            updated_at=now - timedelta(days=15),
        ),
        Item(
            name="CAM-A7S-OLD-01",
            catalog_id=1,
            condition=Condition.DEGRADED,
            availability=Availability.RETIRED,
            deposit_cents=100000,
            deleted_at=now - timedelta(days=20),
            created_at=now - timedelta(days=400),
            updated_at=now - timedelta(days=20),
        ),
        Item(
            name="SND-H6-OLD-01",
            catalog_id=3,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=20000,
            deleted_at=now - timedelta(days=3),
            created_at=now - timedelta(days=390),
            updated_at=now - timedelta(days=3),
        ),
        Item(
            name="GRP-RS3-03",
            catalog_id=8,
            condition=Condition.GOOD,
            availability=Availability.AVAILABLE,
            deposit_cents=75000,
            deleted_at=None,
            created_at=now - timedelta(days=147),
            updated_at=now - timedelta(days=2),
        ),
    ]
    session.add_all(items)
    session.flush()

    requests = [
        Request(
            borrower_id=6,
            phone_number="+33612345678",
            start_date=now + timedelta(days=3),
            end_date=now + timedelta(days=6),
            reason="Court metrage de fin d etudes",
            status=RequestStatus.PENDING,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2),
        ),
        Request(
            borrower_id=7,
            phone_number="+33623456789",
            start_date=now - timedelta(days=15),
            end_date=now - timedelta(days=12),
            reason="Captation interview documentaire",
            status=RequestStatus.APPROVED,
            created_at=now - timedelta(days=18),
            updated_at=now - timedelta(days=12),
        ),
        Request(
            borrower_id=8,
            phone_number="+33634567890",
            start_date=now + timedelta(days=7),
            end_date=now + timedelta(days=9),
            reason="Clip musical multi-cameras",
            status=RequestStatus.REFUSED,
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        ),
        Request(
            borrower_id=9,
            phone_number="+33645678901",
            start_date=now - timedelta(days=2),
            end_date=now + timedelta(days=4),
            reason="Tournage evenement associatif",
            status=RequestStatus.APPROVED,
            created_at=now - timedelta(days=4),
            updated_at=now - timedelta(days=2),
        ),
    ]
    session.add_all(requests)
    session.flush()

    requested_catalogs = [
        RequestedCatalog(request_id=1, catalog_id=1, quantity=1),
        RequestedCatalog(request_id=1, catalog_id=6, quantity=2),
        RequestedCatalog(request_id=2, catalog_id=3, quantity=1),
        RequestedCatalog(request_id=2, catalog_id=7, quantity=1),
        RequestedCatalog(request_id=3, catalog_id=1, quantity=4),
        RequestedCatalog(request_id=3, catalog_id=9, quantity=2),
        RequestedCatalog(request_id=4, catalog_id=2, quantity=1),
        RequestedCatalog(request_id=4, catalog_id=8, quantity=1),
    ]
    session.add_all(requested_catalogs)
    session.flush()

    loans = [
        Loan(
            borrower_id=7,
            assignee_id=2,
            start_date=now - timedelta(days=15),
            end_date=now - timedelta(days=12),
            total_deposit_cents=45000,
            actual_start_date=now - timedelta(days=15),
            actual_return_date=now - timedelta(days=12),
            retained_deposit_cents=5000,
            request_id=2,
            comments="Retour avec légère usure du trépied",
            created_at=now - timedelta(days=16),
            updated_at=now - timedelta(days=12),
        ),
        Loan(
            borrower_id=6,
            assignee_id=3,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=2),
            total_deposit_cents=310000,
            actual_start_date=now - timedelta(days=1),
            actual_return_date=None,
            retained_deposit_cents=None,
            request_id=None,
            comments="Tournage en cours, retour partiel déjà effectué",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(hours=2),
        ),
        Loan(
            borrower_id=9,
            assignee_id=2,
            start_date=now - timedelta(days=2),
            end_date=now + timedelta(days=4),
            total_deposit_cents=310000,
            actual_start_date=now - timedelta(days=2),
            actual_return_date=None,
            retained_deposit_cents=None,
            request_id=4,
            comments="Projet événementiel, matériel principal",
            created_at=now - timedelta(days=4),
            updated_at=now - timedelta(days=1),
        ),
        Loan(
            borrower_id=8,
            assignee_id=2,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=3),
            total_deposit_cents=80000,
            actual_start_date=None,
            actual_return_date=None,
            retained_deposit_cents=None,
            request_id=None,
            comments="Réservation confirmée, prêt pas encore démarré",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        ),
        Loan(
            borrower_id=6,
            assignee_id=3,
            start_date=now - timedelta(days=40),
            end_date=now - timedelta(days=35),
            total_deposit_cents=105000,
            actual_start_date=now - timedelta(days=40),
            actual_return_date=now - timedelta(days=38),
            retained_deposit_cents=0,
            request_id=None,
            comments="Retour anticipé sans dommage",
            created_at=now - timedelta(days=41),
            updated_at=now - timedelta(days=38),
        ),
        Loan(
            borrower_id=7,
            assignee_id=3,
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=1),
            total_deposit_cents=110000,
            actual_start_date=now - timedelta(days=5),
            actual_return_date=now - timedelta(days=1),
            retained_deposit_cents=0,
            request_id=None,
            comments="Prêt clôturé avant date de fin prévue",
            created_at=now - timedelta(days=6),
            updated_at=now - timedelta(days=1),
        ),
        Loan(
            borrower_id=8,
            assignee_id=2,
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=5),
            total_deposit_cents=250000,
            actual_start_date=None,
            actual_return_date=None,
            retained_deposit_cents=None,
            request_id=None,
            comments="Réservation en conflit",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        ),
    ]
    session.add_all(loans)
    session.flush()

    loaned_items = [
        LoanedItem(loan_id=1, item_id=6, actual_return_date=now - timedelta(days=12), return_condition=Condition.GOOD),
        LoanedItem(
            loan_id=1, item_id=15, actual_return_date=now - timedelta(days=12), return_condition=Condition.DEGRADED
        ),
        LoanedItem(loan_id=2, item_id=1, actual_return_date=None, return_condition=None),
        LoanedItem(loan_id=2, item_id=19, actual_return_date=now - timedelta(hours=2), return_condition=Condition.GOOD),
        LoanedItem(loan_id=3, item_id=4, actual_return_date=None, return_condition=None),
        LoanedItem(loan_id=3, item_id=17, actual_return_date=None, return_condition=None),
        LoanedItem(loan_id=4, item_id=12, actual_return_date=None, return_condition=None),
        LoanedItem(loan_id=4, item_id=20, actual_return_date=None, return_condition=None),
        LoanedItem(loan_id=5, item_id=10, actual_return_date=now - timedelta(days=39), return_condition=Condition.GOOD),
        LoanedItem(loan_id=5, item_id=16, actual_return_date=now - timedelta(days=38), return_condition=Condition.GOOD),
        LoanedItem(loan_id=6, item_id=7, actual_return_date=now - timedelta(days=2), return_condition=Condition.GOOD),
        LoanedItem(loan_id=6, item_id=18, actual_return_date=now - timedelta(days=1), return_condition=Condition.GOOD),
        LoanedItem(loan_id=7, item_id=4, actual_return_date=None, return_condition=None),
        LoanedItem(loan_id=7, item_id=13, actual_return_date=None, return_condition=None),
    ]
    session.add_all(loaned_items)
    session.commit()


def main() -> None:
    """Standalone CLI entrypoint to run the database seeder safely."""
    print("WARNING: This will wipe out all existing data in your environment database.")
    confirmation = input("Are you sure you want to proceed? (y/N): ").strip().lower()

    if confirmation != "y":
        print("Operation cancelled.")
        sys.exit(0)

    print("🔌 Connecting to target database...")
    try:
        with Session(engine) as session:
            seed_db(session)
        print("\nDatabase successfully seeded.")
    except Exception as e:
        print(f"\nDatabase seeding failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
