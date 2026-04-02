from app import create_app, db
from app.models.utilisateur import Utilisateur
from app.models.tournoi import Tournoi
from app.models.equipe import Equipe
from app.models.joueur import Joueur
from app.models.match import Match
from app.models.classement import Classement
from app.models.notification import Notification

# Créer l'application Flask
app = create_app('development')

if __name__ == '__main__':
    with app.app_context():
        # Créer toutes les tables dans MySQL
        db.create_all()
        print("Tables créées avec succès !")

    # Lancer le serveur Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )