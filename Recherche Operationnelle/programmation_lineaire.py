from scipy.optimize import linprog

# Coefficients de la fonction objectif
c = [3, 2]

# Coefficients des contraintes d'inégalité
A_ub = [
    [1, 2],
    [4, 2],
    [-1, 1]
]

b_ub = [6, 12, 1]

# Résolution du problème
result = linprog(c, A_ub=A_ub, b_ub=b_ub, method='highs')

# Affichage du résultat
if result.success:
    print("Solution optimale trouvée :")
    print(f"x1 = {result.x[0]:.2f}, x2 = {result.x[1]:.2f}")
    print(f"Valeur optimale de la fonction objectif : {result.fun:.2f}")
else:
    print("Échec de la résolution.")