from pulp import LpMaximize, LpProblem, LpVariable, LpInteger

# 1. Définir le modèle
model = LpProblem(name="production_A_B", sense=LpMaximize)

# 2. Variables de décision (entières, positives)
A = LpVariable(name="Produit_A", lowBound=0, cat=LpInteger)
B = LpVariable(name="Produit_B", lowBound=0, cat=LpInteger)

# 3. Fonction objectif (profit)
# 50 000 Ar pour A et 30 000 Ar pour B
model += 50000 * A + 30000 * B, "Profit_total"

# 4. Contraintes

# Matière première : 5A + 2B ≤ 82
model += 5 * A + 2 * B <= 82, "Contrainte_matiere"

# Temps machine : 3A + 2B ≤ 61
model += 3 * A + 2 * B <= 61, "Contrainte_temps"

# 5. Résolution
model.solve()

# 6. Résultats
print("Statut :", model.status)
print("Solution optimale :")
print("Produit A =", A.value())
print("Produit B =", B.value())
print("Profit total =", model.objective.value(), "Ar")