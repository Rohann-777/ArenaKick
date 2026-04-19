# ArenaKick
## Plateforme de gestion et organisation de tournois de football

Projet transversal L2 — Numérique Malagasy 2035
ESMIA INNOVATION — Année académique 2024-2025
Étudiant : RAKOTOJAONA Tsiaronomena Rohann

---

## Contexte
ArenaKick répond au besoin de numériser l'organisation
des tournois de football à Madagascar, dans le cadre
du thème "Imaginer le Numérique Malagasy de 2035".

---

## Structure du projet
ArenaKick/
├── docs/          # Documentation (CDC, UML, algo)
├── src/
│   ├── backend/   # API Flask + MySQL
│   └── frontend/  # Interface web HTML/CSS/JS
├── data/          # Jeu de données synthétique
└── README.md

---

## Lancement du projet

### Prérequis
- Python 3.12+
- WampServer (MySQL + phpMyAdmin)
- Navigateur web moderne

### Backend (API Flask)
```bash
cd src/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
L'API démarre sur : http://127.0.0.1:5000

### Frontend
```bash
cd src/frontend
python -m http.server 8080
```
L'interface est accessible sur : http://localhost:8080

### Génération des données
```bash
cd data
python generate_data.py
```

---

## Algorithmes implémentés
1. **Round-Robin** (Optimisation) — génération équitable
   des matchs de tournoi
2. **Tri multi-critères FIFA** (Optimisation) — classement
   par points, différence de buts, buts marqués

## Structures de données utilisées
1. **Liste** — stockage des équipes et matchs
2. **Dictionnaire / Hash Map** — statistiques O(1)
3. **File FIFO** — ordonnancement des matchs

---

## API — Routes principales
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | /api/auth/login | Connexion |
| POST | /api/auth/register | Inscription |
| GET | /api/tournois | Liste tournois |
| POST | /api/tournois | Créer tournoi |
| POST | /api/matchs/generer/{id} | Round-Robin |
| GET | /api/matchs/classement/{id} | Classement FIFA |

---

## Tests unitaires
```bash
cd src/backend
python -m pytest tests/ -v
```

---

## Démonstration
Parcours 1 — Organisateur :
1. S'inscrire sur /pages/register.html
2. Se connecter sur /pages/login.html
3. Créer un tournoi
4. Ajouter des équipes
5. Générer les matchs (Round-Robin)
6. Saisir les résultats
7. Consulter le classement FIFA

Parcours 2 — Spectateur :
1. Accéder à index.html sans connexion
2. Consulter les tournois publics
3. Voir le calendrier et le classement
