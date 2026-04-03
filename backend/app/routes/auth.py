from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.utilisateur import Utilisateur

auth_bp = Blueprint('auth', __name__)

# ============================================================
# ROUTE : Inscription
# POST /api/auth/register
# ============================================================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # 1. Vérifier que toutes les données sont présentes
    champs_requis = ['nom', 'prenom', 'email', 'motDePasse', 'typeUtilisateur']
    for champ in champs_requis:
        if champ not in data:
            return jsonify({'erreur': f'Champ manquant : {champ}'}), 400

    # 2. Vérifier si l'email existe déjà
    utilisateur_existant = Utilisateur.query.filter_by(email=data['email']).first()
    if utilisateur_existant:
        return jsonify({'erreur': 'Cet email est déjà utilisé'}), 409

    # 3. Vérifier le type d'utilisateur
    types_valides = ['admin', 'organisateur', 'joueur', 'spectateur']
    if data['typeUtilisateur'] not in types_valides:
        return jsonify({'erreur': 'Type utilisateur invalide'}), 400

    # 4. Vérifier la longueur du mot de passe
    if len(data['motDePasse']) < 8:
        return jsonify({'erreur': 'Le mot de passe doit contenir au moins 8 caractères'}), 400

    # 5. Chiffrer le mot de passe
    mot_de_passe_chiffre = generate_password_hash(data['motDePasse'])

    # 6. Créer le nouvel utilisateur
    nouvel_utilisateur = Utilisateur(
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        motDePasse=mot_de_passe_chiffre,
        typeUtilisateur=data['typeUtilisateur']
    )

    # 7. Sauvegarder dans MySQL
    db.session.add(nouvel_utilisateur)
    db.session.commit()

    return jsonify({
        'message': 'Inscription réussie !',
        'utilisateur': {
            'id': nouvel_utilisateur.idUtilisateur,
            'nom': nouvel_utilisateur.nom,
            'prenom': nouvel_utilisateur.prenom,
            'email': nouvel_utilisateur.email,
            'type': nouvel_utilisateur.typeUtilisateur
        }
    }), 201


# ============================================================
# ROUTE : Connexion
# POST /api/auth/login
# ============================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # 1. Vérifier que email et mot de passe sont présents
    if 'email' not in data or 'motDePasse' not in data:
        return jsonify({'erreur': 'Email et mot de passe requis'}), 400

    # 2. Chercher l'utilisateur dans la BDD
    utilisateur = Utilisateur.query.filter_by(email=data['email']).first()

    # 3. Vérifier si l'utilisateur existe et si le mot de passe est correct
    if not utilisateur or not check_password_hash(utilisateur.motDePasse, data['motDePasse']):
        return jsonify({'erreur': 'Email ou mot de passe incorrect'}), 401

    # 4. Générer le token JWT
    token = create_access_token(identity=str(utilisateur.idUtilisateur))

    return jsonify({
        'message': 'Connexion réussie !',
        'token': token,
        'utilisateur': {
            'id': utilisateur.idUtilisateur,
            'nom': utilisateur.nom,
            'prenom': utilisateur.prenom,
            'email': utilisateur.email,
            'type': utilisateur.typeUtilisateur
        }
    }), 200


# ============================================================
# ROUTE : Profil (route protégée par JWT)
# GET /api/auth/profil
# ============================================================
@auth_bp.route('/profil', methods=['GET'])
@jwt_required()
def profil():
    # Récupérer l'identité depuis le token JWT
    idUtilisateur = get_jwt_identity()

    # Chercher l'utilisateur dans la BDD
    utilisateur = Utilisateur.query.get(int(idUtilisateur))

    if not utilisateur:
        return jsonify({'erreur': 'Utilisateur introuvable'}), 404

    return jsonify({
        'id': utilisateur.idUtilisateur,
        'nom': utilisateur.nom,
        'prenom': utilisateur.prenom,
        'email': utilisateur.email,
        'type': utilisateur.typeUtilisateur,
        'dateInscription': str(utilisateur.dateInscription)
    }), 200