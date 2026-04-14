from backend.app.engines.traffic_factory import run as traffic_run
from backend.app.engines.campaign_packager import run as campaign_run
from backend.app.engines.signal_simulator import run as simulate_run
from backend.app.engines.reality_bridge import run as ingest_run

def run(payload=None):
    payload = payload or {}

    traffic = traffic_run()
    campaign = campaign_run()
    simulated = simulate_run(payload)
    signal = simulated.get("signal", {})
    ingestion = ingest_run(signal)

    return {
        "status": "reality_auto_loop_complete",
        "topic": traffic.get("topic"),
        "traffic": traffic,
        "campaign": campaign,
        "simulated_signal": simulated,
        "ingestion": ingestion,
        "decision": ingestion.get("decision_gate", {}),
        "safe_mode": True
    }
