def rendu(liste_monnaie, rendre):
    liste_monnaie = sorted(liste_monnaie, reverse=True)
    meilleure_solution = []

    def back(reste, combinaison):
        nonlocal meilleure_solution
        if reste == 0:
            if (not meilleure_solution or len(combinaison) < len(meilleure_solution)):
                meilleure_solution = combinaison[:]
            return

        if reste < 0:
            return

        if (meilleure_solution and len(combinaison) >= len(meilleure_solution)):
            return

        for monnaie_courant in liste_monnaie:
            combinaison.append(monnaie_courant)
            back(reste - monnaie_courant, combinaison) 
            combinaison.pop()

    back(rendre, [])
    return meilleure_solution


liste_monnaie = [1,3,4]
print(rendu(liste_monnaie, 6))