import numpy as np
from scipy.optimize import minimize

# Fonction à minimiser
def f(x):
    return (x - 1)**2

# Point initial
x0 = np.array([0])

# Appel de minimize
result = minimize(f, x0, method="BFGS")

# Affichage des résultats
print("Solution optimale :", round(result.x[0], 6))
print("Valeur minimale :", round(result.fun, 6))