import heapq

class TopKAlgorithme:
    """
    Algorithme Top-K utilisant un tas binaire (Min-Heap).
    Famille : Streaming / Fenêtrage
    Complexité : O(n log k) temps, O(k) mémoire
    """

    @staticmethod
    def top_k_equipes(equipes, k, critere='points'):
        """
        Retourne les K meilleures équipes selon un critère.

        Args:
            equipes: liste de dicts avec stats
            k: nombre d'équipes à retourner
            critere: 'points', 'butsPour', 'victoires'

        Returns:
            Liste des K meilleures équipes triées
        """
        if k <= 0 or not equipes:
            return []

        k = min(k, len(equipes))

        # Tas binaire Min-Heap — O(n log k)
        top_k = heapq.nlargest(
            k,
            equipes,
            key=lambda x: (
                x.get('points', 0),
                x.get('differenceButs', 0),
                x.get('butsPour', 0)
            )
        )

        return top_k

    @staticmethod
    def top_k_buteurs(joueurs_stats, k):
        """
        Retourne les K meilleurs buteurs du tournoi.

        Args:
            joueurs_stats: liste de dicts avec buts
            k: nombre de buteurs à retourner

        Returns:
            Liste des K meilleurs buteurs
        """
        if k <= 0 or not joueurs_stats:
            return []

        k = min(k, len(joueurs_stats))

        return heapq.nlargest(
            k,
            joueurs_stats,
            key=lambda x: x.get('buts', 0)
        )

    @staticmethod
    def top_k_naif(equipes, k, critere='points'):
        """
        Solution naïve pour comparaison — O(n log n)
        Trie toutes les équipes puis prend les K premières.
        """
        if k <= 0 or not equipes:
            return []

        equipes_triees = sorted(
            equipes,
            key=lambda x: (
                -x.get('points', 0),
                -x.get('differenceButs', 0),
                -x.get('butsPour', 0)
            )
        )

        return equipes_triees[:k]