#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify verification sources in data/guide.json.

Ensures official announcements and repositories still exist and contain the required tokens.
"""
import json, os, re, sys, time, urllib.error, urllib.request

PROXY = os.environ.get("CLOAK_PROXY", "http://127.0.0.1:19001")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "guide.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))


def check(op, url, expected_token):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with op.open(req, timeout=40) as r:
            text = r.read().decode("utf-8", "replace")
            clean_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))
            if expected_token.lower() in clean_text.lower():
                return r.status, "OK"
            return r.status, "STALE"
    except urllib.error.HTTPError as e:
        return e.code, "HTTP_ERROR"
    except Exception as e:
        return 0, f"ERR: {e}"


def main():
    op = opener()
    d = json.load(open(DATA, encoding="utf-8"))
    sources = d.get("verification_sources", [])
    failed = False
    for s in sources:
        url = s["url"]
        token = s["expected_token"]
        status, res = check(op, url, token)
        print(f"[{res:<5}] {status:<3} | {s['name'][:30]:<32} | {url}")
        if res != "OK":
            failed = True
    if failed:
        sys.exit(1)
    print("\nAll verification sources verified successfully.")


if __name__ == "__main__":
    main()
