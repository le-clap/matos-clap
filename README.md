# Matos CLAP

Application de prêt de matériel du CLAP (Centrale Lille Audiovisuel Production).
Les membres parcourent le catalogue et déposent une demande ; le CLAP la traite
depuis un backoffice — création de prêts, retours, inventaire, planning et
gestion des utilisateurs.

Le backend est une API FastAPI (Python, gérée avec `uv`) adossée à PostgreSQL. Le
frontend est une SPA React / Vite / TypeScript qui consomme un client TypeScript
généré automatiquement depuis le schéma OpenAPI du backend.

## Lancer en local

Le backend a besoin de [`uv`](https://docs.astral.sh/uv/) et d'une base
PostgreSQL. Renseignez `backend/.env` :

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=matos
DB_USER=postgres
DB_PASSWORD=postgres
```

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run ./main.py            # API sur http://localhost:8000 — doc interactive : /docs
```

Le frontend a besoin de Node.js :

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173 — /api et /media sont proxifiés vers :8000
```

L'authentification passe par le SSO de Centrale Lille Assos. En développement on
peut la court-circuiter : lancez le backend avec `ENABLE_DEV_LOGIN=true` et créez
`frontend/.env.local` contenant `VITE_ENABLE_DEV_LOGIN=true`. Le bouton de
connexion ouvre alors une session admin sur le premier utilisateur en base.

## Docker

```bash
docker compose up --build
```

Frontend sur `http://localhost:3000`, API sur `http://localhost:8000`. Nginx sert
le frontend et relaie `/api/` et `/media/` vers le backend.

## Base de données

Le schéma est versionné avec Alembic. Depuis `backend/` :

```bash
uv run alembic upgrade head                            # appliquer les migrations
uv run alembic revision --autogenerate -m "message"    # en générer une nouvelle
uv run alembic downgrade -1                            # revenir en arrière
```

## Vérifications

- Backend, depuis `backend/` : `uv run ruff check .`, `uv run ty check`, `uv run pytest`.
- Frontend, depuis `frontend/` : `npm run lint`, `npm run build`.

`uv run pre-commit install` (dans `backend/`) branche les hooks ruff + ty, et la
CI GitHub Actions rejoue le lint sur les PR vers `main`.

## Organisation

- `backend/` — API FastAPI, modèles SQLModel, migrations Alembic, tests pytest.
- `frontend/` — la SPA React ; voir [`frontend/README.md`](../../../Downloads/matos-clap/matos-clap/frontend/README.md) pour les détails (stack, scripts, arborescence, rôles).
