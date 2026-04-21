class KMPRecherche:
    """
    Algorithme Knuth-Morris-Pratt (KMP).
    Famille : Chaînes / Recherche
    Complexité : O(n + m) temps, O(m) mémoire
    où n = longueur du texte, m = longueur du motif
    """

    @staticmethod
    def construire_table_echec(motif):
        """
        Construit la table d'échec (prefix function).
        O(m) où m = longueur du motif.
        """
        m = len(motif)
        echec = [0] * m
        j = 0

        for i in range(1, m):
            while j > 0 and motif[i] != motif[j]:
                j = echec[j - 1]
            if motif[i] == motif[j]:
                j += 1
            echec[i] = j

        return echec

    @staticmethod
    def rechercher(texte, motif):
        """
        Recherche toutes les occurrences du motif dans le texte.
        O(n + m) où n = longueur texte, m = longueur motif.

        Returns:
            Liste des positions où le motif est trouvé
        """
        if not motif or not texte:
            return []

        # Insensible à la casse
        texte_lower = texte.lower()
        motif_lower = motif.lower()

        n = len(texte_lower)
        m = len(motif_lower)
        positions = []

        echec = KMPRecherche.construire_table_echec(motif_lower)
        j = 0

        for i in range(n):
            while j > 0 and texte_lower[i] != motif_lower[j]:
                j = echec[j - 1]
            if texte_lower[i] == motif_lower[j]:
                j += 1
            if j == m:
                positions.append(i - m + 1)
                j = echec[j - 1]

        return positions

    @staticmethod
    def rechercher_equipes(equipes, motif):
        """
        Recherche des équipes dont le nom contient le motif.
        Utilise KMP pour chaque nom d'équipe.
        """
        resultats = []
        for equipe in equipes:
            positions = KMPRecherche.rechercher(
                equipe.get('nom', ''), motif
            )
            if positions:
                resultats.append({
                    'equipe': equipe,
                    'positions': positions
                })
        return resultats

    @staticmethod
    def rechercher_naif(texte, motif):
        """
        Solution naïve pour comparaison — O(n × m)
        Compare caractère par caractère à chaque position.
        """
        if not motif or not texte:
            return []

        texte_lower = texte.lower()
        motif_lower = motif.lower()
        n = len(texte_lower)
        m = len(motif_lower)
        positions = []

        for i in range(n - m + 1):
            match = True
            for j in range(m):
                if texte_lower[i + j] != motif_lower[j]:
                    match = False
                    break
            if match:
                positions.append(i)

        return positions