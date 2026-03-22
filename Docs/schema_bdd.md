# Schéma de la Base de Données — ArenaKick

## Entités et attributs

### UTILISATEUR
- idUtilisateur (PK)
- nomUtilisateur
- prenomUtilisateur
- emailUtilisateur
- motDePasse
- typeUtilisateur (admin, organisateur, joueur, spectateur)
- dateInscription

### TOURNOI
- idTournoi (PK)
- nomTournoi
- dateDebut
- dateFin
- formatTournoi (poules, elimination, mixte)
- nombreEquipes
- statut (inscription, en_cours, termine)
- idOrganisateur (FK → UTILISATEUR)

### EQUIPE
- idEquipe (PK)
- nomEquipe
- couleurEquipe
- logoEquipe
- idTournoi (FK → TOURNOI)

### JOUEUR
- idJoueur (PK)
- nomJoueur
- prenomJoueur
- numeroMaillot
- posteJoueur (gardien, defenseur, milieu, attaquant)
- idEquipe (FK → EQUIPE)

### MATCH
- idMatch (PK)
- dateMatch
- heureMatch
- terrainMatch
- scoreEquipeA
- scoreEquipeB
- statutMatch (programme, en_cours, termine)
- idEquipeA (FK → EQUIPE)
- idEquipeB (FK → EQUIPE)
- idTournoi (FK → TOURNOI)

### CLASSEMENT
- idClassement (PK)
- points
- victoires
- defaites
- nuls
- butsPour
- butsContre
- differenceButs
- rangEquipe
- statutEquipe (qualifie, barrage, elimine)
- idEquipe (FK → EQUIPE)
- idTournoi (FK → TOURNOI)

### NOTIFICATION
- idNotification (PK)
- contenuNotification
- typeNotification (rappel_match, resultat, info)
- dateNotification
- luNotification (boolean)
- idUtilisateur (FK → UTILISATEUR)
- idMatch (FK → MATCH)

## Relations
- UTILISATEUR ||--o{ TOURNOI : organise
- TOURNOI ||--o{ EQUIPE : contient
- EQUIPE ||--o{ JOUEUR : possede
- TOURNOI ||--o{ MATCH : programme
- EQUIPE ||--o{ MATCH : joueA / joueB
- EQUIPE ||--|| CLASSEMENT : aClassement (par tournoi)
- TOURNOI ||--o{ CLASSEMENT : aClassement
- UTILISATEUR ||--o{ NOTIFICATION : recoit
- MATCH ||--o{ NOTIFICATION : declencheNotif