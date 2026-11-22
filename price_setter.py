from design import T, FLAT, COST_CAP, COST_STOR, solve_plant
from grid import grid_price

# 1. prices if the plant ran flat
p0 = grid_price({t: FLAT for t in T})

# 2. plant designs itself on p0
P, cap, smax = solve_plant(p0)
fixed = COST_CAP * cap + COST_STOR * smax

predicted = fixed + sum(p0[t] *P[t] for t in T) # fixed + electricity at p0
# 3. grid responds to the plant's real demand
p1 = grid_price(P)
realised = fixed + sum(p1[t] * P[t] for t in T) # same design and schedule, electricity at p1

flat_cost = COST_CAP * FLAT + sum(p0[t] * FLAT for t in T)

P2, cap2, smax2 = solve_plant(p1)

print("predicted:", round(predicted))
print("realised:", round(realised))
print("flat:", round(flat_cost))
print("p1:", [round(p1[t], 1) for t in T])
print("re-designed:", round(cap2), round(smax2))