from app import db
from datetime import datetime

class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'

    # Attributs / Colonnes
    idUtilisateur   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom             = db.Column(db.String(100), nullable=False)
    prenom          = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(150), unique=True, nullable=False)
    motDePasse      = db.Column(db.String(255), nullable=False)
    typeUtilisateur = db.Column(
        db.String(50),
        nullable=False,
        default='spectateur'
    )
    dateInscription = db.Column(db.DateTime, default=datetime.utcnow)

    # Colonne discriminante pour le polymorphisme
    __mapper_args__ = {
        'polymorphic_on': typeUtilisateur,
        'polymorphic_identity': 'utilisateur'
    }

    # Relations
    tournois      = db.relationship('Tournoi', backref='organisateur', lazy=True)
    notifications = db.relationship('Notification', backref='utilisateur', lazy=True)

    def __repr__(self):
        return f'<Utilisateur {self.prenom} {self.nom} ({self.typeUtilisateur})>'


# ============================================================
# Classe fille — Administrateur
# ============================================================
class Administrateur(Utilisateur):
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

    def gerer_utilisateurs(self):
        return Utilisateur.query.all()

    def attribuer_role(self, utilisateur, nouveau_role):
        utilisateur.typeUtilisateur = nouveau_role
        db.session.commit()

    def supprimer_tournoi(self, tournoi):
        db.session.delete(tournoi)
        db.session.commit()


# ============================================================
# Classe fille — Organisateur
# ============================================================
class Organisateur(Utilisateur):
    __mapper_args__ = {
        'polymorphic_identity': 'organisateur'
    }

    def creer_tournoi(self, nom, dateDebut, dateFin, format, nombreEquipes):
        from app.models.tournoi import Tournoi
        nouveau_tournoi = Tournoi(
            nom=nom,
            dateDebut=dateDebut,
            dateFin=dateFin,
            format=format,
            nombreEquipes=nombreEquipes,
            statut='inscription',
            idOrganisateur=self.idUtilisateur
        )
        db.session.add(nouveau_tournoi)
        db.session.commit()
        return nouveau_tournoi

    def saisir_resultat(self, match, scoreA, scoreB):
        match.scoreEquipeA = scoreA
        match.scoreEquipeB = scoreB
        match.statut = 'termine'
        db.session.commit()


# ============================================================
# Classe fille — JoueurCompte
# ============================================================
class JoueurCompte(Utilisateur):
    __mapper_args__ = {
        'polymorphic_identity': 'joueur'
    }

    def get_statistiques(self):
        from app.models.joueur import Joueur
        return Joueur.query.filter_by(
            nom=self.nom,
            prenom=self.prenom
        ).first()

    def voir_calendrier(self, idTournoi):
        from app.models.match import Match
        return Match.query.filter_by(idTournoi=idTournoi).all()


# ============================================================
# Classe fille — Spectateur
# ============================================================
class Spectateur(Utilisateur):
    __mapper_args__ = {
        'polymorphic_identity': 'spectateur'
    }

    def voir_classement(self, idTournoi):
        from app.models.classement import Classement
        return Classement.query.filter_by(
            idTournoi=idTournoi
        ).order_by(Classement.points.desc()).all()