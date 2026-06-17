from scipy.optimize import linprog

# Coefficients de la fonction objectif
c = [-3, -2]

# Coefficients des contraintes d'inégalité
A_ub = [
    [1, 1],
    [1, 0],
    [0, 1]
]

b_ub = [4, 2, 3]

# Bornes x >= 0, y >= 0
bounds = [(0, None), (0, None)]

# Résolution
result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

# Affichage du résultat
if result.success:
    print("Solution optimale trouvée :")
    print(f"x1 = {result.x[0]:.2f}, x2 = {result.x[1]:.2f}")
    print(f"Valeur optimale de la fonction objectif : {result.fun:.2f}")
else:
    print("Échec de la résolution.")