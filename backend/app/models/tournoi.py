from app import db
from datetime import datetime

class Tournoi(db.Model):
    __tablename__ = 'tournoi'

    # Attributs / Colonnes
    idTournoi     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom           = db.Column(db.String(150), nullable=False, unique=True)
    dateDebut     = db.Column(db.Date, nullable=False)
    dateFin       = db.Column(db.Date, nullable=False)
    format        = db.Column(
        db.Enum('poules', 'elimination', 'mixte'),
        nullable=False,
        default='poules'
    )
    nombreEquipes = db.Column(db.Integer, nullable=False)
    statut        = db.Column(
        db.Enum('inscription', 'en_cours', 'termine'),
        nullable=False,
        default='inscription'
    )

    # Clé étrangère
    idOrganisateur = db.Column(
        db.Integer,
        db.ForeignKey('utilisateur.idUtilisateur'),
        nullable=False
    )

    # Relations
    equipes       = db.relationship('Equipe', backref='tournoi', lazy=True)
    matchs        = db.relationship('Match', backref='tournoi', lazy=True)
    classements   = db.relationship('Classement', backref='tournoi', lazy=True)

    def __repr__(self):
        return f'<Tournoi {self.nom} ({self.statut})>'