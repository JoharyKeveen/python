import numpy as np
from scipy.optimize import minimize

# minimiser
def f(x):
    return x[0]**2 + x[1]**2 - 3*x[0] - 4*x[1] + x[0]*x[1]

x0 = np.array([0.0, 0.0])

result = minimize(f, x0, method='BFGS')

print("Solution optimale :", np.round(result.x, 2))
print("Valeur minimale :", round(result.fun, 2))