# Matos CLAP — Frontend

Interface web de la plateforme de prêt de matériel du **CLAP**.
Application monopage (SPA) couvrant à la fois l'espace
utilisateur (catalogue, demandes, prêts) et le **backoffice** de gestion
(demandes, prêts, inventaire, utilisateurs).

## Stack

- **React 19** + **Vite 7** + **TypeScript**
- **TailwindCSS 4** — thème sombre « rouge / gris charbon » défini dans `src/index.css`
- **TanStack Query** — état serveur et cache
- **React Router 7** — routage
- **SDK généré** via [`@hey-api/openapi-ts`](https://heyapi.dev) depuis `../backend/openapi.json`
- **lucide-react** (icônes) · **date-fns** (dates)

Aucune librairie d'UI lourde : les composants (`src/components/ui`) sont écrits
sur mesure pour un rendu cohérent et léger.

## Démarrage

```bash
npm install
npm run generate   # régénère openapi.json (backend) + le client typé src/client
npm run dev        # http://localhost:5173 (proxy /api -> http://localhost:8000)
```

Le backend doit tourner sur le port `8000`. En dev, l'authentification CLA peut
être court-circuitée en lançant le backend avec `ENABLE_DEV_LOGIN=true` et en
définissant `VITE_ENABLE_DEV_LOGIN=true` côté frontend.

## Scripts

| Script                    | Rôle                                                    |
| ------------------------- | ------------------------------------------------------- |
| `npm run dev`             | Serveur de développement Vite                           |
| `npm run build`           | Vérification TypeScript + build de production (`dist/`) |
| `npm run lint`            | ESLint                                                  |
| `npm run generate:client` | Régénère le SDK depuis `../backend/openapi.json`        |
| `npm run generate`        | Régénère `openapi.json` puis le SDK                     |

## Architecture

```
src/
  auth/            Contexte d'authentification (session via cookie httpOnly)
  client/          SDK généré (ne pas éditer à la main)
  components/      Chrome partagé + design system (components/ui)
  features/        Logique métier (panier de demande, cartes catalogue)
  hooks/           Hooks TanStack Query par ressource
  layouts/         Coque utilisateur (AppLayout) et backoffice (AdminLayout)
  lib/             Client API, helpers de format, rôles, query keys
  pages/           Pages utilisateur + pages backoffice (pages/admin)
```

### Rôles

`user < clap < manager < admin`. Les routes `/admin/*` exigent
`clap`, la gestion de l'inventaire exige `manager`, et la modification des rôles
utilisateurs exige `admin`.
