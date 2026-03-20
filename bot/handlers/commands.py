import httpx
from config import LMS_API_URL, LMS_API_KEY

def handle_start() -> str:
    return "👋 Welcome to LMS Bot! Use /help to see available commands."

def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status\n"
        "/scores <lab> — Show scores for a lab\n"
        "/labs — List available labs"
    )

def handle_health() -> str:
    try:
        r = httpx.get(f"{LMS_API_URL}/health", headers={"Authorization": f"Bearer {LMS_API_KEY}"}, timeout=5)
        if r.status_code == 200:
            return "✅ Backend is up and running."
        return f"⚠️ Backend returned status {r.status_code}."
    except Exception as e:
        return f"❌ Backend unreachable: {e}"

def handle_scores(lab: str) -> str:
    return f"📊 Scores for {lab}: Not implemented yet."

def handle_labs() -> str:
    return "📚 Available labs: Not implemented yet."

def handle_unknown(text: str) -> str:
    return f"🤔 Unknown command: {text}. Use /help to see available commands."
