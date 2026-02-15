# Fichier seed généré avec Gemini pour des tests
# Merci Gemini :))

from sqlmodel import Session, select
from db.database import engine
from models.models import *
from datetime import datetime


def seed_data():
    with Session(engine) as session:
        # 1. Vérifier si la base est déjà remplie pour éviter les doublons
        # On regarde s'il y a déjà des catégories
        existing_category = session.exec(select(Category)).first()
        if existing_category:
            print("Database already seeded. Skipping...")
            return

        print("Seeding database...")

        # --- ÉTAPE 1 : Les tables de référence (Reference Tables) ---

        # Conditions (État du matériel)
        cond_new = Condition(name="Neuf", description="Matériel jamais utilisé ou parfait état")
        cond_good = Condition(name="Bon état", description="Traces d'usure normale, fonctionnel")
        cond_bad = Condition(name="Dégradé", description="Fonctionnel mais abîmé")

        # Disponibilités
        avail_ok = Availability(name="Disponible", description="Prêt à l'emprunt")
        avail_loaned = Availability(name="Emprunté", description="Actuellement sorti")
        avail_maint = Availability(name="Maintenance", description="En réparation")

        # Catégories
        cat_camera = Category(name="Caméra", description="Boîtiers et caméras")
        cat_light = Category(name="Lumière", description="Panneaux LED, Mandarines...")
        cat_sound = Category(name="Son", description="Micros, perches, enregistreurs")
        cat_mach = Category(name="Machinerie", description="Trépieds, stabilisateurs")

        # On ajoute tout ça à la session
        session.add(cond_new)
        session.add(cond_good)
        session.add(cond_bad)
        session.add(avail_ok)
        session.add(avail_loaned)
        session.add(avail_maint)
        session.add(cat_camera)
        session.add(cat_light)
        session.add(cat_sound)
        session.add(cat_mach)

        # On commit pour générer les IDs (nécessaire pour la suite)
        session.commit()

        # --- ÉTAPE 2 : Le Catalogue (Les fiches produits génériques) ---

        cat_sony = Catalog(
            name="Sony A7S III",
            description="Boîtier hybride plein format orienté vidéo 4K.",
            category_id=cat_camera.id,
            image_path="https://images.unsplash.com/photo-1516035069371-29a1b244cc32?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
            # Image test
        )

        cat_zoom = Catalog(
            name="Zoom H6",
            description="Enregistreur portable 6 pistes.",
            category_id=cat_sound.id,
            image_path="https://producelikeapro.com/blog/wp-content/uploads/2021/06/Zoom-H6-Review-6-Channel-Handy-Recorder.jpg"
        )

        cat_tripod = Catalog(
            name="Manfrotto 504HD",
            description="Trépied vidéo fluide pro.",
            category_id=cat_mach.id,
            image_path="https://www.f44location.com/wp-content/uploads/2020/03/40607_Manffroto_1.jpg"
        )

        session.add(cat_sony)
        session.add(cat_zoom)
        session.add(cat_tripod)
        session.commit()

        # --- ÉTAPE 3 : Les Items physiques (Le vrai matériel) ---

        # 2 Caméras Sony
        item_cam_01 = Item(
            name="CAM-01",
            catalog_id=cat_sony.id,
            deposit=2000.00,
            condition_id=cond_new.id,
            availability_id=avail_ok.id,
            last_availability_update=datetime.now()
        )

        item_cam_02 = Item(
            name="CAM-02",
            catalog_id=cat_sony.id,
            deposit=2000.00,
            condition_id=cond_good.id,  # Celle-ci est un peu usée
            availability_id=avail_loaned.id,  # Et elle est déjà sortie !
            last_availability_update=datetime.now()
        )

        # 1 Enregistreur
        item_snd_01 = Item(
            name="SND-01",
            catalog_id=cat_zoom.id,
            deposit=300.00,
            condition_id=cond_new.id,
            availability_id=avail_ok.id,
            last_availability_update=datetime.now()
        )

        session.add(item_cam_01)
        session.add(item_cam_02)
        session.add(item_snd_01)

        # --- ÉTAPE 4 : Un Utilisateur de test ---

        test_user = User(
            username="JBclap",
            name="Jean Baptiste",
            email="jean.baptiste@le-clap.fr",
        )

        session.add(test_user)

        # Validation finale
        session.commit()
        print("Seeding complete!")