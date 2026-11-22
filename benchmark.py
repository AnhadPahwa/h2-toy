import os
import numpy as np
import matplotlib.pyplot as plt
from design import T, FLAT, solve_plant
from grid import grid_price
from equilibrium import solve_eq

def to_vec(d):
    return np.array([d[t] for t in T])

P_star = to_vec(solve_eq()[0])

def run(step_rule, n_iter=100):
    P_hat = {t: FLAT for t in T}
    dist = []
    for j in range(n_iter):
        P, _, _ = solve_plant(grid_price(P_hat))
        delta = step_rule(j)
        P_hat = {t: P_hat[t] + delta * (P[t] - P_hat[t]) for t in T}
        dist.append(np.linalg.norm(to_vec(P_hat) - P_star) / np.linalg.norm(P_star))
    return dist

rules = {
    "δ = 1.0":     lambda j: 1.0,
    "δ = 0.1":     lambda j: 0.1,
    "δ = 0.8^j":   lambda j: 0.8 ** j,
    "δ = 0.9^j":   lambda j: 0.9 ** j,
    "δ = 0.95^j":  lambda j: 0.95 ** j,
    "δ = 1/(j+1)": lambda j: 1 / (j + 1),
}

os.makedirs("figures", exist_ok=True)
plt.figure()
for name, rule in rules.items():
    d = run(rule)
    print(f"{name:12s} " + " ".join(f"{d[k]:.4f}" for k in [9, 24, 49, 99]))
    plt.semilogy(range(1, len(d) + 1), d, label=name)
plt.xlabel("iteration")
plt.ylabel("‖P_hat − P*‖ / ‖P*‖")
plt.legend()
plt.savefig("figures/distance_to_equilibrium.png", dpi=150)