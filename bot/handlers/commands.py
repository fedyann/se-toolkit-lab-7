import httpx
from config import LMS_API_URL, LMS_API_KEY


def _headers():
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def _get(path: str):
    url = f"{LMS_API_URL}{path}"
    r = httpx.get(url, headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def handle_start() -> str:
    return "👋 Welcome to LMS Bot!\nUse /help to see available commands."


def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Per-task pass rates for a lab (e.g. /scores lab-04)"
    )


def handle_health() -> str:
    try:
        items = _get("/items/")
        count = len(items)
        return f"✅ Backend is healthy. {count} items available."
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({LMS_API_URL}). Check that the services are running. ({e})"
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_labs() -> str:
    try:
        items = _get("/items/")
        labs = [i for i in items if i.get("type") == "lab" or i.get("item_type") == "lab"]
        if not labs:
            return "No labs found in the backend."
        lines = "\n".join(f"- {l['title']}" for l in labs)
        return f"Available labs:\n{lines}"
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({LMS_API_URL}). Check that the services are running. ({e})"
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_scores(lab: str) -> str:
    if not lab:
        return "⚠️ Please specify a lab. Example: /scores lab-04"
    try:
        data = _get(f"/analytics/pass-rates?lab={lab}")
        if not data:
            return f"No data found for lab '{lab}'. Check the lab name (e.g. lab-04)."
        lines = []
        for item in data:
            name = item.get("task", "?")
            score = item.get("avg_score", 0)
            attempts = item.get("attempts", 0)
            lines.append(f"- {name}: {score:.1f}% ({attempts} attempts)")
        return f"Pass rates for {lab}:\n" + "\n".join(lines)
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({LMS_API_URL}). ({e})"
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_unknown(text: str) -> str:
    return f"🤔 Unknown command: '{text}'. Use /help to see available commands."