from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.match import Match
from app.models.equipe import Equipe
from app.models.tournoi import Tournoi
from app.models.classement import Classement
from app.models.utilisateur import Utilisateur
from datetime import datetime, timedelta
import random

matchs_bp = Blueprint('matchs', __name__)

# ============================================================
# Fonction utilitaire
# ============================================================
def get_utilisateur_connecte():
    idUtilisateur = get_jwt_identity()
    return Utilisateur.query.get(int(idUtilisateur))

def verifier_role(utilisateur, roles_autorises):
    return utilisateur and utilisateur.typeUtilisateur in roles_autorises

# ============================================================
# ALGORITHME ROUND-ROBIN
# ============================================================
def generer_round_robin(equipes):
    n = len(equipes)
    matchs = []

    # Si nombre impair on ajoute une équipe fictive
    if n % 2 != 0:
        equipes.append(None)
        n += 1

    # Rotation Round-Robin
    for journee in range(n - 1):
        for i in range(n // 2):
            equipeA = equipes[i]
            equipeB = equipes[n - 1 - i]

            # On ignore les matchs avec l'équipe fictive
            if equipeA is not None and equipeB is not None:
                matchs.append((equipeA, equipeB))

        # Rotation — on fixe la première équipe
        equipes = [equipes[0]] + [equipes[-1]] + equipes[1:-1]

    return matchs

# ============================================================
# ROUTE : Générer les matchs (Round-Robin)
# POST /api/matchs/generer/<idTournoi>
# ============================================================
@matchs_bp.route('/generer/<int:idTournoi>', methods=['POST'])
@jwt_required()
def generer_matchs(idTournoi):
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle
    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé — Organisateur requis'}), 403

    # 2. Vérifier que le tournoi existe
    tournoi = Tournoi.query.get(idTournoi)
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    # 3. Vérifier que le tournoi est en inscription
    if tournoi.statut != 'inscription':
        return jsonify({'erreur': 'Les matchs ont déjà été générés'}), 400

    # 4. Récupérer les équipes
    equipes = Equipe.query.filter_by(idTournoi=idTournoi).all()

    # 5. Vérifier le nombre minimum d'équipes
    if len(equipes) < 2:
        return jsonify({'erreur': 'Il faut au moins 2 équipes pour générer les matchs'}), 400

    # 6. Mélange aléatoire pour la transparence
    random.shuffle(equipes)

    # 7. Générer les matchs avec l'algorithme Round-Robin
    paires_matchs = generer_round_robin(equipes.copy())

    # 8. Créer les matchs dans la BDD
    date_match = tournoi.dateDebut
    matchs_crees = []

    for equipeA, equipeB in paires_matchs:
        nouveau_match = Match(
            dateMatch=date_match,
            statut='programme',
            idEquipeA=equipeA.idEquipe,
            idEquipeB=equipeB.idEquipe,
            idTournoi=idTournoi
        )
        db.session.add(nouveau_match)
        matchs_crees.append(nouveau_match)

        # Espacer les matchs d'un jour
        date_match = date_match + timedelta(days=1)

    # 9. Initialiser le classement pour chaque équipe
    for equipe in Equipe.query.filter_by(idTournoi=idTournoi).all():
        classement = Classement(
            points=0,
            victoires=0,
            defaites=0,
            nuls=0,
            butsPour=0,
            butsContre=0,
            differenceButs=0,
            idEquipe=equipe.idEquipe,
            idTournoi=idTournoi
        )
        db.session.add(classement)

    # 10. Mettre à jour le statut du tournoi
    tournoi.statut = 'en_cours'
    db.session.commit()

    return jsonify({
        'message': f'{len(matchs_crees)} matchs générés avec succès !',
        'tournoi': tournoi.nom,
        'statut': tournoi.statut,
        'matchs': [
            {
                'id': m.idMatch,
                'equipeA': m.idEquipeA,
                'equipeB': m.idEquipeB,
                'date': str(m.dateMatch),
                'statut': m.statut
            }
            for m in matchs_crees
        ]
    }), 201

# ============================================================
# ROUTE : Voir tous les matchs d'un tournoi
# GET /api/matchs/tournoi/<idTournoi>
# ============================================================
@matchs_bp.route('/tournoi/<int:idTournoi>', methods=['GET'])
def get_matchs_tournoi(idTournoi):
    tournoi = Tournoi.query.get(idTournoi)
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    matchs = Match.query.filter_by(idTournoi=idTournoi).all()

    resultat = []
    for match in matchs:
        resultat.append({
            'id': match.idMatch,
            'equipeA': match.equipeA.nom,
            'equipeB': match.equipeB.nom,
            'scoreEquipeA': match.scoreEquipeA,
            'scoreEquipeB': match.scoreEquipeB,
            'date': str(match.dateMatch),
            'heure': str(match.heureMatch) if match.heureMatch else None,
            'terrain': match.terrain,
            'statut': match.statut
        })

    return jsonify(resultat), 200

# ============================================================
# ROUTE : Saisir le résultat d'un match
# PUT /api/matchs/<id>/resultat
# ============================================================
@matchs_bp.route('/<int:id>/resultat', methods=['PUT'])
@jwt_required()
def saisir_resultat(id):
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle
    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé — Organisateur requis'}), 403

    match = Match.query.get(id)
    if not match:
        return jsonify({'erreur': 'Match introuvable'}), 404

    # 2. Vérifier que le match n'est pas déjà terminé
    if match.statut == 'termine':
        return jsonify({'erreur': 'Ce match est déjà terminé'}), 400

    data = request.get_json()

    # 3. Vérifier les scores
    if 'scoreEquipeA' not in data or 'scoreEquipeB' not in data:
        return jsonify({'erreur': 'Scores manquants'}), 400

    if data['scoreEquipeA'] < 0 or data['scoreEquipeB'] < 0:
        return jsonify({'erreur': 'Les scores doivent être positifs'}), 400

    scoreA = data['scoreEquipeA']
    scoreB = data['scoreEquipeB']

    # 4. Mettre à jour le match
    match.scoreEquipeA = scoreA
    match.scoreEquipeB = scoreB
    match.statut = 'termine'

    if 'terrain' in data and data['terrain']:
        match.terrain = data['terrain']
    if 'heureMatch' in data and data['heureMatch']:
        match.heureMatch = data['heureMatch']

    # 5. Mettre à jour le classement
    classementA = Classement.query.filter_by(
        idEquipe=match.idEquipeA,
        idTournoi=match.idTournoi
    ).first()

    classementB = Classement.query.filter_by(
        idEquipe=match.idEquipeB,
        idTournoi=match.idTournoi
    ).first()

    # Mettre à jour les buts
    classementA.butsPour    += scoreA
    classementA.butsContre  += scoreB
    classementB.butsPour    += scoreB
    classementB.butsContre  += scoreA

    # Victoire équipe A
    if scoreA > scoreB:
        classementA.victoires  += 1
        classementA.points     += 3
        classementB.defaites   += 1

    # Victoire équipe B
    elif scoreB > scoreA:
        classementB.victoires  += 1
        classementB.points     += 3
        classementA.defaites   += 1

    # Match nul
    else:
        classementA.nuls    += 1
        classementA.points  += 1
        classementB.nuls    += 1
        classementB.points  += 1

    # Mettre à jour la différence de buts
    classementA.differenceButs = classementA.butsPour - classementA.butsContre
    classementB.differenceButs = classementB.butsPour - classementB.butsContre

    db.session.commit()

    return jsonify({
        'message': 'Résultat enregistré avec succès !',
        'match': {
            'id': match.idMatch,
            'equipeA': match.equipeA.nom,
            'equipeB': match.equipeB.nom,
            'scoreEquipeA': match.scoreEquipeA,
            'scoreEquipeB': match.scoreEquipeB,
            'statut': match.statut
        }
    }), 200

# ============================================================
# ROUTE : Voir le classement d'un tournoi
# GET /api/matchs/classement/<idTournoi>
# ============================================================
@matchs_bp.route('/classement/<int:idTournoi>', methods=['GET'])
def get_classement(idTournoi):
    tournoi = Tournoi.query.get(idTournoi)
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    # Tri multi-critères FIFA
    classements = Classement.query.filter_by(idTournoi=idTournoi).order_by(
        Classement.points.desc(),
        Classement.differenceButs.desc(),
        Classement.butsPour.desc()
    ).all()

    resultat = []
    for rang, classement in enumerate(classements, start=1):
        equipe = Equipe.query.get(classement.idEquipe)
        resultat.append({
            'rang': rang,
            'equipe': equipe.nom,
            'points': classement.points,
            'victoires': classement.victoires,
            'nuls': classement.nuls,
            'defaites': classement.defaites,
            'butsPour': classement.butsPour,
            'butsContre': classement.butsContre,
            'differenceButs': classement.differenceButs
        })

    return jsonify(resultat), 200