import pyomo.environ as pyo
from design import T, COST_CAP, COST_STOR, build_plant, solve_plant
from grid import B, BASE, grid_price

def solve_eq():
    m = pyo.ConcreteModel()
    build_plant(m)

    area = sum(B*BASE[t] * m.P[t] + (B/2) * m.P[t]**2 for t in m.T)
    m.obj = pyo.Objective(expr=COST_CAP * m.CAP + COST_STOR * m.SMAX + area, sense=pyo.minimize)

    result = pyo.SolverFactory("highs").solve(m)
    assert str(result.solver.termination_condition) == "optimal", result.solver.termination_condition

    P_star = {t: pyo.value(m.P[t]) for t in T}
    return P_star, pyo.value(m.CAP), pyo.value(m.SMAX)

def cost_at(P, cap, smax, prices):
    return COST_CAP * cap + COST_STOR * smax + sum(prices[t] * P[t] for t in T)

if __name__ == "__main__":
    P_star, cap_star, smax_star = solve_eq()
    p_star = grid_price(P_star)

    print("P*:", [round(P_star[t]) for t in T])
    print("CAP*:", round(cap_star), "SMAX*:", round(smax_star))
    print("p*:", [round(p_star[t], 2) for t in T])

    # verification: is P* really an equilibrium
    P_lp, cap_lp, smax_lp = solve_plant(p_star)

    print("cost of P* at p*:     ", round(cost_at(P_star, cap_star, smax_star, p_star)))
    print("plant's LP best at p*:", round(cost_at(P_lp, cap_lp, smax_lp, p_star)))
    print("plant's LP schedule:  ", [round(P_lp[t]) for t in T])

