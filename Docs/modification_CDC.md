# Modifications du CDC — ArenaKick

## Modification 1 — Base de données (date : 25 Mars 2026)
- **Avant** : SQLite
- **Après** : MySQL + phpMyAdmin
- **Raison** : Meilleure gestion des données, interface visuelle
  phpMyAdmin, plus adapté au contexte académique et professionnel
- **Impact** : Mise à jour de la section 11 (Technologies) du CDC

## Évolutions futures (Version 2)
- Événements de match (buts, passes, cartons) → table EvenementMatch
- Team of the week / XI of the week → table Selection
- Notifications push mobile via Firebase Cloud Messaging