# Diagramme de Classes — ArenaKick

## Classe parent et classes filles (Héritage)

### Utilisateur (classe mère)
**Attributs** : idUtilisateur, nom, prenom, email,
motDePasse, typeUtilisateur, dateInscription
**Méthodes** : seConnecter(), seDeconnecter(),
getProfile(), updateProfile()

### Administrateur (hérite de Utilisateur)
**Méthodes spécifiques** : gererUtilisateurs(),
attribuerRoles(), supprimerTournoi()

### Organisateur (hérite de Utilisateur)
**Méthodes spécifiques** : creerTournoi(),
gererEquipes(), saisirResultat(), genererMatchs()

### Joueur (hérite de Utilisateur)
**Méthodes spécifiques** : getStatistiques(),
voirCalendrier(), voirMonEquipe()

### Spectateur (hérite de Utilisateur)
**Méthodes spécifiques** : ajouterFavori(),
voirClassement(), consulterSansCompte()

---

## Autres classes

### Tournoi
**Attributs** : idTournoi, nom, dateDebut, dateFin,
format, nombreEquipes, statut, idOrganisateur FK
**Méthodes** : creer(), configurerFormat(),
genererMatchs(), cloturerTournoi(),
getEquipes(), getMatchs()

### Equipe
**Attributs** : idEquipe, nom, couleur, logo,
nomCoach, idTournoi FK
**Méthodes** : inscrire(), getJoueurs(),
getClassement(), updateInfos()

### Joueur (entité BDD — différent de la classe Joueur)
**Attributs** : idJoueur, nom, prenom, age,
numeroMaillot, poste, idEquipe FK
**Méthodes** : getStatistiques(), updateProfil()

### Match
**Attributs** : idMatch, dateMatch, heureMatch,
terrain, scoreEquipeA, scoreEquipeB, statut,
idEquipeA FK, idEquipeB FK, idTournoi FK
**Méthodes** : creerMatch(), saisirResultat(),
updateStatut(), getEquipes(), getProgramme()

### Classement
**Attributs** : idClassement, points, victoires,
defaites, nuls, butsPour, butsContre,
differenceButs, rang, statut,
idEquipe FK, idTournoi FK
**Méthodes** : calculerPoints(), updateClassement(),
trierEquipes(), getStatutEquipe()

### Notification
**Attributs** : idNotification, contenu, type,
dateEnvoi, lu, idUtilisateur FK, idMatch FK
**Méthodes** : envoyer(), marquerLu(),
getNotifications()

---

## Relations

### Héritage
- Administrateur --|> Utilisateur
- Organisateur --|> Utilisateur
- Joueur --|> Utilisateur
- Spectateur --|> Utilisateur

### Associations
- Utilisateur "1" --> "0..*" Tournoi : organise
- Tournoi "1" --> "2..*" Equipe : contient
- Equipe "1" --> "1..*" Joueur : possede
- Tournoi "1" --> "1..*" Match : programme
- Equipe "1" --> "0..*" Match : joueA / joueB
- Equipe "1" --> "1" Classement : aClassement
- Tournoi "1" --> "0..*" Classement : aClassement
- Utilisateur "1" --> "0..*" Notification : recoit
- Match "1" --> "0..*" Notification : declencheNotif

---

## Notes
- Les classes filles héritent de tous les attributs
  et méthodes de Utilisateur
- typeUtilisateur permet à SQLAlchemy d'identifier
  la classe fille (polymorphisme)
- La BDD utilise une seule table utilisateur
  (Single Table Inheritance)
- genererMatchs() implémente l'algorithme Round-Robin
- calculerPoints() implémente le tri multi-critères FIFA