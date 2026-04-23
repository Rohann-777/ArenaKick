class GrapheTournoi:
    """
    Graphe orienté pondéré représentant les confrontations
    entre équipes d'un tournoi.

    Structure : Liste d'adjacence
    - Nœuds : équipes
    - Arêtes : matchs joués (orientées : vainqueur → perdant)
    - Poids : score du match

    Complexité mémoire : O(V + E)
    où V = nombre d'équipes, E = nombre de matchs
    """

    def __init__(self):
        self.noeuds = {}
        self.adjacence = {}

    def ajouter_equipe(self, idEquipe, nomEquipe):
        """Ajoute un nœud (équipe) au graphe. O(1)"""
        self.noeuds[idEquipe] = nomEquipe
        if idEquipe not in self.adjacence:
            self.adjacence[idEquipe] = []

    def ajouter_match(self, idEquipeA, idEquipeB,
                      scoreA, scoreB):
        """
        Ajoute une arête orientée selon le résultat.
        Victoire A → arête A vers B
        Victoire B → arête B vers A
        Nul → arêtes dans les deux sens
        O(1)
        """
        if idEquipeA not in self.adjacence:
            self.adjacence[idEquipeA] = []
        if idEquipeB not in self.adjacence:
            self.adjacence[idEquipeB] = []

        match_info = {
            'scoreA': scoreA,
            'scoreB': scoreB,
            'nomA': self.noeuds.get(idEquipeA, str(idEquipeA)),
            'nomB': self.noeuds.get(idEquipeB, str(idEquipeB))
        }

        if scoreA > scoreB:
            # A a gagné → arête A → B
            self.adjacence[idEquipeA].append({
                'adversaire': idEquipeB,
                'resultat': 'victoire',
                'score': f"{scoreA}-{scoreB}",
                **match_info
            })
        elif scoreB > scoreA:
            # B a gagné → arête B → A
            self.adjacence[idEquipeB].append({
                'adversaire': idEquipeA,
                'resultat': 'victoire',
                'score': f"{scoreB}-{scoreA}",
                **match_info
            })
        else:
            # Nul → arêtes dans les deux sens
            self.adjacence[idEquipeA].append({
                'adversaire': idEquipeB,
                'resultat': 'nul',
                'score': f"{scoreA}-{scoreB}",
                **match_info
            })
            self.adjacence[idEquipeB].append({
                'adversaire': idEquipeA,
                'resultat': 'nul',
                'score': f"{scoreA}-{scoreB}",
                **match_info
            })

    def get_confrontations(self, idEquipe):
        """
        Retourne toutes les confrontations d'une équipe.
        O(degree(v))
        """
        return self.adjacence.get(idEquipe, [])

    def get_resultat_direct(self, idEquipeA, idEquipeB):
        """
        Retourne le résultat direct entre deux équipes.
        Utile pour départager les égalités FIFA.
        O(degree(v))
        """
        for match in self.adjacence.get(idEquipeA, []):
            if match['adversaire'] == idEquipeB:
                return {
                    'vainqueur': idEquipeA,
                    'score': match['score'],
                    'resultat': match['resultat']
                }
        for match in self.adjacence.get(idEquipeB, []):
            if match['adversaire'] == idEquipeA:
                return {
                    'vainqueur': idEquipeB,
                    'score': match['score'],
                    'resultat': match['resultat']
                }
        return None

    def equipe_dominante(self):
        """
        Retourne l'équipe avec le plus de victoires directes.
        O(V + E)
        """
        victoires = {id: 0 for id in self.noeuds}
        for idEquipe, matchs in self.adjacence.items():
            for match in matchs:
                if match['resultat'] == 'victoire':
                    victoires[idEquipe] += 1

        if not victoires:
            return None

        idDominant = max(victoires, key=victoires.get)
        return {
            'idEquipe': idDominant,
            'nom': self.noeuds.get(idDominant),
            'victoires': victoires[idDominant]
        }

    def est_complet(self):
        """
        Vérifie que toutes les équipes se sont affrontées.
        Un graphe complet a V×(V-1) arêtes orientées.
        O(V + E)
        """
        v = len(self.noeuds)
        total_aretes = sum(
            len(matchs) for matchs in self.adjacence.values()
        )
        aretes_attendues = v * (v - 1)
        return total_aretes >= aretes_attendues

    def to_dict(self):
        """Sérialise le graphe en dictionnaire JSON."""
        return {
            'noeuds': [
                {'id': k, 'nom': v}
                for k, v in self.noeuds.items()
            ],
            'aretes': [
                {
                    'source': idEquipe,
                    'cible': match['adversaire'],
                    'score': match['score'],
                    'resultat': match['resultat']
                }
                for idEquipe, matchs in self.adjacence.items()
                for match in matchs
            ],
            'estComplet': self.est_complet(),
            'nombreNoeuds': len(self.noeuds),
            'nombreAretes': sum(
                len(m) for m in self.adjacence.values()
            )
        }