import numpy as np
from scipy.optimize import minimize

def objective( x ):
    return 3*x[0]**2 + 2*x[1]**2 + x[0]*x[1]

constraint = {'type': 'eq', 'fun': lambda x: x[0] + x[1] - 100}

x0 = np.array([50, 50])

result = minimize(objective ,x0,constraints =[constraint] , method ="SLSQP")

print("Solution optimale :", np.round(result.x, 2))
print("Valeur minimale :", round(result.fun, 2))