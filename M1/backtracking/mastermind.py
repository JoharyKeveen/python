# Paramètres
COULEURS = [0, 1, 2, 3]
TAILLE = 3

def generer_combinaisons():
    resultats = []

    def backtrack(combinaison):
        if len(combinaison) == TAILLE:
            resultats.append(combinaison[:])
            return
        for c in COULEURS:
            combinaison.append(c)
            backtrack(combinaison)
            combinaison.pop()

    backtrack([])
    return resultats

def calculer_indice(secret, proposition):
    bien_places = 0
    mal_places = 0

    # bien placés
    for i in range(TAILLE):
        if secret[i] == proposition[i]:
            bien_places += 1

    secret_copy = secret[:]
    prop_copy = proposition[:]

    # esorina reo bien placés
    for i in range(TAILLE):
        if secret[i] == proposition[i]:
            secret_copy[i] = -1
            prop_copy[i] = -2

    # mal placés
    for i in range(TAILLE):
        if prop_copy[i] in secret_copy:
            mal_places += 1
            secret_copy[secret_copy.index(prop_copy[i])] = -1

    return (bien_places, mal_places)

def filtrer(possibles, proposition, indice):
    nouveaux = []
    for comb in possibles:
        resultat = calculer_indice(comb, proposition)
        if resultat == indice:
            nouveaux.append(comb)
    return nouveaux

def mastermind():
    possibles = generer_combinaisons()
    tentatives = 0
    print("Pense à une combinaison de " + str(TAILLE) + " avec les couleurs : " + " ".join(str(c) for c in COULEURS) + "\n")
    while True:
        tentatives += 1
        proposition = possibles[0]

        print("Tentative", tentatives, ":", proposition)

        bien = int(input("Bien placés : "))
        mal = int(input("Mal placés : "))

        possibles = filtrer(possibles, proposition, (bien, mal))
        if bien == TAILLE:
            print("Trouvé en ", tentatives, " tentatives !")
            break
        if len(possibles) == 0:
            print("Erreur : indices incohérents")
            break

mastermind()