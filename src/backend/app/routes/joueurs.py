from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.joueur import Joueur
from app.models.equipe import Equipe
from app.models.tournoi import Tournoi
from app.models.utilisateur import Utilisateur

joueurs_bp = Blueprint('joueurs', __name__)

# ============================================================
# Fonction utilitaire
# ============================================================
def get_utilisateur_connecte():
    idUtilisateur = get_jwt_identity()
    return Utilisateur.query.get(int(idUtilisateur))

def verifier_role(utilisateur, roles_autorises):
    return utilisateur and utilisateur.typeUtilisateur in roles_autorises

# ============================================================
# ROUTE : Créer un joueur
# POST /api/joueurs
# ============================================================
@joueurs_bp.route('', methods=['POST'])
@jwt_required()
def creer_joueur():
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle
    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé — Organisateur requis'}), 403

    data = request.get_json()

    # 2. Vérifier les champs requis
    champs_requis = ['nom', 'prenom', 'idEquipe']
    for champ in champs_requis:
        if champ not in data:
            return jsonify({'erreur': f'Champ manquant : {champ}'}), 400

    # 3. Vérifier que l'équipe existe
    equipe = Equipe.query.get(data['idEquipe'])
    if not equipe:
        return jsonify({'erreur': 'Équipe introuvable'}), 404

    # 4. Vérifier que le tournoi est encore en inscription
    tournoi = Tournoi.query.get(equipe.idTournoi)
    if tournoi.statut == 'termine':
        return jsonify({'erreur': 'Ce tournoi est terminé'}), 400

    # 5. Vérifier l'âge minimum
    if 'age' in data and data['age'] < 16:
        return jsonify({'erreur': 'Le joueur doit avoir au moins 16 ans'}), 400

    # 6. Vérifier que le numéro de maillot est unique dans l'équipe
    if 'numeroMaillot' in data and data['numeroMaillot']:
        maillot_existant = Joueur.query.filter_by(
            idEquipe=data['idEquipe'],
            numeroMaillot=data['numeroMaillot']
        ).first()
        if maillot_existant:
            return jsonify({
                'erreur': f'Le numéro {data["numeroMaillot"]} est déjà pris dans cette équipe'
            }), 409

    # 7. Vérifier que le joueur n'existe pas déjà dans l'équipe
    joueur_existant = Joueur.query.filter_by(
        nom=data['nom'],
        prenom=data['prenom'],
        idEquipe=data['idEquipe']
    ).first()
    if joueur_existant:
        return jsonify({'erreur': 'Ce joueur existe déjà dans cette équipe'}), 409

    # 8. Créer le joueur
    nouveau_joueur = Joueur(
        nom=data['nom'],
        prenom=data['prenom'],
        age=data.get('age'),
        poste=data.get('poste'),
        numeroMaillot=data.get('numeroMaillot'),
        idEquipe=data['idEquipe']
    )

    db.session.add(nouveau_joueur)
    db.session.commit()

    return jsonify({
        'message': 'Joueur créé avec succès !',
        'joueur': {
            'id': nouveau_joueur.idJoueur,
            'nom': nouveau_joueur.nom,
            'prenom': nouveau_joueur.prenom,
            'age': nouveau_joueur.age,
            'poste': nouveau_joueur.poste,
            'numeroMaillot': nouveau_joueur.numeroMaillot,
            'idEquipe': nouveau_joueur.idEquipe
        }
    }), 201

# ============================================================
# ROUTE : Voir tous les joueurs d'une équipe
# GET /api/joueurs/equipe/<idEquipe>
# ============================================================
@joueurs_bp.route('/equipe/<int:idEquipe>', methods=['GET'])
def get_joueurs_equipe(idEquipe):
    equipe = Equipe.query.get(idEquipe)
    if not equipe:
        return jsonify({'erreur': 'Équipe introuvable'}), 404

    joueurs = Joueur.query.filter_by(idEquipe=idEquipe).all()

    resultat = []
    for joueur in joueurs:
        resultat.append({
            'id': joueur.idJoueur,
            'nom': joueur.nom,
            'prenom': joueur.prenom,
            'age': joueur.age,
            'poste': joueur.poste,
            'numeroMaillot': joueur.numeroMaillot,
            'idEquipe': joueur.idEquipe
        })

    return jsonify(resultat), 200

# ============================================================
# ROUTE : Voir un joueur précis
# GET /api/joueurs/<id>
# ============================================================
@joueurs_bp.route('/<int:id>', methods=['GET'])
def get_joueur(id):
    joueur = Joueur.query.get(id)
    if not joueur:
        return jsonify({'erreur': 'Joueur introuvable'}), 404

    return jsonify({
        'id': joueur.idJoueur,
        'nom': joueur.nom,
        'prenom': joueur.prenom,
        'age': joueur.age,
        'poste': joueur.poste,
        'numeroMaillot': joueur.numeroMaillot,
        'idEquipe': joueur.idEquipe
    }), 200

# ============================================================
# ROUTE : Modifier un joueur
# PUT /api/joueurs/<id>
# ============================================================
@joueurs_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def modifier_joueur(id):
    utilisateur = get_utilisateur_connecte()

    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé'}), 403

    joueur = Joueur.query.get(id)
    if not joueur:
        return jsonify({'erreur': 'Joueur introuvable'}), 404

    data = request.get_json()

    # Vérifier l'âge minimum
    if 'age' in data and data['age'] < 16:
        return jsonify({'erreur': 'Le joueur doit avoir au moins 16 ans'}), 400

    if 'nom' in data:
        joueur.nom = data['nom']
    if 'prenom' in data:
        joueur.prenom = data['prenom']
    if 'age' in data:
        joueur.age = data['age']
    if 'poste' in data:
        joueur.poste = data['poste']
    if 'numeroMaillot' in data:
        joueur.numeroMaillot = data['numeroMaillot']

    db.session.commit()

    return jsonify({'message': 'Joueur modifié avec succès !'}), 200

# ============================================================
# ROUTE : Supprimer un joueur
# DELETE /api/joueurs/<id>
# ============================================================
@joueurs_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def supprimer_joueur(id):
    utilisateur = get_utilisateur_connecte()

    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé'}), 403

    joueur = Joueur.query.get(id)
    if not joueur:
        return jsonify({'erreur': 'Joueur introuvable'}), 404

    db.session.delete(joueur)
    db.session.commit()

    return jsonify({'message': 'Joueur supprimé avec succès !'}), 200