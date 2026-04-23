from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.algorithms.top_k import TopKAlgorithme
from app.algorithms.kmp import KMPRecherche
from app.models.classement import Classement
from app.models.equipe import Equipe
from app.models.tournoi import Tournoi
from app.algorithms.graphe import GrapheTournoi
from app.models.match import Match
import time

algorithmes_bp = Blueprint('algorithmes', __name__)

# ============================================================
# ROUTE : Top-K équipes d'un tournoi
# GET /api/algorithmes/top-k/<idTournoi>?k=3
# ============================================================
@algorithmes_bp.route('/top-k/<int:idTournoi>', methods=['GET'])
def top_k_equipes(idTournoi):
    k = int(request.args.get('k', 3))

    tournoi = Tournoi.query.get(idTournoi)
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    classements = Classement.query.filter_by(
        idTournoi=idTournoi
    ).all()

    if not classements:
        return jsonify({'erreur': 'Aucun classement disponible'}), 404

    equipes_stats = []
    for c in classements:
        equipe = Equipe.query.get(c.idEquipe)
        equipes_stats.append({
            'idEquipe': c.idEquipe,
            'nom': equipe.nom if equipe else 'Inconnu',
            'points': c.points,
            'victoires': c.victoires,
            'nuls': c.nuls,
            'defaites': c.defaites,
            'butsPour': c.butsPour,
            'butsContre': c.butsContre,
            'differenceButs': c.differenceButs
        })

    # Mesure temps — Top-K optimisé
    debut = time.perf_counter()
    top_k = TopKAlgorithme.top_k_equipes(equipes_stats, k)
    temps_optimise = (time.perf_counter() - debut) * 1000

    # Mesure temps — Solution naïve
    debut = time.perf_counter()
    top_k_naif = TopKAlgorithme.top_k_naif(equipes_stats, k)
    temps_naif = (time.perf_counter() - debut) * 1000

    return jsonify({
        'tournoi': tournoi.nom,
        'k': k,
        'top_k': top_k,
        'comparaison': {
            'optimise_ms': round(temps_optimise, 4),
            'naif_ms': round(temps_naif, 4),
            'algorithme': 'Min-Heap O(n log k)',
            'baseline': 'Tri complet O(n log n)'
        }
    }), 200

# ============================================================
# ROUTE : Recherche KMP d'équipe
# GET /api/algorithmes/recherche?q=barea
# ============================================================
@algorithmes_bp.route('/recherche', methods=['GET'])
def recherche_equipe():
    motif = request.args.get('q', '')

    if not motif:
        return jsonify({'erreur': 'Paramètre q requis'}), 400

    equipes = Equipe.query.all()
    equipes_list = [
        {'idEquipe': e.idEquipe, 'nom': e.nom,
         'couleur': e.couleur, 'idTournoi': e.idTournoi}
        for e in equipes
    ]

    # Mesure temps — KMP optimisé
    debut = time.perf_counter()
    resultats_kmp = KMPRecherche.rechercher_equipes(
        equipes_list, motif
    )
    temps_kmp = (time.perf_counter() - debut) * 1000

    # Mesure temps — Solution naïve
    debut = time.perf_counter()
    resultats_naif = [
        e for e in equipes_list
        if motif.lower() in e['nom'].lower()
    ]
    temps_naif = (time.perf_counter() - debut) * 1000

    return jsonify({
        'motif': motif,
        'resultats': [r['equipe'] for r in resultats_kmp],
        'nombre': len(resultats_kmp),
        'comparaison': {
            'kmp_ms': round(temps_kmp, 4),
            'naif_ms': round(temps_naif, 4),
            'algorithme': 'KMP O(n + m)',
            'baseline': 'Recherche naive O(n x m)'
        }
    }), 200

# ============================================================
# ROUTE : Graphe des confrontations d'un tournoi
# GET /api/algorithmes/graphe/<idTournoi>
# ============================================================
@algorithmes_bp.route('/graphe/<int:idTournoi>', methods=['GET'])
def graphe_tournoi(idTournoi):
    tournoi = Tournoi.query.get(idTournoi)
    if not tournoi:
        return jsonify({'erreur': 'Tournoi introuvable'}), 404

    # Construire le graphe
    graphe = GrapheTournoi()

    # Ajouter les équipes (nœuds)
    equipes = Equipe.query.filter_by(idTournoi=idTournoi).all()
    for equipe in equipes:
        graphe.ajouter_equipe(equipe.idEquipe, equipe.nom)

    # Ajouter les matchs (arêtes)
    matchs = Match.query.filter_by(
        idTournoi=idTournoi,
        statut='termine'
    ).all()
    for match in matchs:
        graphe.ajouter_match(
            match.idEquipeA,
            match.idEquipeB,
            match.scoreEquipeA,
            match.scoreEquipeB
        )

    dominant = graphe.equipe_dominante()

    return jsonify({
        'tournoi': tournoi.nom,
        'graphe': graphe.to_dict(),
        'equipeDominante': dominant,
        'grapheComplet': graphe.est_complet()
    }), 200

# ============================================================
# ROUTE : Confrontation directe entre deux équipes
# GET /api/algorithmes/confrontation/<idA>/<idB>
# ============================================================
@algorithmes_bp.route(
    '/confrontation/<int:idA>/<int:idB>',
    methods=['GET']
)
def confrontation_directe(idA, idB):
    equipeA = Equipe.query.get(idA)
    equipeB = Equipe.query.get(idB)

    if not equipeA or not equipeB:
        return jsonify({'erreur': 'Équipe introuvable'}), 404

    match = Match.query.filter(
        ((Match.idEquipeA == idA) & (Match.idEquipeB == idB)) |
        ((Match.idEquipeA == idB) & (Match.idEquipeB == idA)),
        Match.statut == 'termine'
    ).first()

    if not match:
        return jsonify({
            'erreur': 'Aucun match joué entre ces équipes'
        }), 404

    # Construire graphe pour ce match
    graphe = GrapheTournoi()
    graphe.ajouter_equipe(idA, equipeA.nom)
    graphe.ajouter_equipe(idB, equipeB.nom)
    graphe.ajouter_match(
        match.idEquipeA,
        match.idEquipeB,
        match.scoreEquipeA,
        match.scoreEquipeB
    )

    resultat = graphe.get_resultat_direct(idA, idB)

    return jsonify({
        'equipeA': equipeA.nom,
        'equipeB': equipeB.nom,
        'scoreEquipeA': match.scoreEquipeA,
        'scoreEquipeB': match.scoreEquipeB,
        'resultat': resultat
    }), 200