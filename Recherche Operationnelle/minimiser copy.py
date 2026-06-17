import numpy as np
from scipy.optimize import minimize

def objective( x ):
    return x[0]**2 + x[1]**2

# Dé finition de la contrainte x0 + x1 = 1
constraint = {'type': 'eq', 'fun': lambda x: x[0] + x[1] - 1}

# Point initial
x0 = [0.5 , 0.5]

# Appel de minimize avec contrainte
result = minimize(objective ,x0,constraints =[constraint] , method ="SLSQP")

print (" Solution  optimale : ", result.x )
print (" Valeur de la fonction en minimum : ", result.fun )