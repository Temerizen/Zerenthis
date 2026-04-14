# EXECUTION ENGINE

This system:
- scans generated systems
- executes latest ones
- scores output
- logs performance

Endpoints:
POST /api/execution/run
GET  /api/execution/logs

Each system must expose:
def run():
    return result
