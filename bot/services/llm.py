import sys
import json
import httpx
from config import LMS_API_URL, LMS_API_KEY, LLM_API_KEY, LLM_API_BASE_URL, LLM_API_MODEL


def _lms_headers():
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def _lms_get(path: str):
    r = httpx.get(f"{LMS_API_URL}{path}", headers=_lms_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def _lms_post(path: str):
    r = httpx.post(f"{LMS_API_URL}{path}", headers=_lms_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get the list of all labs and tasks available in the LMS",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get the list of enrolled students and their groups",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get number of submissions per day for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, default 5"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get the completion rate percentage for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh and sync data from the autochecker into the LMS database",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def _execute_tool(name: str, args: dict) -> str:
    try:
        if name == "get_items":
            data = _lms_get("/items/")
            return f"{len(data)} items: " + json.dumps(data[:20])
        elif name == "get_learners":
            data = _lms_get("/learners/")
            return f"{len(data)} learners: " + json.dumps(data[:10])
        elif name == "get_scores":
            data = _lms_get(f"/analytics/scores?lab={args['lab']}")
            return json.dumps(data)
        elif name == "get_pass_rates":
            data = _lms_get(f"/analytics/pass-rates?lab={args['lab']}")
            return f"{len(data)} tasks: " + json.dumps(data)
        elif name == "get_timeline":
            data = _lms_get(f"/analytics/timeline?lab={args['lab']}")
            return json.dumps(data[:10])
        elif name == "get_groups":
            data = _lms_get(f"/analytics/groups?lab={args['lab']}")
            return json.dumps(data)
        elif name == "get_top_learners":
            limit = args.get("limit", 5)
            data = _lms_get(f"/analytics/top-learners?lab={args['lab']}&limit={limit}")
            return json.dumps(data)
        elif name == "get_completion_rate":
            data = _lms_get(f"/analytics/completion-rate?lab={args['lab']}")
            return json.dumps(data)
        elif name == "trigger_sync":
            data = _lms_post("/pipeline/sync")
            return json.dumps(data)
        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool error: {e}"


SYSTEM_PROMPT = """You are an LMS assistant bot. You help students and teachers get information about labs, scores, and performance.

You have access to tools that query the LMS backend. When a user asks a question:
1. Call the appropriate tool(s) to get the data
2. Analyze the results
3. Give a clear, concise answer

For greetings or unclear messages, respond helpfully and explain what you can do.
Always use tools to get real data — never make up numbers."""


def route(user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    max_iterations = 10
    for i in range(max_iterations):
        try:
            r = httpx.post(
                f"{LLM_API_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": LLM_API_MODEL,
                    "messages": messages,
                    "tools": TOOLS,
                    "tool_choice": "auto",
                    "max_tokens": 1000,
                },
                timeout=60,
            )
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            return f"LLM error: HTTP {e.response.status_code}. {e.response.text[:200]}"
        except Exception as e:
            return f"LLM error: {e}"

        response = r.json()
        choice = response["choices"][0]
        message = choice["message"]
        messages.append(message)

        # No tool calls — final answer
        if not message.get("tool_calls"):
            return message.get("content") or "No response from LLM."

        # Execute tool calls
        tool_calls = message["tool_calls"]
        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

        for tc in tool_calls:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except Exception:
                args = {}

            print(f"[tool] LLM called: {name}({json.dumps(args)})", file=sys.stderr)
            result = _execute_tool(name, args)
            print(f"[tool] Result: {result[:80]}", file=sys.stderr)

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })

    return "Sorry, I couldn't complete the request after multiple steps."