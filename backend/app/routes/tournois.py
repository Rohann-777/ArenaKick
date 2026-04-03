from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.tournoi import Tournoi
from app.models.utilisateur import Utilisateur
from datetime import datetime

tournois_bp = Blueprint('tournois', __name__)

# ============================================================
# Fonction utilitaire — Vérifier le rôle de l'utilisateur
# ============================================================
def get_utilisateur_connecte():
    idUtilisateur = get_jwt_identity()
    return Utilisateur.query.get(int(idUtilisateur))

def verifier_role(utilisateur, roles_autorises):
    return utilisateur and utilisateur.typeUtilisateur in roles_autorises

# ============================================================
# ROUTE : Créer un tournoi
# POST /api/tournois
# ============================================================
@tournois_bp.route('', methods=['POST'])
@jwt_required()
def creer_tournoi():
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle
    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé — Organisateur requis'}), 403

    data = request.get_json()

    # 2. Vérifier les champs requis
    champs_requis = ['nom', 'dateDebut', 'dateFin', 'format', 'nombreEquipes']
    for champ in champs_requis:
        if champ not in data:
            return jsonify({'erreur': f'Champ manquant : {champ}'}), 400

    # 3. Vérifier que le nom est unique
    tournoi_existant = Tournoi.query.filter_by(nom=data['nom']).first()
    if tournoi_existant:
        return jsonify({'erreur': 'Un tournoi avec ce nom existe déjà'}), 409

    # 4. Vérifier les dates
    try:
        date_debut = datetime.strptime(data['dateDebut'], '%Y-%m-%d').date()
        date_fin   = datetime.strptime(data['dateFin'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'erreur': 'Format de date invalide — utilisez YYYY-MM-DD'}), 400

    if date_fin <= date_debut:
        return jsonify({'erreur': 'La date de fin doit être après la date de début'}), 400

    # 5. Vérifier le nombre d'équipes
    nombres_valides = [4, 8, 16, 32]
    if data['nombreEquipes'] not in nombres_valides:
        return jsonify({'erreur': 'Nombre d\'équipes invalide — choisir 4, 8, 16 ou 32'}), 400

    # 6. Vérifier le format
    formats_valides = ['poules', 'elimination', 'mixte']
    if data['format'] not in formats_valides:
        return jsonify({'erreur': 'Format invalide — choisir poules, elimination ou mixte'}), 400

    # 7. Créer le tournoi
    nouveau_tournoi = Tournoi(
        nom=data['nom'],
        dateDebut=date_debut,
        dateFin=date_fin,
        format=data['format'],
        nombreEquipes=data['nombreEquipes'],
        statut='inscription',
        idOrganisateur=utilisateur.idUtilisateur
    )

    db.session.add(nouveau_tournoi)
    db.session.commit()

    return jsonify({
        'message': 'Tournoi créé avec succès !',
        'tournoi': {
            'id': nouveau_tournoi.idTournoi,
            'nom': nouveau_tournoi.nom,
            'dateDebut': str(nouveau_tournoi.dateDebut),
            'dateFin': str(nouveau_tournoi.dateFin),
            'format': nouveau_tournoi.format,
            'nombreEquipes': nouveau_tournoi.nombreEquipes,
            'statut': nouveau_tournoi.statut
        }
    }), 201

# ============================================================
# ROUTE : Voir tous les tournois
# GET /api/tournois
# ============================================================
@tournois_bp.route('', methods=['GET'])
def get_tournois():
    tournois = Tournoi.query.all()

    resultat = []
    for tournoi in tournois:
        resultat.append({
            'id': tournoi.idTournoi,
            'nom': tournoi.nom,
            'dateDebut': str(tournoi.dateDebut),
            'dateFin': str(tournoi.dateFin),
            'format': tournoi.format,
            'nombreEquipes': tournoi.nombreEquipes,
            'statut': tournoi.statut
        })

    return jsonify(resultat), 200

# ============================================================
# ROUTE : Voir un tournoi précis
# GET /api/tournois/<id>
# ============================================================
@tournois_bp.route('/<int:id>', methods=['GET'])
def get_tournoi(id):
    tournoi = Tournoi.query.get(id)

    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    return jsonify({
        'id': tournoi.idTournoi,
        'nom': tournoi.nom,
        'dateDebut': str(tournoi.dateDebut),
        'dateFin': str(tournoi.dateFin),
        'format': tournoi.format,
        'nombreEquipes': tournoi.nombreEquipes,
        'statut': tournoi.statut
    }), 200

# ============================================================
# ROUTE : Modifier un tournoi
# PUT /api/tournois/<id>
# ============================================================
@tournois_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def modifier_tournoi(id):
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle
    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé'}), 403

    tournoi = Tournoi.query.get(id)

    # 2. Vérifier si le tournoi existe
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    # 3. Vérifier que le tournoi n'est pas en cours
    if tournoi.statut == 'en_cours':
        return jsonify({'erreur': 'Impossible de modifier un tournoi en cours'}), 400

    data = request.get_json()

    # 4. Mettre à jour les champs
    if 'nom' in data:
        tournoi.nom = data['nom']
    if 'dateDebut' in data:
        tournoi.dateDebut = datetime.strptime(data['dateDebut'], '%Y-%m-%d').date()
    if 'dateFin' in data:
        tournoi.dateFin = datetime.strptime(data['dateFin'], '%Y-%m-%d').date()
    if 'format' in data:
        tournoi.format = data['format']
    if 'nombreEquipes' in data:
        tournoi.nombreEquipes = data['nombreEquipes']

    db.session.commit()

    return jsonify({'message': 'Tournoi modifié avec succès !'}), 200

# ============================================================
# ROUTE : Supprimer un tournoi
# DELETE /api/tournois/<id>
# ============================================================
@tournois_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def supprimer_tournoi(id):
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle — seul l'admin peut supprimer
    if not verifier_role(utilisateur, ['admin']):
        return jsonify({'erreur': 'Accès refusé — Administrateur requis'}), 403

    tournoi = Tournoi.query.get(id)

    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    db.session.delete(tournoi)
    db.session.commit()

    return jsonify({'message': 'Tournoi supprimé avec succès !'}), 200