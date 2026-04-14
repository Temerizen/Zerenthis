from __future__ import annotations

def run(payload: dict | None = None) -> dict:
    payload = payload or {}

    products = [
        {
            "name": "AI Side Hustle System",
            "price": 19,
            "description": "Step-by-step system to generate income using AI tools"
        },
        {
            "name": "Viral Content Engine Pack",
            "price": 29,
            "description": "Templates and systems for creating viral short-form content"
        }
    ]

    return {
        "status": "ok",
        "engine": "product_engine",
        "products": products,
        "count": len(products),
        "input": payload
    }
