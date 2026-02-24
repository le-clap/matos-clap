from sqlmodel import Session, select

from db.database import engine
from models.enums import Availability, Condition
from models.models import Catalog, Category, Item, User


def seed_data():
    with Session(engine) as session:
        existing_category = session.exec(select(Category)).first()
        if existing_category:
            print("Database already seeded. Skipping...")
            return

        print("Seeding database...")

        # --- Categories ---

        cat_camera = Category(name="Caméra", description="Boîtiers et caméras")
        cat_light = Category(name="Lumière", description="Panneaux LED, Mandarines...")
        cat_sound = Category(name="Son", description="Micros, perches, enregistreurs")
        cat_mach = Category(name="Machinerie", description="Trépieds, stabilisateurs")

        session.add_all([cat_camera, cat_light, cat_sound, cat_mach])
        session.commit()

        assert cat_camera.id is not None
        assert cat_sound.id is not None
        assert cat_mach.id is not None

        # --- Catalogs ---

        cat_sony = Catalog(
            name="Sony A7S III",
            description="Boîtier hybride plein format orienté vidéo 4K.",
            category_id=cat_camera.id,
            image_path="https://images.unsplash.com/photo-1516035069371-29a1b244cc32",
        )
        cat_zoom = Catalog(
            name="Zoom H6",
            description="Enregistreur portable 6 pistes.",
            category_id=cat_sound.id,
            image_path="https://producelikeapro.com/blog/wp-content/uploads/2021/06/Zoom-H6-Review-6-Channel-Handy-Recorder.jpg",
        )
        cat_tripod = Catalog(
            name="Manfrotto 504HD",
            description="Trépied vidéo fluide pro.",
            category_id=cat_mach.id,
            image_path="https://www.f44location.com/wp-content/uploads/2020/03/40607_Manffroto_1.jpg",
        )

        session.add_all([cat_sony, cat_zoom, cat_tripod])
        session.commit()

        assert cat_sony.id is not None
        assert cat_zoom.id is not None
        assert cat_tripod.id is not None

        # --- Items ---

        session.add_all(
            [
                Item(
                    name="CAM-01",
                    catalog_id=cat_sony.id,
                    condition=Condition.NEW,
                    availability=Availability.AVAILABLE,
                    deposit_cents=2000_00,
                ),
                Item(
                    name="CAM-02",
                    catalog_id=cat_sony.id,
                    condition=Condition.GOOD,
                    availability=Availability.AVAILABLE,
                    deposit_cents=2000_00,
                ),
                Item(
                    name="SND-01",
                    catalog_id=cat_zoom.id,
                    condition=Condition.NEW,
                    availability=Availability.AVAILABLE,
                    deposit_cents=300_00,
                ),
            ]
        )

        # --- Test user ---

        session.add(
            User(
                username="JBclap",
                name="Jean Baptiste",
                email="jean.baptiste@le-clap.fr",
            )
        )

        session.commit()
        print("Seeding complete!")
