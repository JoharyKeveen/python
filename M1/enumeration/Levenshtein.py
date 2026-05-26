def generer_mots(M, k):
    alphabet = ['a','b','d','e','f','g','h','i','j','k','l','m','n','o','p','r','s','t','v','y','z']
    vus = set()
    resultats = []

    def rec(mot, operations_restantes):
        if operations_restantes < 0:
            return

        if mot not in vus:
            vus.add(mot)
            resultats.append(mot)

        # Suppression
        for i in range(len(mot)):
            nouveau = mot[:i] + mot[i+1:]
            rec(nouveau, operations_restantes - 1)

        # Insertion
        for i in range(len(mot) + 1):
            for c in alphabet:
                nouveau = mot[:i] + c + mot[i:]
                rec(nouveau, operations_restantes - 1)

        # Substitution
        for i in range(len(mot)):
            for c in alphabet:
                if mot[i] != c:
                    nouveau = mot[:i] + c + mot[i+1:]
                    rec(nouveau, operations_restantes - 1)

    rec(M, k)
    return resultats

mots = generer_mots("vato", 2)
print(len(mots))
print(mots)