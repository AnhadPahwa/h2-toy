from design import T, FLAT

B = 0.002   # £/MWh per MW of total demand
BASE = {t: 7500 if t < 6 else (32500 if 17 <= t <= 20 else 17500) for t in T}

def grid_price(P):
    return {t: B * (BASE[t] + P[t]) for t in T}

if __name__ == "__main__":
    p = grid_price({t: FLAT for t in T})
    print(p[0], p[6], p[17])   # expect 30.0 50.0 80.0
