import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))

from app.algorithms.kmp import KMPRecherche
from app.algorithms.top_k import TopKAlgorithme
from app.algorithms.graphe import GrapheTournoi

# ============================================================
# Tests KMP
# ============================================================
class TestKMP:

    def test_kmp_trouve_motif_simple(self):
        positions = KMPRecherche.rechercher("Barea", "area")
        assert positions == [1]

    def test_kmp_insensible_casse(self):
        positions = KMPRecherche.rechercher("BAREA", "barea")
        assert positions == [0]

    def test_kmp_motif_absent(self):
        positions = KMPRecherche.rechercher("Barea", "xyz")
        assert positions == []

    def test_kmp_motif_vide(self):
        positions = KMPRecherche.rechercher("Barea", "")
        assert positions == []

    def test_kmp_vs_naif_meme_resultat(self):
        texte = "FC Fosa Juniors Madagascar"
        motif = "Fosa"
        kmp = KMPRecherche.rechercher(texte, motif)
        naif = KMPRecherche.rechercher_naif(texte, motif)
        assert kmp == naif

# ============================================================
# Tests Top-K
# ============================================================
class TestTopK:

    def setup_method(self):
        self.equipes = [
            {'nom': 'Barea', 'points': 10,
             'differenceButs': 5, 'butsPour': 15},
            {'nom': 'COSFA', 'points': 7,
             'differenceButs': 2, 'butsPour': 10},
            {'nom': 'Adema', 'points': 12,
             'differenceButs': 8, 'butsPour': 20},
            {'nom': 'Fosa', 'points': 9,
             'differenceButs': 3, 'butsPour': 12},
            {'nom': 'Elgeco', 'points': 5,
             'differenceButs': -2, 'butsPour': 8},
        ]

    def test_top_k_retourne_k_elements(self):
        result = TopKAlgorithme.top_k_equipes(self.equipes, 3)
        assert len(result) == 3

    def test_top_k_premier_est_meilleur(self):
        result = TopKAlgorithme.top_k_equipes(self.equipes, 1)
        assert result[0]['nom'] == 'Adema'

    def test_top_k_vs_naif_meme_resultat(self):
        optimise = TopKAlgorithme.top_k_equipes(
            self.equipes, 3
        )
        naif = TopKAlgorithme.top_k_naif(self.equipes, 3)
        assert [e['nom'] for e in optimise] == \
               [e['nom'] for e in naif]

    def test_top_k_superieur_n(self):
        result = TopKAlgorithme.top_k_equipes(
            self.equipes, 100
        )
        assert len(result) == len(self.equipes)

    def test_top_k_liste_vide(self):
        result = TopKAlgorithme.top_k_equipes([], 3)
        assert result == []

# ============================================================
# Tests Graphe
# ============================================================
class TestGraphe:

    def setup_method(self):
        self.graphe = GrapheTournoi()
        self.graphe.ajouter_equipe(1, "Barea")
        self.graphe.ajouter_equipe(2, "COSFA")
        self.graphe.ajouter_equipe(3, "Adema")
        self.graphe.ajouter_match(1, 2, 3, 1)
        self.graphe.ajouter_match(2, 3, 2, 2)
        self.graphe.ajouter_match(1, 3, 1, 0)

    def test_graphe_nombre_noeuds(self):
        assert len(self.graphe.noeuds) == 3

    def test_graphe_victoire_oriente(self):
        confrontations = self.graphe.get_confrontations(1)
        adversaires = [c['adversaire'] for c in confrontations]
        assert 2 in adversaires

    def test_graphe_nul_bidirectionnel(self):
        confA = self.graphe.get_confrontations(2)
        confB = self.graphe.get_confrontations(3)
        adversairesA = [c['adversaire'] for c in confA]
        adversairesB = [c['adversaire'] for c in confB]
        assert 3 in adversairesA
        assert 2 in adversairesB

    def test_graphe_resultat_direct(self):
        resultat = self.graphe.get_resultat_direct(1, 2)
        assert resultat is not None
        assert resultat['vainqueur'] == 1

    def test_graphe_equipe_dominante(self):
        dominant = self.graphe.equipe_dominante()
        assert dominant['idEquipe'] == 1

# ============================================================
# Tests Round-Robin
# ============================================================
class TestRoundRobin:

    def test_round_robin_nombre_matchs(self):
        from app.routes.matchs import generer_round_robin
        from collections import namedtuple
        Equipe = namedtuple('Equipe', ['idEquipe', 'nom'])
        equipes = [Equipe(i, f"Equipe{i}") for i in range(1, 5)]
        matchs = generer_round_robin(equipes)
        assert len(matchs) == 6

    def test_round_robin_pas_de_doublons(self):
        from app.routes.matchs import generer_round_robin
        from collections import namedtuple
        Equipe = namedtuple('Equipe', ['idEquipe', 'nom'])
        equipes = [Equipe(i, f"Equipe{i}") for i in range(1, 5)]
        matchs = generer_round_robin(equipes)
        paires = set()
        for a, b in matchs:
            paire = tuple(sorted([a.idEquipe, b.idEquipe]))
            assert paire not in paires
            paires.add(paire)