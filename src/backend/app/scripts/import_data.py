import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))))

from app import create_app, db
from app.models.utilisateur import Utilisateur
from app.models.tournoi import Tournoi
from app.models.equipe import Equipe
from app.models.joueur import Joueur
from app.models.match import Match
from app.models.classement import Classement
from werkzeug.security import generate_password_hash
from datetime import datetime

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..', '..', 'data'
)

def charger_json(fichier):
    chemin = os.path.join(DATA_DIR, fichier)
    with open(chemin, 'r', encoding='utf-8') as f:
        return json.load(f)

def importer_donnees():
    app = create_app('development')

    with app.app_context():
        print("Suppression des anciennes donnees...")
        from app.models.notification import Notification
        from sqlalchemy import text

        # TRUNCATE remet les auto_increment à 1
        # Désactiver les contraintes FK temporairement
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
        db.session.execute(text('TRUNCATE TABLE notification'))
        db.session.execute(text('TRUNCATE TABLE classement'))
        db.session.execute(text('TRUNCATE TABLE `match`'))
        db.session.execute(text('TRUNCATE TABLE joueur'))
        db.session.execute(text('TRUNCATE TABLE equipe'))
        db.session.execute(text('TRUNCATE TABLE tournoi'))
        db.session.execute(text('TRUNCATE TABLE utilisateur'))
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        db.session.commit()
        print("  Tables vidées et auto_increment remis à 1")

        # ============================================================
        # 1. Créer les utilisateurs par défaut
        # ============================================================
        print("Creation des utilisateurs...")

        admin = Utilisateur(
            nom="RAKOTOJAONA",
            prenom="Rohann",
            email="admin@arenakick.mg",
            motDePasse=generate_password_hash("admin2035"),
            typeUtilisateur="admin"
        )

        organisateur = Utilisateur(
            nom="Rabe",
            prenom="Jean",
            email="organisateur@arenakick.mg",
            motDePasse=generate_password_hash("orga2035"),
            typeUtilisateur="organisateur"
        )

        spectateur = Utilisateur(
            nom="Rakoto",
            prenom="Marie",
            email="spectateur@arenakick.mg",
            motDePasse=generate_password_hash("spec2035"),
            typeUtilisateur="spectateur"
        )

        db.session.add_all([admin, organisateur, spectateur])
        db.session.commit()
        print(f"  3 utilisateurs crees")

        # ============================================================
        # 2. Importer le tournoi
        # ============================================================
        print("Import du tournoi...")
        tournois_data = charger_json('tournois.json')

        for t in tournois_data:
            tournoi = Tournoi(
                nom=t['nom'],
                dateDebut=datetime.strptime(
                    t['dateDebut'], '%Y-%m-%d'
                ).date(),
                dateFin=datetime.strptime(
                    t['dateFin'], '%Y-%m-%d'
                ).date(),
                format=t['format'],
                nombreEquipes=t['nombreEquipes'],
                statut=t['statut'],
                idOrganisateur=organisateur.idUtilisateur
            )
            db.session.add(tournoi)

        db.session.commit()
        print(f"  {len(tournois_data)} tournoi(s) importe(s)")

        # ============================================================
        # 3. Importer les équipes
        # ============================================================
        print("Import des equipes...")
        equipes_data = charger_json('equipes.json')

        equipes_map = {}
        # Récupérer l'id réel du tournoi créé
        tournoi_cree = Tournoi.query.first()

        for e in equipes_data:
            equipe = Equipe(
                nom=e['nom'],
                couleur=e.get('couleur'),
                nomCoach=e.get('nomCoach'),
                idTournoi=tournoi_cree.idTournoi
        )
            db.session.add(equipe)
            db.session.flush()
            equipes_map[e['idEquipe']] = equipe.idEquipe

        db.session.commit()
        print(f"  {len(equipes_data)} equipe(s) importee(s)")

        # ============================================================
        # 4. Importer les joueurs
        # ============================================================
        print("Import des joueurs...")
        joueurs_data = charger_json('joueurs.json')

        for j in joueurs_data:
            joueur = Joueur(
                nom=j['nom'],
                prenom=j['prenom'],
                age=j.get('age'),
                numeroMaillot=j.get('numeroMaillot'),
                poste=j.get('poste'),
                idEquipe=equipes_map[j['idEquipe']]
            )
            db.session.add(joueur)

        db.session.commit()
        print(f"  {len(joueurs_data)} joueur(s) importe(s)")

        # ============================================================
        # 5. Importer les matchs
        # ============================================================
        print("Import des matchs...")
        matchs_data = charger_json('matchs.json')

        matchs_map = {}
        for m in matchs_data:
            match = Match(
                dateMatch=datetime.strptime(
                    m['dateMatch'], '%Y-%m-%d'
                ).date(),
                scoreEquipeA=m.get('scoreEquipeA', 0),
                scoreEquipeB=m.get('scoreEquipeB', 0),
                statut=m.get('statut', 'termine'),
                idEquipeA=equipes_map[m['idEquipeA']],
                idEquipeB=equipes_map[m['idEquipeB']],
                idTournoi=tournoi_cree.idTournoi
            )
            db.session.add(match)
            db.session.flush()
            matchs_map[m['idMatch']] = match.idMatch

        db.session.commit()
        print(f"  {len(matchs_data)} match(s) importe(s)")

        # ============================================================
        # 6. Importer les classements
        # ============================================================
        print("Import des classements...")
        classements_data = charger_json('classements.json')

        for c in classements_data:
            classement = Classement(
                points=c.get('points', 0),
                victoires=c.get('victoires', 0),
                nuls=c.get('nuls', 0),
                defaites=c.get('defaites', 0),
                butsPour=c.get('butsPour', 0),
                butsContre=c.get('butsContre', 0),
                differenceButs=c.get('differenceButs', 0),
                rang=c.get('rang'),
                idEquipe=equipes_map[c['idEquipe']],
                idTournoi=tournoi_cree.idTournoi
            )
            db.session.add(classement)

        db.session.commit()
        print(f"  {len(classements_data)} classement(s) importe(s)")

        # ============================================================
        # Résumé
        # ============================================================
        print("\n========================================")
        print("Import termine avec succes !")
        print("========================================")
        print(f"Utilisateurs : {Utilisateur.query.count()}")
        print(f"Tournois     : {Tournoi.query.count()}")
        print(f"Equipes      : {Equipe.query.count()}")
        print(f"Joueurs      : {Joueur.query.count()}")
        print(f"Matchs       : {Match.query.count()}")
        print(f"Classements  : {Classement.query.count()}")
        print("========================================")
        print("\nComptes de connexion :")
        print("  Admin        : admin@arenakick.mg / admin2035")
        print("  Organisateur : organisateur@arenakick.mg / orga2035")
        print("  Spectateur   : spectateur@arenakick.mg / spec2035")

if __name__ == "__main__":
    importer_donnees()