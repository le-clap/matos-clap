# Matos CLAP

Site d'emprunt de matériel du CLAP.

## Installation locale

### Serveur API

Le projet utilise un backend FastAPI pour gérer les requêtes des utilisateurs.
Pour installer les dépendances et lancer le serveur :

- [Installer uv](https://docs.astral.sh/uv/getting-started/installation/) si ce n'est pas déjà fait
- Avoir une instance PostgreSQL accessible et créer un fichier `backend/.env` avec les variables suivantes :

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=database
DB_USER=username
DB_PASSWORD=password
```

- Exécuter les commandes suivantes :

```commandline
cd backend/
uv sync
uv run alembic upgrade head
uv run ./main.py
```

Puis aller à [cette adresse](http://localhost:8000/docs) pour voir la doc de l'API

### Application React

Le projet utilise un frontend écrit en React-Typescript-TailwindCSS, basé sur le framework [Vite](https://vitejs.fr/).
Le projet utilise également [shadcn](https://ui.shadcn.com/) pour la gestion des composants graphiques.

Pour installer les dépendances et lancer le serveur :

- [Installer Node.js et npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) sur votre machine
- Exécuter les commandes suivantes :

```commandline
cd frontend/
npm install
npm run dev
```

Puis aller à [cette adresse](http://localhost:5173) pour aller voir la page d'accueil.

### Migrations de base de données (Alembic)

Le projet utilise [Alembic](https://alembic.sqlalchemy.org/) pour gérer les migrations de schéma de la base de données PostgreSQL.

Depuis `backend/` :

```commandline
# Appliquer toutes les migrations en attente
uv run alembic upgrade head

# Créer une nouvelle migration (autogénérée depuis les modèles)
uv run alembic revision --autogenerate -m "description"

# Revenir à une révision précédente
uv run alembic downgrade -1
```

---

## Qualité de code

### Backend (ruff + ty + pre-commit)

Depuis `backend/` :

```commandline
uv sync
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

#### Pre-commit

Pour installer les hooks pre-commit :

```commandline
cd backend/
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
```

Les hooks s'exécutent automatiquement avant chaque commit.

---

## Exécution avec Docker

Une stack Docker est disponible pour lancer backend + frontend :

```commandline
docker compose up --build
```

- Frontend : [http://localhost:3000](http://localhost:3000)
- Backend/API docs : [http://localhost:8000/docs](http://localhost:8000/docs)

Le frontend (Nginx) reverse-proxy les routes `/api/` vers le service backend.

---

## CI

Un workflow GitHub Actions (`.github/workflows/lint.yml`) vérifie sur push/PR vers `main`.
