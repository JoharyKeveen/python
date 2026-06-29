from pulp import LpMaximize, LpProblem, LpVariable, LpBinary

# 1. Modèle
model = LpProblem(name="selection_projets", sense=LpMaximize)

# 2. Variables binaires
A = LpVariable(name="A", cat=LpBinary)
B = LpVariable(name="B", cat=LpBinary)
C = LpVariable(name="C", cat=LpBinary)
D = LpVariable(name="D", cat=LpBinary)
E = LpVariable(name="E", cat=LpBinary)

# 3. Fonction objectif
model += 18*A + 24*B + 17*C + 28*D + 12*E, "Gain_total"

# 4. Contraintes
model += 6*A + 8*B + 5*C + 10*D + 4*E <= 20, "Budget"
model += 3*A + 5*B + 4*C + 6*D + 2*E <= 12, "Duree"
model += A + B <= 1, "Incompatibilite_A_B"

# 5. Résolution
model.solve()

# 6. Résultats
print("=== SOLUTION OPTIMALE ===")
print("Statut :", model.status)

projets = {"A": A, "B": B, "C": C, "D": D, "E": E}

for name, var in projets.items():
    print(name, "=", int(var.value()))

# 7. Calcul du budget utilisé
budget_utilise = (
    6*A.value() + 8*B.value() + 5*C.value() + 10*D.value() + 4*E.value()
)

# 8. Calcul de la durée réalisée
duree_utilisee = (
    3*A.value() + 5*B.value() + 4*C.value() + 6*D.value() + 2*E.value()
)

# 9. Affichage final
print("\n=== UTILISATION DES RESSOURCES ===")
print("Budget utilisé =", budget_utilise, "/ 20")
print("Durée utilisée =", duree_utilisee, "/ 12")

print("\nGain total =", model.objective.value())