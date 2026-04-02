from app import db

class Joueur(db.Model):
    __tablename__ = 'joueur'

    # Attributs / Colonnes
    idJoueur      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom           = db.Column(db.String(100), nullable=False)
    prenom        = db.Column(db.String(100), nullable=False)
    numeroMaillot = db.Column(db.Integer, nullable=True)
    poste         = db.Column(
        db.Enum('gardien', 'defenseur', 'milieu', 'attaquant'),
        nullable=True
    )

    # Clé étrangère
    idEquipe = db.Column(
        db.Integer,
        db.ForeignKey('equipe.idEquipe'),
        nullable=False
    )

    def __repr__(self):
        return f'<Joueur {self.prenom} {self.nom} ({self.poste})>'