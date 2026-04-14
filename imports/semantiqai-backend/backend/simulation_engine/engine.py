from .simulator import simulate_scenario
from .decision_tree import build_decision_tree
from .risk import analyze_risk
from .opportunity import analyze_opportunity
from .strategy import strategic_analysis
from .hypothesis import generate_hypothesis

def run_simulation(context, decision):
    sim = simulate_scenario(context, decision)
    risk = analyze_risk(context + decision)
    opp = analyze_opportunity(context + decision)

    return {
        "simulation": sim,
        "risk": risk,
        "opportunity": opp
    }

def run_strategy(situation):
    return strategic_analysis(situation)

def run_tree(situation):
    return build_decision_tree(situation)

def run_hypothesis(topic):
    return generate_hypothesis(topic)
