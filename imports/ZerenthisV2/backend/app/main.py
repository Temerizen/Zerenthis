from backend.app.routes import max_evolution
from backend.app.routes import evolution
from backend.app.routes import autonomous_builder
from backend.app.routes import builder_intelligence
from backend.app.routes import builder
from fastapi import FastAPI
from backend.app.routes import autopilot
from backend.app.routes import intelligence
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.phase_verify import router as phase_verify_router
from backend.app.routes.phase_lock import router as phase_lock_router
from backend.app.routes.multi_target_manager import router as multi_target_manager_router
from backend.app.routes.queue_manager import router as queue_manager_router
from backend.app.routes.posting_result import router as posting_result_router
from backend.app.routes.posting_execute import router as posting_execute_router
from backend.app.routes.posting_bridge import router as posting_bridge_router
from backend.app.routes.autopilot_engine import router as autopilot_engine_router
from backend.app.routes.scaling_engine import router as scaling_engine_router
from backend.app.routes.real_traffic_bridge import router as real_traffic_bridge_router
from backend.app.routes.traffic_bridge import router as traffic_bridge_router
from backend.app.routes.champion_engine import router as champion_engine_router
from backend.app.routes.evolution_engine import router as evolution_engine_router
from backend.app.routes.reality_exporter import router as reality_exporter_router
from backend.app.routes.reality_loop_auto import router as reality_loop_auto_router
from backend.app.routes.signal_simulator import router as signal_simulator_router
from backend.app.routes.reality_loop import router as reality_loop_router
from backend.app.routes.reality_bridge import router as reality_bridge_router
from backend.app.routes.campaign_packager import router as campaign_packager_router
from backend.app.routes.traffic_factory import router as traffic_factory_router
from backend.app.routes.intelligence_priority import router as intelligence_priority_router
from backend.app.routes.product import router as product_router
from backend.app.routes.full_cycle import router as full_cycle_router
from backend.app.routes.revenue import router as revenue_router

app = FastAPI()
app.include_router(autopilot.router)
app.include_router(intelligence.router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(phase_verify_router)
app.include_router(phase_lock_router)
app.include_router(multi_target_manager_router)
app.include_router(queue_manager_router)
app.include_router(posting_result_router)
app.include_router(posting_execute_router)
app.include_router(posting_bridge_router)
app.include_router(autopilot_engine_router)
app.include_router(scaling_engine_router)
app.include_router(real_traffic_bridge_router)
app.include_router(traffic_bridge_router)
app.include_router(champion_engine_router)
app.include_router(evolution_engine_router)
app.include_router(reality_exporter_router)
app.include_router(reality_loop_auto_router)
app.include_router(signal_simulator_router)
app.include_router(reality_loop_router)
app.include_router(reality_bridge_router)
app.include_router(campaign_packager_router)
app.include_router(traffic_factory_router)

app.include_router(intelligence_priority_router)
app.include_router(product_router)
app.include_router(full_cycle_router)
app.include_router(revenue_router)

@app.get("/health")
def health():
    return {"status": "ok"}



















from backend.app.routes import market
app.include_router(market.router, prefix="/api")





from backend.app.engines.trade_memory import get_stats

@app.get("/api/market/stats")
def market_stats():
    return get_stats()


app.include_router(builder.router)

app.include_router(builder_intelligence.router)

app.include_router(autonomous_builder.router)

app.include_router(evolution.router)

app.include_router(max_evolution.router)


