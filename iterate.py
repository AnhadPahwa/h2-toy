import numpy as np
import matplotlib.pyplot as plt
from design import T, FLAT, solve_plant
from grid import grid_price
import os

def to_vec(d):
    return np.array([d[t] for t in T]) # for norms

def run(step_rule, n_iter=60):
    P_hat = {t: FLAT for t in T}
    P_old, c_old = None, None
    eps_d, eps_p = [], []

    for j in range(n_iter):
        prices = grid_price(P_hat)
        P, cap, smax = solve_plant(prices)

        P_vec, c_vec = to_vec(P), to_vec(prices)
        if P_old is not None:
            eps_d.append(np.linalg.norm(P_vec - P_old) / np.linalg.norm(P_old))
            eps_p.append(np.linalg.norm(c_vec - c_old) / np.linalg.norm(c_old))
        P_old, c_old = P_vec, c_vec

        delta = step_rule(j)
        P_hat = {t: P_hat[t] + delta * (P[t] - P_hat[t]) for t in T}

    return eps_d, eps_p, cap, smax, P_hat, P

rules = {
    "δ = 1.0":  lambda j: 1.0,
    "δ = 0.2":  lambda j: 0.2,
    "δ = 0.1":  lambda j: 0.1,
    "δ = 0.8^j": lambda j: 0.8 ** j,
    "δ = 0.9^j": lambda j: 0.9 ** j,
}

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
for name, rule in rules.items():
    eps_d, eps_p, cap, smax, P_hat, P = run(rule)
    print(f"{name:10s} final CAP {cap:7.0f}  SMAX {smax:5.0f}")
    ax1.semilogy(eps_d, label=name)
    ax2.semilogy(eps_p, label=name)
    gap = np.linalg.norm(to_vec(P) - to_vec(P_hat)) / np.linalg.norm(to_vec(P_hat))
    print(f"{name:10s} belief-vs-plant gap {gap:.3f}")
ax1.set_ylabel("demand residual")
ax2.set_ylabel("price residual")
ax2.set_xlabel("iteration")
ax1.legend()
os.makedirs("figures", exist_ok=True)
plt.savefig("figures/residuals.png", dpi=150)