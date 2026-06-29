import numpy as np
from scipy.optimize import minimize

# minimiser
def objective( x ):
    return (x[0]-2)**2 + (x[1]+1)**2

constraint = {'type': 'eq', 'fun': lambda x: x[0] + 2*x[1] - 3}

x0 = np.array([0.0, 0.0])

result = minimize(objective ,x0,constraints =[constraint] , method ="SLSQP")

print("Solution optimale :", np.round(result.x, 2))
print("Valeur minimale :", round(result.fun, 2))