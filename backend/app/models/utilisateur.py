from app import db
from datetime import datetime

class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'

    # Attributs / Colonnes
    idUtilisateur = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom           = db.Column(db.String(100), nullable=False)
    prenom        = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    motDePasse    = db.Column(db.String(255), nullable=False)
    typeUtilisateur = db.Column(
        db.Enum('admin', 'organisateur', 'joueur', 'spectateur'),
        nullable=False,
        default='spectateur'
    )
    dateInscription = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    tournois      = db.relationship('Tournoi', backref='organisateur', lazy=True)
    notifications = db.relationship('Notification', backref='utilisateur', lazy=True)

    def __repr__(self):
        return f'<Utilisateur {self.prenom} {self.nom} ({self.typeUtilisateur})>'