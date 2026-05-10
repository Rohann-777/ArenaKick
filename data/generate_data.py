import json
import random
from datetime import datetime, timedelta

# Équipes malgaches typiques
EQUIPES = [
    {"nom": "Barea de Madagascar", "couleur": "Rouge et Vert", "nomCoach": "Ratsimba Jean"},
    {"nom": "COSFA FC", "couleur": "Bleu et Blanc", "nomCoach": "Randria Paul"},
    {"nom": "AS Adema", "couleur": "Rouge et Blanc", "nomCoach": "Rakoto Pierre"},
    {"nom": "FC Fosa Juniors", "couleur": "Jaune et Noir", "nomCoach": "Razafy Marc"},
    {"nom": "Elgeco Plus FC", "couleur": "Vert et Blanc", "nomCoach": "Rasolofo Henri"},
    {"nom": "AS Mama", "couleur": "Violet et Blanc", "nomCoach": "Andriantsoa Luc"},
    {"nom": "BonGoo FC", "couleur": "Orange et Noir", "nomCoach": "Ravelo Eric"},
    {"nom": "Ajesaia FC", "couleur": "Bleu et Jaune", "nomCoach": "Rabemanana Jules"},
]

POSTES = ["gardien", "defenseur", "milieu", "attaquant"]
PRENOMS = ["Andry", "Hery", "Tojo", "Fidy", "Niry",
           "Mamy", "Tiana", "Hasina", "Ny Aina", "Tahiry"]
NOMS = ["Rakoto", "Rabe", "Rado", "Ravo", "Ndriana",
        "Tsiry", "Mara", "Tafita", "Zara", "Vola"]

def generer_joueurs(equipes):
    joueurs = []
    idJoueur = 1
    for equipe in equipes:
        for maillot in range(1, 12):
            joueurs.append({
                "idJoueur": idJoueur,
                "nom": random.choice(NOMS),
                "prenom": random.choice(PRENOMS),
                "age": random.randint(18, 35),
                "numeroMaillot": maillot,
                "poste": random.choice(POSTES),
                "idEquipe": equipe["idEquipe"]
            })
            idJoueur += 1
    return joueurs

def generer_matchs_round_robin(equipes, idTournoi, date_debut):
    n = len(equipes)
    liste = equipes.copy()
    if n % 2 != 0:
        liste.append(None)
        n += 1

    matchs = []
    idMatch = 1
    date_courante = date_debut

    for journee in range(n - 1):
        for i in range(n // 2):
            equipeA = liste[i]
            equipeB = liste[n - 1 - i]
            if equipeA and equipeB:
                scoreA = random.randint(0, 5)
                scoreB = random.randint(0, 5)
                matchs.append({
                    "idMatch": idMatch,
                    "idEquipeA": equipeA["idEquipe"],
                    "idEquipeB": equipeB["idEquipe"],
                    "nomEquipeA": equipeA["nom"],
                    "nomEquipeB": equipeB["nom"],
                    "scoreEquipeA": scoreA,
                    "scoreEquipeB": scoreB,
                    "dateMatch": date_courante.strftime("%Y-%m-%d"),
                    "statut": "termine",
                    "idTournoi": idTournoi
                })
                idMatch += 1
                date_courante += timedelta(days=1)

        liste = [liste[0]] + [liste[-1]] + liste[1:-1]

    return matchs

def calculer_classement(equipes, matchs, idTournoi):
    stats = {}
    for equipe in equipes:
        stats[equipe["idEquipe"]] = {
            "idEquipe": equipe["idEquipe"],
            "nomEquipe": equipe["nom"],
            "points": 0,
            "victoires": 0,
            "nuls": 0,
            "defaites": 0,
            "butsPour": 0,
            "butsContre": 0,
            "differenceButs": 0,
            "idTournoi": idTournoi
        }

    for match in matchs:
        a = match["idEquipeA"]
        b = match["idEquipeB"]
        sA = match["scoreEquipeA"]
        sB = match["scoreEquipeB"]

        stats[a]["butsPour"] += sA
        stats[a]["butsContre"] += sB
        stats[b]["butsPour"] += sB
        stats[b]["butsContre"] += sA

        if sA > sB:
            stats[a]["victoires"] += 1
            stats[a]["points"] += 3
            stats[b]["defaites"] += 1
        elif sB > sA:
            stats[b]["victoires"] += 1
            stats[b]["points"] += 3
            stats[a]["defaites"] += 1
        else:
            stats[a]["nuls"] += 1
            stats[a]["points"] += 1
            stats[b]["nuls"] += 1
            stats[b]["points"] += 1

    for s in stats.values():
        s["differenceButs"] = s["butsPour"] - s["butsContre"]

    classement = sorted(
        stats.values(),
        key=lambda x: (
            -x["points"],
            -x["differenceButs"],
            -x["butsPour"]
        )
    )

    for rang, equipe in enumerate(classement, start=1):
        equipe["rang"] = rang

    return classement

if __name__ == "__main__":
    # Tournoi
    tournoi = {
        "idTournoi": 1,
        "nom": "Tournoi Malagasy 2035",
        "dateDebut": "2035-06-01",
        "dateFin": "2035-07-01",
        "format": "poules",
        "nombreEquipes": 8,
        "statut": "en_cours"
    }

    # Équipes
    equipes = []
    for i, eq in enumerate(EQUIPES, start=1):
        equipes.append({
            "idEquipe": i,
            "idTournoi": 1,
            **eq
        })

    # Joueurs
    joueurs = generer_joueurs(equipes)

    # Matchs Round-Robin
    date_debut = datetime(2035, 6, 1)
    matchs = generer_matchs_round_robin(equipes, 1, date_debut)

    # Classement
    classement = calculer_classement(equipes, matchs, 1)

    # Sauvegarde
    with open("tournois.json", "w", encoding="utf-8") as f:
        json.dump([tournoi], f, ensure_ascii=False, indent=2)

    with open("equipes.json", "w", encoding="utf-8") as f:
        json.dump(equipes, f, ensure_ascii=False, indent=2)

    with open("joueurs.json", "w", encoding="utf-8") as f:
        json.dump(joueurs, f, ensure_ascii=False, indent=2)

    with open("matchs.json", "w", encoding="utf-8") as f:
        json.dump(matchs, f, ensure_ascii=False, indent=2)

    with open("classements.json", "w", encoding="utf-8") as f:
        json.dump(classement, f, ensure_ascii=False, indent=2)

    print(f"Données générées avec succès !")
    print(f"  {len(equipes)} équipes")
    print(f"  {len(joueurs)} joueurs")
    print(f"  {len(matchs)} matchs")
    print(f"  {len(classement)} entrées de classement")