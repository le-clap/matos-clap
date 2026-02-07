# Site_emprunt_clap (nom à changer)

## Installation

---

### Serveur API

Le projet utilise un backend FastAPI pour gérer les requêtes des utilisateurs.
Pour installer toutes les dépendances et lancer le serveur :

- [Installer uv](https://docs.astral.sh/uv/getting-started/installation/) si ce n'est pas déjà fait
- Exécuter les commandes suivantes : 

```commandline
cd backend/
uv sync
uv run ./main.py
```

Puis aller à [cette adresse](http://localhost:8000/docs) pour voir la doc de l'API

### Application React

Le projet utilise un frontend écrit en React-Tailscript-TailwindCSS, basé sur le framework [Vite](https://vitejs.fr/).  
Le projet utilise également [shadcn](https://ui.shadcn.com/) pour la gestion des composants graphiques.

Pour installer les dépendances et lancer le serveur : 

- [Installer Node.js et npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) sur votre machine
- Exécuter les commandes commandes suivantes : 

```commandline
cd frontend/
npm install
npm run dev
```

Puis aller à [cette adresse](http://localhost:5173) pour aller voir la page d'accueil.

---

Une version plus détaillée de cette doc sera écrite (soon TM) pour mettre en selle les futurs clappeux :))
