#!/usr/bin/env python3
"""Bulk Google index check via the SpeedyIndex checker API.

Usage:
    export SPEEDYINDEX_API_KEY=...
    python speedyindex_check.py urls.txt

Writes indexed.txt and unindexed.txt next to the input file.
Docs: https://en.speedyindex.com/api.php
"""
import os
import sys
import time

import requests

API = "https://app.speedyindex.com"
CHUNK = 10_000  # max URLs per task per the API docs


def headers():
    key = os.environ.get("SPEEDYINDEX_API_KEY")
    if not key:
        sys.exit("Set SPEEDYINDEX_API_KEY in the environment.")
    return {"Authorization": key, "Content-Type": "application/json"}


def post(path, payload):
    try:
        r = requests.post(f"{API}{path}", json=payload, headers=headers(), timeout=60)
        r.raise_for_status()
    except requests.RequestException as e:
        sys.exit(f"API error on {path}: {e}")
    data = r.json()
    if data.get("code") not in (0, None):
        sys.exit(f"API returned code {data.get('code')} on {path}: {data}")
    return data


def main(path):
    with open(path, encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]
    if not urls:
        sys.exit("No URLs in input file.")

    indexed, unindexed = [], []
    for i in range(0, len(urls), CHUNK):
        chunk = urls[i:i + CHUNK]
        task_id = post("/v2/task/google/checker/create",
                       {"title": f"check {os.path.basename(path)} {i // CHUNK + 1}", "urls": chunk})["task_id"]
        print(f"task {task_id}: {len(chunk)} URLs submitted")

        # Poll until the report is ready. Status payload shape may vary; treat a
        # non-empty report as completion.
        for _ in range(120):
            time.sleep(30)
            rep = post("/v2/task/google/checker/fullreport", {"task_id": task_id})
            res = rep.get("result", rep)
            if res.get("indexed_links") is not None or res.get("unindexed_links") is not None:
                indexed += [x if isinstance(x, str) else x.get("url", "") for x in res.get("indexed_links", [])]
                unindexed += [x if isinstance(x, str) else x.get("url", "") for x in res.get("unindexed_links", [])]
                print(f"task {task_id}: {len(res.get('indexed_links', [])):,} indexed / "
                      f"{len(res.get('unindexed_links', [])):,} not indexed")
                break
        else:
            print(f"task {task_id}: still processing after 60 min, re-run later")

    base = os.path.dirname(os.path.abspath(path))
    for name, rows in (("indexed.txt", indexed), ("unindexed.txt", unindexed)):
        with open(os.path.join(base, name), "w", encoding="utf-8") as f:
            f.write("\n".join(rows))
    print("wrote indexed.txt, unindexed.txt")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
