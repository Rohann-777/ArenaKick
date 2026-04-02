from app import db
from datetime import datetime

class Match(db.Model):
    __tablename__ = 'match'

    # Attributs / Colonnes
    idMatch      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dateMatch    = db.Column(db.Date, nullable=False)
    heureMatch   = db.Column(db.Time, nullable=True)
    terrain      = db.Column(db.String(150), nullable=True)
    scoreEquipeA = db.Column(db.Integer, nullable=True, default=0)
    scoreEquipeB = db.Column(db.Integer, nullable=True, default=0)
    statut       = db.Column(
        db.Enum('programme', 'en_cours', 'termine'),
        nullable=False,
        default='programme'
    )

    # Clés étrangères
    idEquipeA = db.Column(
        db.Integer,
        db.ForeignKey('equipe.idEquipe'),
        nullable=False
    )
    idEquipeB = db.Column(
        db.Integer,
        db.ForeignKey('equipe.idEquipe'),
        nullable=False
    )
    idTournoi = db.Column(
        db.Integer,
        db.ForeignKey('tournoi.idTournoi'),
        nullable=False
    )

    # Relations
    notifications = db.relationship('Notification', backref='match', lazy=True)

    def __repr__(self):
        return f'<Match {self.idMatch} - {self.statut}>'