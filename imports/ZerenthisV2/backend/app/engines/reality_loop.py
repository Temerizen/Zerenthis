from backend.app.engines.traffic_factory import run as traffic_run
from backend.app.engines.campaign_packager import run as campaign_run
from backend.app.engines.signal_simulator import run as simulate_run
from backend.app.engines.reality_bridge import run as ingest_run
from backend.app.engines.real_traffic_bridge import run as real_signal_run

def run():
    # STEP 1: generate system output
    traffic = traffic_run()
    campaign = campaign_run()

    # STEP 2: ALWAYS pull fresh signal
    real = real_signal_run()
    signal = real.get("signal", {})
    signal_source = "real_fresh"

    # fallback (safety)
    if not signal:
        simulated = simulate_run()
        signal = simulated.get("signal", {})
        signal_source = "simulated_fallback"

    # STEP 3: ingest
    ingestion = ingest_run(signal)

    return {
        "status": "adaptive_loop_complete",
        "topic": traffic.get("topic"),
        "signal_source": signal_source,
        "signal": signal,
        "traffic": traffic,
        "campaign": campaign,
        "ingestion": ingestion,
        "decision": ingestion.get("decision_gate", {}),
        "safe_mode": True
    }
