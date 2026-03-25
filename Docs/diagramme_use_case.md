# Diagramme Use Case — ArenaKick

## Acteurs
- **Administrateur** : accès complet au système
- **Organisateur** : gestion des tournois
- **Joueur** : consultation et suivi personnel
- **Spectateur** : consultation publique

## Cas d'utilisation par acteur

### Administrateur
- Gérer les utilisateurs (créer, modifier, supprimer)
- Attribuer les rôles (organisateur, joueur, spectateur)
- Gérer les données système
- Ajouter / supprimer un match

### Organisateur
- Créer et configurer un tournoi
- Gérer les équipes et joueurs
- Générer les matchs automatiquement
- Saisir et valider les résultats

### Joueur (+ actions communes)
- Consulter le calendrier des matchs
- Consulter les statistiques (les siennes + celles des autres)
- Consulter le classement
- Recevoir les notifications

### Spectateur
- Consulter le calendrier (partagé)
- Consulter les statistiques (partagé)
- Suivre les résultats des matchs
- Ajouter un joueur en favori
- Consulter sans compte (accès public)

### Commun (tous les acteurs connectés)
- S'authentifier via JWT

## Notes
- Les spectateurs peuvent consulter certaines infos sans compte
- Le bouton "Ajouter en favori" est une fonctionnalité Could Have
- L'authentification JWT est obligatoire pour toute action d'écriture