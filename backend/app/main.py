from fastapi import FastAPI
import app.routes.system as system
import app.routes.money as money
import app.routes.traffic as traffic
import app.routes.evolution as evolution
import app.routes.decision as decision
import app.routes.execution as execution

app = FastAPI(title="Zerenthis Empire")

app.include_router(system.router)
app.include_router(money.router)
app.include_router(traffic.router)
app.include_router(evolution.router)
app.include_router(decision.router)
app.include_router(execution.router)

@app.get("/health")
def health():
    return {"status": "Zerenthis Alive"}
