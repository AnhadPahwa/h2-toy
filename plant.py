import pyomo.environ as pyo, highspy
import numpy as np
import matplotlib.pyplot as plt

# Constants:
DEMAND = 150 #t/h of hydrogen to steel plant every hour
EFF = 50 # MW per t/h
CAP = 1.5 * DEMAND * EFF # MW of electrolyser capacity (δ = 50%)
SMAX = 300 # t of storage

T = range(24) # hours in a day
price = {t: 30 if t < 6 else (80 if 17 <= t <= 20 else 50) for t in T} # 30 at night, 80 from 17:00-20:00, 50 otherwise

# model
m = pyo.ConcreteModel()
m.T = pyo.Set(initialize=T)

m.P = pyo.Var(m.T, bounds=(0, CAP))
m.H = pyo.Var(m.T, within=pyo.NonNegativeReals)
m.I = pyo.Var(m.T, bounds=(0,SMAX))

# Constraint pattern: a rule function called once every hour (t)
def production_rule(m, t):
    return m.H[t] == m.P[t] / EFF
m.production = pyo.Constraint(m.T, rule = production_rule)

def balance_rule(m, t):
    prev = 0 if t == 0 else m.I[t - 1]
    return m.I[t] == prev + m.H[t] - DEMAND
m.balance = pyo.Constraint(m.T, rule=balance_rule)

m.end = pyo.Constraint(expr=m.I[23] == 0)

def ramp_up_rule(m, t):
    if t ==0:
        return pyo.Constraint.Skip
    return m.P[t] - m.P[t-1] <= 0.2 * CAP
m.ramp_up = pyo.Constraint(m.T, rule=ramp_up_rule)

def ramp_down_rule(m, t):
    if t ==0:
        return pyo.Constraint.Skip
    return m.P[t-1] - m.P[t] <= 0.2 * CAP
m.ramp_down = pyo.Constraint(m.T, rule=ramp_down_rule)

m.obj = pyo.Objective(expr=sum(price[t] * m.P[t] for t in m.T), sense=pyo.minimize)

# Solve
result = pyo.SolverFactory("appsi_highs").solve(m)
print(result.solver.termination_condition)
print("optimised cost:", pyo.value(m.obj))
print("flat-run cost: ", sum(price[t] * DEMAND * EFF for t in T))
print("P:", [round(pyo.value(m.P[t])) for t in T])
print("I:", [round(pyo.value(m.I[t])) for t in T])