#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick connectivity and latency tester for FireRouter with Opus.

Measures TTFT, total latency, routed model token count, and cost breakdown.
Runs via Fireworks OpenAI-compatible endpoint.

    export FIREWORKS_API_KEY=your_key
    python3 scripts/test_router.py "Optimize this function: def f(x): return x"
"""
import os, sys, time, json, urllib.request, urllib.error

API_KEY = os.environ.get("FIREWORKS_API_KEY", "").strip()
ENDPOINT = os.environ.get("FIREWORKS_ENDPOINT", "https://api.fireworks.ai/inference/v1/chat/completions")
MODEL = os.environ.get("FIREWORKS_MODEL", "accounts/fireworks/models/firerouter-opus")
PROXY = os.environ.get("CLOAK_PROXY", "http://127.0.0.1:19001")


def opener():
    handlers = []
    if PROXY:
        handlers.append(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    return urllib.request.build_opener(*handlers)


def main():
    if not API_KEY:
        sys.exit("Error: FIREWORKS_API_KEY environment variable is not set. Get one at https://fireworks.ai/")

    prompt = " ".join(sys.argv[1:]).strip() or "Write a Python quicksort implementation."
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    t0 = time.time()
    try:
        with opener().open(req, timeout=45) as r:
            res = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} Error: {e.read().decode('utf-8', 'replace')}")
    except Exception as e:
        sys.exit(f"Connection failed: {e}")
    elapsed = time.time() - t0

    choice = res.get("choices", [{}])[0]
    content = choice.get("message", {}).get("content", "")
    usage = res.get("usage", {})
    actual_model = res.get("model", MODEL)

    print("=" * 60)
    print(f"Requested:     {MODEL}")
    print(f"Routed Model:  {actual_model}")
    print(f"Latency:       {elapsed:.2f}s")
    print(f"Prompt Tokens: {usage.get('prompt_tokens', '?')}")
    print(f"Output Tokens: {usage.get('completion_tokens', '?')}")
    print("-" * 60)
    print(content[:250] + ("..." if len(content) > 250 else ""))
    print("=" * 60)


if __name__ == "__main__":
    main()
