# Diagramme de Classes — ArenaKick

## Classes et responsabilités

### Utilisateur
**Attributs** : idUtilisateur, nom, prenom, email,
motDePasse, typeUtilisateur, dateInscription
**Méthodes** : seConnecter(), seDeconnecter(),
getProfile(), updateProfile()

### Tournoi
**Attributs** : idTournoi, nom, dateDebut, dateFin,
format, nombreEquipes, statut
**Méthodes** : creer(), configurerFormat(),
genererMatchs(), cloturerTournoi(),
getEquipes(), getMatchs()

### Equipe
**Attributs** : idEquipe, nom, couleur, logo
**Méthodes** : inscrire(), getJoueurs(),
getClassement(), updateInfos()

### Joueur
**Attributs** : idJoueur, nom, prenom,
numeroMaillot, poste
**Méthodes** : getStatistiques(), updateProfil()

### Match
**Attributs** : idMatch, dateMatch, terrain,
scoreEquipeA, scoreEquipeB, statut
**Méthodes** : creerMatch(), saisirResultat(),
updateStatut(), getEquipes(), getProgramme()

### Classement
**Attributs** : idClassement, points, victoires,
defaites, nuls, butsPour, butsContre, rang, statut
**Méthodes** : calculerPoints(), updateClassement(),
trierEquipes(), getStatutEquipe()

### Notification
**Attributs** : idNotification, contenu, type,
dateEnvoi, lu
**Méthodes** : envoyer(), marquerLu(),
getNotifications()

## Relations
- Utilisateur "1" --> "0..*" Tournoi : organise
- Tournoi "1" --> "2..*" Equipe : contient
- Equipe "1" --> "1..*" Joueur : possede
- Tournoi "1" --> "1..*" Match : programme
- Match "2" --> "1" Equipe : implique
- Equipe "1" --> "1" Classement : aClassement
- Utilisateur "1" --> "0..*" Notification : recoit
- Match "1" --> "0..*" Notification : declencheNotif

## Notes
- Les méthodes seront traduites en fonctions Python dans Flask
- genererMatchs() implémente l'algorithme Round-Robin
- calculerPoints() implémente le tri multi-critères FIFA