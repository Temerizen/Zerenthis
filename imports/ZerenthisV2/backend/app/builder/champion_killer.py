import random, copy

def attack_champion(params):
    new = copy.deepcopy(params)

    for k in ["risk_per_trade","take_profit","stop_loss","position_scale"]:
        if k in new:
            strength = random.uniform(0.2, 0.6)  # BIG mutations
            delta = new[k] * strength * (random.random()*2-1)
            new[k] = max(0.001, new[k] + delta)

    return new

def generate_next(params):
    import random

    roll = random.random()

    if roll < 0.4:
        return attack_champion(params)   # AGGRESSIVE
    elif roll < 0.7:
        return adaptive_mutation(params) # NORMAL
    else:
        return adaptive_mutation(params) # SAFE VARIANT
