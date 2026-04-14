from __future__ import annotations
import json, os, time, base64, urllib.parse
from typing import Dict, Any, List, Optional

import requests

SWARM_PATH = "backend/data/swarm_leaderboard.json"
VAR_TRACK_PATH = "backend/data/variant_tracking.json"
POST_LOG_PATH = "backend/data/live_post_log.json"

PLATFORMS = ["x"]  # V21: ship X first, keep Reddit scaffolded but disabled

def _load(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _find_link(product: str, headline: str) -> Optional[str]:
    store = _load(VAR_TRACK_PATH)
    key = f"{product}||{headline}"
    rec = store.get(key, {})
    return rec.get("url")

def _generate_post(headline: str, link: str) -> str:
    candidates = [
        f"{headline}\n\nStart here: {link}",
        f"{headline}\n\nTry it now: {link}",
        f"People are sleeping on this:\n{headline}\n\n{link}",
        f"{headline}\n\nThis changes everything: {link}",
    ]
    # deterministic-ish without importing random
    idx = int(time.time()) % len(candidates)
    return candidates[idx]

def _pick_winner() -> Dict[str, Any]:
    swarm = _load(SWARM_PATH)
    if not isinstance(swarm, list) or not swarm:
        return {}
    return swarm[0]

def _post_to_x(text: str) -> Dict[str, Any]:
    """
    Preferred auth:
      - X_ACCESS_TOKEN (OAuth 2.0 user token or suitable user-context token)
    Fallback optional:
      - X_BEARER_TOKEN (may not work for user-context create-post flows depending on token type)
    """
    access_token = os.getenv("X_ACCESS_TOKEN", "").strip()
    bearer_token = os.getenv("X_BEARER_TOKEN", "").strip()

    token = access_token or bearer_token
    if not token:
        return {
            "status": "skipped",
            "platform": "x",
            "reason": "missing_credentials"
        }

    url = "https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        body = {}
        try:
            body = r.json()
        except Exception:
            body = {"raw": r.text}

        if 200 <= r.status_code < 300:
            post_id = None
            if isinstance(body, dict):
                post_id = ((body.get("data") or {}).get("id"))
            return {
                "status": "posted",
                "platform": "x",
                "http_status": r.status_code,
                "post_id": post_id,
                "response": body,
            }

        return {
            "status": "error",
            "platform": "x",
            "http_status": r.status_code,
            "response": body,
        }
    except Exception as e:
        return {
            "status": "error",
            "platform": "x",
            "reason": str(e),
        }

def _reddit_stub(text: str) -> Dict[str, Any]:
    """
    Reddit is intentionally disabled by default in V21.
    Kept as scaffold because API access/approval can vary.
    """
    enabled = os.getenv("REDDIT_ENABLE_POSTING", "").strip().lower() == "true"
    if not enabled:
        return {
            "status": "skipped",
            "platform": "reddit",
            "reason": "disabled_by_default"
        }

    client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    username = os.getenv("REDDIT_USERNAME", "").strip()
    password = os.getenv("REDDIT_PASSWORD", "").strip()
    subreddit = os.getenv("REDDIT_SUBREDDIT", "").strip()

    if not all([client_id, client_secret, username, password, subreddit]):
        return {
            "status": "skipped",
            "platform": "reddit",
            "reason": "missing_credentials"
        }

    user_agent = os.getenv("REDDIT_USER_AGENT", "Zerenthis/1.0 by automation")

    try:
        creds = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
        token_resp = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            headers={
                "Authorization": f"Basic {creds}",
                "User-Agent": user_agent,
            },
            data={
                "grant_type": "password",
                "username": username,
                "password": password,
            },
            timeout=30,
        )

        token_body = token_resp.json()
        access_token = token_body.get("access_token")
        if token_resp.status_code >= 300 or not access_token:
            return {
                "status": "error",
                "platform": "reddit",
                "http_status": token_resp.status_code,
                "response": token_body,
            }

        lines = text.splitlines()
        title = lines[0][:280] if lines else "Zerenthis update"
        body = "\n".join(lines[1:]).strip() or text

        submit_resp = requests.post(
            "https://oauth.reddit.com/api/submit",
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": user_agent,
            },
            data={
                "sr": subreddit,
                "kind": "self",
                "title": title,
                "text": body,
            },
            timeout=30,
        )

        try:
            submit_body = submit_resp.json()
        except Exception:
            submit_body = {"raw": submit_resp.text}

        if 200 <= submit_resp.status_code < 300:
            return {
                "status": "posted",
                "platform": "reddit",
                "http_status": submit_resp.status_code,
                "response": submit_body,
            }

        return {
            "status": "error",
            "platform": "reddit",
            "http_status": submit_resp.status_code,
            "response": submit_body,
        }
    except Exception as e:
        return {
            "status": "error",
            "platform": "reddit",
            "reason": str(e),
        }

def run_live_deploy() -> Dict[str, Any]:
    winner = _pick_winner()
    if not winner:
        return {"status": "no_swarm_data"}

    product = winner.get("product")
    headline = winner.get("headline")
    link = _find_link(product, headline)

    if not link:
        return {"status": "no_link_found", "product": product, "headline": headline}

    text = _generate_post(headline, link)

    results: List[Dict[str, Any]] = []
    results.append(_post_to_x(text))
    results.append(_reddit_stub(text))

    log = _load(POST_LOG_PATH)
    if not isinstance(log, list):
        log = []

    entry = {
        "product": product,
        "headline": headline,
        "link": link,
        "text": text,
        "results": results,
        "timestamp": time.time(),
    }
    log.append(entry)
    log = log[-200:]
    _save(POST_LOG_PATH, log)

    overall = "posted" if any(r.get("status") == "posted" for r in results) else "completed"

    return {
        "status": overall,
        "product": product,
        "headline": headline,
        "link": link,
        "results": results,
        "timestamp": entry["timestamp"],
    }
