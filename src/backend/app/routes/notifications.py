from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.notification import Notification
from app.models.utilisateur import Utilisateur
from app.models.match import Match
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

# ============================================================
# Fonction utilitaire
# ============================================================
def get_utilisateur_connecte():
    idUtilisateur = get_jwt_identity()
    return Utilisateur.query.get(int(idUtilisateur))

def verifier_role(utilisateur, roles_autorises):
    return utilisateur and utilisateur.typeUtilisateur in roles_autorises

# ============================================================
# ROUTE : Créer une notification
# POST /api/notifications
# ============================================================
@notifications_bp.route('', methods=['POST'])
@jwt_required()
def creer_notification():
    utilisateur = get_utilisateur_connecte()

    # 1. Vérifier le rôle
    if not verifier_role(utilisateur, ['organisateur', 'admin']):
        return jsonify({'erreur': 'Accès refusé — Organisateur requis'}), 403

    data = request.get_json()

    # 2. Vérifier les champs requis
    champs_requis = ['contenu', 'type', 'idUtilisateur']
    for champ in champs_requis:
        if champ not in data:
            return jsonify({'erreur': f'Champ manquant : {champ}'}), 400

    # 3. Vérifier le type de notification
    types_valides = ['rappel_match', 'resultat', 'info']
    if data['type'] not in types_valides:
        return jsonify({
            'erreur': 'Type invalide — choisir rappel_match, resultat ou info'
        }), 400

    # 4. Vérifier que l'utilisateur destinataire existe
    destinataire = Utilisateur.query.get(data['idUtilisateur'])
    if not destinataire:
        return jsonify({'erreur': 'Utilisateur destinataire introuvable'}), 404

    # 5. Vérifier que le match existe si fourni
    if 'idMatch' in data and data['idMatch']:
        match = Match.query.get(data['idMatch'])
        if not match:
            return jsonify({'erreur': 'Match introuvable'}), 404

    # 6. Créer la notification
    nouvelle_notification = Notification(
        contenu=data['contenu'],
        type=data['type'],
        lu=False,
        idUtilisateur=data['idUtilisateur'],
        idMatch=data.get('idMatch')
    )

    db.session.add(nouvelle_notification)
    db.session.commit()

    return jsonify({
        'message': 'Notification envoyée avec succès !',
        'notification': {
            'id': nouvelle_notification.idNotification,
            'contenu': nouvelle_notification.contenu,
            'type': nouvelle_notification.type,
            'dateEnvoi': str(nouvelle_notification.dateEnvoi),
            'lu': nouvelle_notification.lu,
            'idUtilisateur': nouvelle_notification.idUtilisateur
        }
    }), 201

# ============================================================
# ROUTE : Voir toutes les notifications d'un utilisateur
# GET /api/notifications/mes-notifications
# ============================================================
@notifications_bp.route('/mes-notifications', methods=['GET'])
@jwt_required()
def get_mes_notifications():
    idUtilisateur = get_jwt_identity()

    notifications = Notification.query.filter_by(
        idUtilisateur=int(idUtilisateur)
    ).order_by(Notification.dateEnvoi.desc()).all()

    resultat = []
    for notif in notifications:
        resultat.append({
            'id': notif.idNotification,
            'contenu': notif.contenu,
            'type': notif.type,
            'dateEnvoi': str(notif.dateEnvoi),
            'lu': notif.lu,
            'idMatch': notif.idMatch
        })

    return jsonify(resultat), 200

# ============================================================
# ROUTE : Marquer une notification comme lue
# PUT /api/notifications/<id>/lire
# ============================================================
@notifications_bp.route('/<int:id>/lire', methods=['PUT'])
@jwt_required()
def marquer_lue(id):
    idUtilisateur = get_jwt_identity()

    notification = Notification.query.get(id)
    if not notification:
        return jsonify({'erreur': 'Notification introuvable'}), 404

    # Vérifier que la notification appartient à l'utilisateur connecté
    if notification.idUtilisateur != int(idUtilisateur):
        return jsonify({'erreur': 'Accès refusé'}), 403

    notification.lu = True
    db.session.commit()

    return jsonify({'message': 'Notification marquée comme lue'}), 200

# ============================================================
# ROUTE : Marquer toutes les notifications comme lues
# PUT /api/notifications/tout-lire
# ============================================================
@notifications_bp.route('/tout-lire', methods=['PUT'])
@jwt_required()
def marquer_tout_lue():
    idUtilisateur = get_jwt_identity()

    Notification.query.filter_by(
        idUtilisateur=int(idUtilisateur),
        lu=False
    ).update({'lu': True})

    db.session.commit()

    return jsonify({'message': 'Toutes les notifications marquées comme lues'}), 200

# ============================================================
# ROUTE : Supprimer une notification
# DELETE /api/notifications/<id>
# ============================================================
@notifications_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def supprimer_notification(id):
    idUtilisateur = get_jwt_identity()

    notification = Notification.query.get(id)
    if not notification:
        return jsonify({'erreur': 'Notification introuvable'}), 404

    # Vérifier que la notification appartient à l'utilisateur
    if notification.idUtilisateur != int(idUtilisateur):
        return jsonify({'erreur': 'Accès refusé'}), 403

    db.session.delete(notification)
    db.session.commit()

    return jsonify({'message': 'Notification supprimée avec succès !'}), 200

# ============================================================
# ROUTE : Compter les notifications non lues
# GET /api/notifications/non-lues
# ============================================================
@notifications_bp.route('/non-lues', methods=['GET'])
@jwt_required()
def compter_non_lues():
    idUtilisateur = get_jwt_identity()

    count = Notification.query.filter_by(
        idUtilisateur=int(idUtilisateur),
        lu=False
    ).count()

    return jsonify({'nonLues': count}), 200