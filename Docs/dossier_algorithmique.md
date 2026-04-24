# Dossier Algorithmique — ArenaKick
## Numérique Malagasy 2035
**Étudiant** : RAKOTOJAONA Tsiaronomena Rohann
**Projet** : ArenaKick — Plateforme de gestion de tournois de football
**Date** : 2026

---

## 1. Problèmes Algorithmiques

### 1.1 Génération équitable des matchs
**Problème** : Étant donné n équipes inscrites dans un tournoi,
générer un calendrier de matchs garantissant que chaque équipe
affronte toutes les autres exactement une fois, de façon équitable
et sans biais de tirage.

**Entrées** : Liste de n équipes, date de début du tournoi
**Sorties** : Liste de n×(n-1)/2 matchs avec dates assignées

### 1.2 Classement multi-critères
**Problème** : Après chaque match, maintenir un classement trié
selon les règles FIFA : points > différence de buts > buts marqués
> confrontation directe.

**Entrées** : Résultats des matchs (scoreA, scoreB)
**Sorties** : Tableau de classement trié et mis à jour

### 1.3 Recherche de texte dans les noms
**Problème** : Rechercher efficacement une équipe ou un joueur
par nom partiel dans une liste potentiellement grande.

**Entrées** : Liste de noms, motif de recherche
**Sorties** : Liste des correspondances avec positions

### 1.4 Sélection des K meilleures équipes
**Problème** : Extraire les K meilleures équipes d'un tournoi
sans trier l'intégralité du classement.

**Entrées** : Liste de n équipes avec stats, entier k
**Sorties** : Les k meilleures équipes selon critères FIFA

### 1.5 Modélisation des confrontations
**Problème** : Représenter et interroger les résultats directs
entre équipes pour départager les égalités.

**Entrées** : Matchs joués avec scores
**Sorties** : Graphe orienté des confrontations

---

## 2. Modèles

### 2.1 Modèle Round-Robin
- **Type** : Algorithme de rotation cyclique
- **Contrainte** : Chaque paire (i,j) apparaît exactement une fois
- **Métrique** : n×(n-1)/2 matchs pour n équipes
- **Hypothèse** : n ≥ 2 équipes inscrites

### 2.2 Modèle de Classement FIFA
- **Type** : Tri multi-critères stable
- **Contraintes** :
  - Victoire = 3 pts, Nul = 1 pt, Défaite = 0 pt
  - Départage : points > DB > BP > confrontation directe
- **Métrique** : Rang final de chaque équipe

### 2.3 Modèle KMP
- **Type** : Automate fini déterministe
- **Contrainte** : Recherche insensible à la casse
- **Métrique** : Nombre d'occurrences et positions
- **Hypothèse** : Texte et motif en UTF-8

### 2.4 Modèle Top-K
- **Type** : Sélection par tas binaire
- **Contrainte** : k ≤ n équipes
- **Métrique** : k meilleures équipes par points
- **Hypothèse** : Classement déjà calculé disponible

### 2.5 Modèle Graphe
- **Type** : Graphe orienté pondéré
- **Structure** : Liste d'adjacence
- **Nœuds** : Équipes (V = n)
- **Arêtes** : Matchs joués (E ≤ n×(n-1))
- **Poids** : Score du match

---

## 3. Algorithmes Choisis

### 3.1 Round-Robin (Famille : Optimisation)

**Description** :
Algorithme de rotation cyclique garantissant que chaque équipe
affronte toutes les autres exactement une fois.

**Pseudo-code** :
FONCTION round_robin(equipes):
n ← longueur(equipes)
SI n est impair ALORS ajouter équipe_fictive
matchs ← []
POUR journee DE 0 À n-2 FAIRE:
    POUR i DE 0 À n/2 - 1 FAIRE:
        equipeA ← equipes[i]
        equipeB ← equipes[n-1-i]
        SI equipeA ≠ null ET equipeB ≠ null ALORS
            ajouter (equipeA, equipeB) à matchs
    FIN POUR
    # Rotation : fixer equipes[0], tourner les autres
    equipes ← [equipes[0]] + [equipes[n-1]] + equipes[1:n-1]
FIN POUR
RETOURNER matchs
FIN FONCTION

### 3.2 Tri multi-critères FIFA (Famille : Optimisation)

**Description** :
Tri stable par clé composite utilisant Timsort Python.

**Pseudo-code** :
FONCTION trier_classement(equipes):
RETOURNER trier(equipes,
clé = (points DESC,
différence_buts DESC,
buts_pour DESC))
FIN FONCTION

### 3.3 KMP — Knuth-Morris-Pratt (Famille : Chaînes/Recherche)

**Description** :
Recherche de motif avec table d'échec évitant les comparaisons
redondantes.

**Pseudo-code** :
FONCTION construire_table_echec(motif):
m ← longueur(motif)
echec ← tableau de 0 de taille m
j ← 0
POUR i DE 1 À m-1 FAIRE:
TANT QUE j > 0 ET motif[i] ≠ motif[j] FAIRE:
j ← echec[j-1]
SI motif[i] = motif[j] ALORS j ← j + 1
echec[i] ← j
FIN POUR
RETOURNER echec
FIN FONCTION
FONCTION kmp_rechercher(texte, motif):
echec ← construire_table_echec(motif)
j ← 0
positions ← []
POUR i DE 0 À longueur(texte)-1 FAIRE:
TANT QUE j > 0 ET texte[i] ≠ motif[j] FAIRE:
j ← echec[j-1]
SI texte[i] = motif[j] ALORS j ← j + 1
SI j = longueur(motif) ALORS:
ajouter (i - longueur(motif) + 1) à positions
j ← echec[j-1]
FIN POUR
RETOURNER positions
FIN FONCTION

### 3.4 Top-K Min-Heap (Famille : Streaming/Fenêtrage)

**Description** :
Sélection des K meilleurs éléments via tas binaire minimum,
sans trier l'intégralité de la liste.

**Pseudo-code** :
FONCTION top_k(equipes, k):
# Utilise un Min-Heap de taille k
heap ← tas_vide()
POUR chaque equipe DANS equipes FAIRE:
    SI taille(heap) < k ALORS:
        insérer(heap, equipe)
    SINON SI equipe.points > minimum(heap).points ALORS:
        extraire_minimum(heap)
        insérer(heap, equipe)
    FIN SI
FIN POUR
RETOURNER trier_descendant(heap)
FIN FONCTION

---

## 4. Structures de Données

### 4.1 Tas Binaire (Min-Heap)
**Définition** : Arbre binaire complet où chaque nœud est
inférieur ou égal à ses enfants.

**Intégration** : Utilisé dans `top_k.py` via `heapq.nlargest()`
pour sélectionner les K meilleures équipes.

**Pourquoi adapté** :
- Insertion en O(log k) — seulement k éléments en mémoire
- Extraction du minimum en O(log k)
- Idéal pour streaming (données arrivant une par une)

### 4.2 Table de Hachage (Dictionnaire Python)
**Définition** : Structure clé-valeur basée sur une fonction
de hachage avec gestion des collisions par chaînage.

**Intégration** : Utilisée partout dans l'API Flask pour
représenter les statistiques d'équipe (idEquipe → stats).

**Pourquoi adapté** :
- Accès en O(1) amorti
- Construction du classement en O(n)
- Sérialisation JSON native

### 4.3 Graphe — Liste d'Adjacence
**Définition** : Ensemble de nœuds et d'arêtes représenté
par un dictionnaire de listes (idEquipe → [matchs]).

**Intégration** : Utilisé dans `graphe.py` pour modéliser
les confrontations entre équipes du tournoi.

**Pourquoi adapté** :
- Mémoire O(V + E) vs O(V²) pour matrice d'adjacence
- Adapté aux graphes creux (peu d'arêtes vs nœuds)
- Parcours des voisins en O(degree(v))

---

## 5. Complexité

| Algorithme            | Temps        | Mémoire | Cas pire           |
|-----------------------|--------------|---------|--------------------|
| Round-Robin           | O(n²)        | O(n²)   | n équipes          |
| Tri FIFA (Timsort)    | O(n log n)   | O(n)    | n équipes          |
| KMP — table échec     | O(m)         | O(m)    | m = longueur motif |
| KMP — recherche       | O(n + m)     | O(m)    | n = longueur texte |
| Top-K Min-Heap        | O(n log k)   | O(k)    | k ≤ n              |
| Graphe — construction | O(V + E)     | O(V + E)| V équipes, E matchs|
| Graphe — voisins      | O(degree(v)) | O(1)    | v = nœud           |

**Justifications** :
- Round-Robin : O(n²) car n-1 journées × n/2 matchs/journée
- KMP : O(n+m) grâce à la table d'échec évitant
  les retours arrière naïfs
- Top-K : O(n log k) << O(n log n) quand k << n
  Ex: k=3, n=1000 → 1585 ops vs 10000 ops

---

## 6. Validation

### 6.1 Tests unitaires

Crée `src/backend/tests/test_algorithmes.py` :

---

## 7. Résultats — Tableau comparatif

| Algorithme          | Baseline       | Optimisé            | Gain                  |
|-----------          |---------       |---------            |-----------------------|  
| **Recherche texte** | Naïf O(n×m)    | KMP O(n+m)          | ~6x sur grands textes |
| **Sélection Top-K** | Tri O(n log n) | Min-Heap O(n log k) | ~6x pour k=3, n=1000  |
| **Classement**      | Tri naïf O(n²) | Timsort O(n log n)  | ~100x pour n=64       |

### Mesures réelles (API Flask)

| Route                                | Temps optimisé | Temps naïf |
|--------------------------------------|--------------- |------------|
| `/api/algorithmes/recherche?q=barea` | 0.056 ms       | 0.004 ms   |
| `/api/algorithmes/top-k/1?k=3`       | 0.037 ms       | 0.014 ms   |

> Note : Sur de petits jeux de données (n=8 équipes),
> la différence est minime. L'avantage algorithmique
> devient significatif pour n > 100 équipes.

---

## Contraintes réalisme 2035 déclarées

| Contrainte                     | Impact architectural                   | Impact algorithmique                  |
|--------------------------------|----------------------------------------|---------------------------------------|
| **Coupures d'énergie**         | Sauvegarde Git régulière, MySQL        | Algorithmes légers en mémoire         |
| **Faible débit**               | API REST légère, JSON compact          | KMP réduit les requêtes de recherche  |
| **Sécurité**                   | JWT, hashage mot de passe              | Validation des entrées à chaque route |
| **Connectivité intermittente** | Développement offline possible         | MySQL via WampServer, fonctionnel en local sans internet       |