# Diagrammes de Séquence — ArenaKick

## Composants du système
- **Organisateur** : acteur principal des scénarios
- **Frontend** : interface web (HTML/CSS/JS)
- **API Flask** : backend Python
- **MySQL** : base de données (via phpMyAdmin)

---

## Scénario 1 — Authentification (Login)

### Flux normal (succès)
1. L'organisateur saisit son email et mot de passe
2. Le Frontend envoie POST /api/login { email, motDePasse }
3. L'API Flask interroge MySQL : SELECT utilisateur WHERE email = ?
4. MySQL retourne les données de l'utilisateur
5. L'API vérifie le mot de passe et le rôle (organisateur)
6. L'API génère un token JWT
7. L'API retourne 200 OK + token JWT
8. Le Frontend sauvegarde le token JWT localement
9. Le Frontend redirige vers le tableau de bord organisateur

### Flux alternatif (échec)
- Si email inexistant ou mot de passe incorrect → 401 Unauthorized
- Le Frontend affiche un message d'erreur

---

## Scénario 2 — Création d'un tournoi

### Flux normal (succès)
1. L'organisateur clique sur "Créer un tournoi"
2. Le Frontend affiche le formulaire
3. L'organisateur saisit : nom, dateDebut, dateFin, format, nombreEquipes
4. Le Frontend valide les données côté client
5. Le Frontend envoie POST /api/tournois + token JWT
6. L'API Flask vérifie le token JWT
7. L'API insère le tournoi dans MySQL : INSERT INTO tournoi
8. MySQL retourne l'idTournoi généré
9. L'API retourne 201 Created + données du tournoi
10. Le Frontend affiche le tableau de bord du tournoi
11. Message affiché : "Tournoi créé ! Ajoutez vos équipes"

### Flux alternatif (erreur validation)
- Si données invalides côté client → erreur affichée sur le formulaire
- Si token JWT invalide → 401 Unauthorized

---

## Scénario 3 — Génération automatique des matchs (Round-Robin)

### Flux normal (succès)
1. L'organisateur clique sur "Générer les matchs"
2. Le Frontend envoie POST /api/tournois/{id}/generer-matchs + token JWT
3. L'API Flask vérifie le token JWT et le statut du tournoi
4. L'API récupère toutes les équipes : SELECT équipes WHERE idTournoi = ?
5. MySQL retourne la liste des équipes
6. L'API effectue un tirage aléatoire des équipes (transparence)
7. L'API exécute l'algorithme Round-Robin → n×(n-1)/2 matchs générés
8. L'API insère tous les matchs : INSERT INTO match
9. L'API met à jour le statut du tournoi : UPDATE statut = "en_cours"
10. MySQL confirme l'enregistrement
11. L'API retourne 201 Created + liste complète des matchs
12. Le Frontend affiche le calendrier complet des rencontres
13. L'organisateur voit : Équipe A vs Équipe B, dates, terrains...

### Règle métier importante
- Une fois les matchs générés, le statut du tournoi passe à "en_cours"
- Toute modification des groupes est IMPOSSIBLE (prévention de tricherie)
- Seul l'Administrateur peut forcer une remise à zéro en cas exceptionnel

---

## Notes techniques
- Chaque requête vers l'API (sauf login) doit contenir le token JWT
- La validation des données est effectuée deux fois :
  côté Frontend (expérience utilisateur) ET côté Backend (sécurité)
- MySQL remplace SQLite — meilleure gestion des données et interface
  phpMyAdmin pour la visualisation