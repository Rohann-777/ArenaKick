from app import db

class Equipe(db.Model):
    __tablename__ = 'equipe'

    # Attributs / Colonnes
    idEquipe  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom       = db.Column(db.String(100), nullable=False)
    couleur   = db.Column(db.String(50), nullable=True)
    logo      = db.Column(db.String(255), nullable=True)
    nomCoach = db.Column(db.String(150), nullable=True)

    # Clé étrangère
    idTournoi = db.Column(
        db.Integer,
        db.ForeignKey('tournoi.idTournoi'),
        nullable=False
    )

    # Relations
    joueurs     = db.relationship('Joueur', backref='equipe', lazy=True)
    classement  = db.relationship('Classement', backref='equipe', lazy=True)
    matchsA     = db.relationship(
        'Match',
        foreign_keys='Match.idEquipeA',
        backref='equipeA',
        lazy=True
    )
    matchsB     = db.relationship(
        'Match',
        foreign_keys='Match.idEquipeB',
        backref='equipeB',
        lazy=True
    )

    def __repr__(self):
        return f'<Equipe {self.nom}>'