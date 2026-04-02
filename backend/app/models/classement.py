from app import db

class Classement(db.Model):
    __tablename__ = 'classement'

    # Attributs / Colonnes
    idClassement   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    points         = db.Column(db.Integer, nullable=False, default=0)
    victoires      = db.Column(db.Integer, nullable=False, default=0)
    defaites       = db.Column(db.Integer, nullable=False, default=0)
    nuls           = db.Column(db.Integer, nullable=False, default=0)
    butsPour       = db.Column(db.Integer, nullable=False, default=0)
    butsContre     = db.Column(db.Integer, nullable=False, default=0)
    differenceButs = db.Column(db.Integer, nullable=False, default=0)
    rang           = db.Column(db.Integer, nullable=True)
    statut         = db.Column(
        db.Enum('qualifie', 'barrage', 'elimine'),
        nullable=True
    )

    # Clés étrangères
    idEquipe  = db.Column(
        db.Integer,
        db.ForeignKey('equipe.idEquipe'),
        nullable=False
    )
    idTournoi = db.Column(
        db.Integer,
        db.ForeignKey('tournoi.idTournoi'),
        nullable=False
    )

    def __repr__(self):
        return f'<Classement Equipe {self.idEquipe} - {self.points} pts>'