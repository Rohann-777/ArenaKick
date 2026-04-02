from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notification'

    # Attributs / Colonnes
    idNotification = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contenu        = db.Column(db.String(255), nullable=False)
    type           = db.Column(
        db.Enum('rappel_match', 'resultat', 'info'),
        nullable=False,
        default='info'
    )
    dateEnvoi      = db.Column(db.DateTime, default=datetime.utcnow)
    lu             = db.Column(db.Boolean, default=False)

    # Clés étrangères
    idUtilisateur = db.Column(
        db.Integer,
        db.ForeignKey('utilisateur.idUtilisateur'),
        nullable=False
    )
    idMatch = db.Column(
        db.Integer,
        db.ForeignKey('match.idMatch'),
        nullable=True
    )

    def __repr__(self):
        return f'<Notification {self.type} - lu={self.lu}>'