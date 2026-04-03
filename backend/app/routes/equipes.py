from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.equipe import Equipe
from app.models.tournoi import Tournoi
from app.models.utilisateur import Utilisateur

equipes_bp = Blueprint('equipes', __name__)

# ============================================================
# Fonction utilitaire — Récupérer l'utilisateur connecté
# ============================================================
def get_utilisateur_connecte():
    idUtilisateur = get_jwt_identity()
    return Utilisateur.query.get(int(idUtilisateur))

def verifier_role(utilisateur, roles_autorises):
    return utilisateur and utilisateur.typeUtilisateur in roles_autorises

# ============================================================
# ROUTE : Créer une équipe
# POST /api/equipes
# ============================================================
@equipes_bp.route('', methods=['POST'])
@jwt_required()
def creer_equipe():
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle
    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé — Organisateur requis'}), 403

    data = request.get_json()

    # 2. Vérifier les champs requis
    champs_requis = ['nom', 'idTournoi']
    for champ in champs_requis:
        if champ not in data:
            return jsonify({'erreur': f'Champ manquant : {champ}'}), 400

    # 3. Vérifier que le tournoi existe
    tournoi = Tournoi.query.get(data['idTournoi'])
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    # 4. Vérifier que le tournoi est encore en inscription
    if tournoi.statut != 'inscription':
        return jsonify({'erreur': 'Ce tournoi n\'accepte plus de nouvelles équipes'}), 400

    # 5. Vérifier que le nombre max d'équipes n'est pas atteint
    nombre_equipes_actuel = Equipe.query.filter_by(idTournoi=data['idTournoi']).count()
    if nombre_equipes_actuel >= tournoi.nombreEquipes:
        return jsonify({'erreur': f'Ce tournoi est complet — maximum {tournoi.nombreEquipes} équipes'}), 400

    # 6. Vérifier que le nom est unique dans ce tournoi
    equipe_existante = Equipe.query.filter_by(
        nom=data['nom'],
        idTournoi=data['idTournoi']
    ).first()
    if equipe_existante:
        return jsonify({'erreur': 'Une équipe avec ce nom existe déjà dans ce tournoi'}), 409

    # 7. Créer l'équipe
    nouvelle_equipe = Equipe(
        nom=data['nom'],
        couleur=data.get('couleur'),
        logo=data.get('logo'),
        nomCoach=data.get('nomCoach'),
        idTournoi=data['idTournoi']
    )

    db.session.add(nouvelle_equipe)
    db.session.commit()

    return jsonify({
        'message': 'Équipe créée avec succès !',
        'equipe': {
            'id': nouvelle_equipe.idEquipe,
            'nom': nouvelle_equipe.nom,
            'couleur': nouvelle_equipe.couleur,
            'logo': nouvelle_equipe.logo,
            'nomCoach': nouvelle_equipe.nomCoach,
            'idTournoi': nouvelle_equipe.idTournoi
        }
    }), 201

# ============================================================
# ROUTE : Voir toutes les équipes d'un tournoi
# GET /api/equipes/tournoi/<idTournoi>
# ============================================================
@equipes_bp.route('/tournoi/<int:idTournoi>', methods=['GET'])
def get_equipes_tournoi(idTournoi):
    tournoi = Tournoi.query.get(idTournoi)
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    equipes = Equipe.query.filter_by(idTournoi=idTournoi).all()

    resultat = []
    for equipe in equipes:
        resultat.append({
            'id': equipe.idEquipe,
            'nom': equipe.nom,
            'couleur': equipe.couleur,
            'logo': equipe.logo,
            'nomCoach': equipe.nomCoach,
            'idTournoi': equipe.idTournoi
        })

    return jsonify(resultat), 200

# ============================================================
# ROUTE : Voir une équipe précise
# GET /api/equipes/<id>
# ============================================================
@equipes_bp.route('/<int:id>', methods=['GET'])
def get_equipe(id):
    equipe = Equipe.query.get(id)

    if not equipe:
        return jsonify({'erreur': 'Équipe introuvable'}), 404

    return jsonify({
        'id': equipe.idEquipe,
        'nom': equipe.nom,
        'couleur': equipe.couleur,
        'logo': equipe.logo,
        'nomCoach': equipe.nomCoach,
        'idTournoi': equipe.idTournoi
    }), 200

# ============================================================
# ROUTE : Modifier une équipe
# PUT /api/equipes/<id>
# ============================================================
@equipes_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def modifier_equipe(id):
    utilisateur = get_utilisateur_connecte()

    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé'}), 403

    equipe = Equipe.query.get(id)
    if not equipe:
        return jsonify({'erreur': 'Équipe introuvable'}), 404

    # Vérifier que le tournoi est encore en inscription
    tournoi = Tournoi.query.get(equipe.idTournoi)
    if tournoi.statut != 'inscription':
        return jsonify({'erreur': 'Impossible de modifier une équipe — tournoi en cours'}), 400

    data = request.get_json()

    if 'nom' in data:
        equipe.nom = data['nom']
    if 'couleur' in data:
        equipe.couleur = data['couleur']
    if 'logo' in data:
        equipe.logo = data['logo']
    if 'nomCoach' in data:
        equipe.nomCoach = data['nomCoach']

    db.session.commit()

    return jsonify({'message': 'Équipe modifiée avec succès !'}), 200

# ============================================================
# ROUTE : Supprimer une équipe
# DELETE /api/equipes/<id>
# ============================================================
@equipes_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def supprimer_equipe(id):
    utilisateur = get_utilisateur_connecte()

    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé'}), 403

    equipe = Equipe.query.get(id)
    if not equipe:
        return jsonify({'erreur': 'Équipe introuvable'}), 404

    # Vérifier que le tournoi est encore en inscription
    tournoi = Tournoi.query.get(equipe.idTournoi)
    if tournoi.statut != 'inscription':
        return jsonify({'erreur': 'Impossible de supprimer — tournoi en cours'}), 400

    db.session.delete(equipe)
    db.session.commit()

    return jsonify({'message': 'Équipe supprimée avec succès !'}), 200