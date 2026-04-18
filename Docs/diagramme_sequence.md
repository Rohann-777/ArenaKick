# Diagrammes de Séquence — ArenaKick

## Composants du système
- **Utilisateur** : acteur principal des scénarios
  (Administrateur, Organisateur, JoueurCompte, Spectateur)
- **Frontend** : interface web (HTML/CSS/JS)
- **API Flask** : backend Python
- **MySQL** : base de données (via WampServer + phpMyAdmin)

---

## Scénario 1 — Authentification (Login)

### Flux normal (succès)
1. L'utilisateur saisit son email et mot de passe
2. Le Frontend valide les champs localement
3. Le Frontend envoie POST /api/auth/login
   { email, motDePasse }
4. L'API Flask interroge MySQL :
   SELECT utilisateur WHERE email = ?
5. MySQL retourne les données de l'utilisateur
6. SQLAlchemy instancie automatiquement la bonne
   classe fille selon typeUtilisateur :
   - typeUtilisateur = 'admin' → Administrateur
   - typeUtilisateur = 'organisateur' → Organisateur
   - typeUtilisateur = 'joueur' → JoueurCompte
   - typeUtilisateur = 'spectateur' → Spectateur
7. L'API vérifie le mot de passe avec check_password_hash
8. L'API génère un token JWT avec l'idUtilisateur
9. L'API retourne 200 OK + token JWT + infos utilisateur
10. Le Frontend sauvegarde le token dans localStorage
11. Le Frontend redirige vers le tableau de bord

### Flux alternatif (échec)
- Si email inexistant → 401 Unauthorized
- Si mot de passe incorrect → 401 Unauthorized
- Le Frontend affiche un message d'erreur

---

## Scénario 2 — Création d'un tournoi

### Préconditions
- L'utilisateur est connecté en tant qu'Organisateur
  ou Administrateur
- Token JWT valide présent dans localStorage

### Flux normal (succès)
1. L'Organisateur clique sur "Créer un tournoi"
2. Le Frontend affiche le formulaire de création
3. L'Organisateur saisit :
   nom, dateDebut, dateFin, format, nombreEquipes
4. Le Frontend valide les données côté client :
   - Champs obligatoires remplis ?
   - dateFin > dateDebut ?
   - nombreEquipes valide (4, 8, 16 ou 32) ?
5. Le Frontend envoie POST /api/tournois
   Header : Authorization: Bearer <token>
   Body : { nom, dateDebut, dateFin, format, nombreEquipes }
6. L'API Flask vérifie le token JWT
7. SQLAlchemy instancie l'objet Organisateur
8. L'API vérifie le rôle (organisateur ou admin)
9. L'API valide les données côté serveur (double sécurité)
10. L'API vérifie que le nom du tournoi est unique
11. L'API insère le tournoi dans MySQL :
    INSERT INTO tournoi avec statut = 'inscription'
12. MySQL retourne l'idTournoi généré
13. L'API retourne 201 Created + données du tournoi
14. Le Frontend affiche le tableau de bord du tournoi
15. Message : "Tournoi créé ! Ajoutez vos équipes"

### Flux alternatif (erreur)
- Si token JWT invalide → 401 Unauthorized
- Si rôle insuffisant (joueur/spectateur) → 403 Forbidden
- Si nom déjà utilisé → 409 Conflict
- Si données invalides côté client → erreur formulaire
- Si données invalides côté serveur → 400 Bad Request

---

## Scénario 3 — Génération automatique des matchs (Round-Robin)

### Préconditions
- L'Organisateur est connecté
- Le tournoi est en statut 'inscription'
- Au moins 2 équipes sont inscrites au tournoi

### Flux normal (succès)
1. L'Organisateur clique sur "Générer les matchs"
2. Le Frontend affiche une confirmation :
   "Générer les matchs ? Cette action est irréversible !"
3. L'Organisateur confirme
4. Le Frontend envoie POST /api/matchs/generer/{idTournoi}
   Header : Authorization: Bearer <token>
5. L'API Flask vérifie le token JWT
6. L'API vérifie le statut du tournoi = 'inscription'
7. L'API récupère toutes les équipes :
   SELECT equipe WHERE idTournoi = ?
8. MySQL retourne la liste des équipes
9. L'API effectue un tirage aléatoire (random.shuffle)
   pour garantir la transparence du tournoi
10. L'API exécute l'algorithme Round-Robin :
    - Pour n équipes → n×(n-1)/2 matchs générés
    - Une équipe reste fixe, les autres tournent
    - Chaque équipe affronte toutes les autres une fois
11. L'API insère tous les matchs dans MySQL :
    INSERT INTO match (statut = 'programme')
12. L'API initialise le classement pour chaque équipe :
    INSERT INTO classement (points=0, victoires=0...)
13. L'API met à jour le statut du tournoi :
    UPDATE tournoi SET statut = 'en_cours'
14. MySQL confirme l'enregistrement
15. L'API retourne 201 Created + liste complète des matchs
16. Le Frontend affiche le calendrier des rencontres
17. L'Organisateur voit : Équipe A vs Équipe B, dates...

### Règles métier importantes
- Une fois les matchs générés, le statut passe à 'en_cours'
- Toute modification des groupes est IMPOSSIBLE
- Seul l'Administrateur peut forcer une remise à zéro
- Le tirage aléatoire garantit l'équité sportive

### Flux alternatif (erreur)
- Si token JWT invalide → 401 Unauthorized
- Si rôle insuffisant → 403 Forbidden
- Si tournoi déjà en cours → 400 Bad Request
- Si moins de 2 équipes → 400 Bad Request

---

## Notes techniques générales
- Chaque requête vers l'API (sauf login et routes
  publiques) doit contenir le token JWT dans le header :
  Authorization: Bearer <token>
- La validation des données est effectuée deux fois :
  côté Frontend (expérience utilisateur) ET
  côté Backend (sécurité obligatoire)
- SQLAlchemy instancie automatiquement la bonne classe
  fille grâce au polymorphisme (Single Table Inheritance)
- MySQL remplace SQLite — meilleure gestion des données
  et interface phpMyAdmin pour la visualisation
- Le token JWT expire après 86400 secondes (24 heures)
- Les mots de passe sont chiffrés avec werkzeug
  (generate_password_hash / check_password_hash)