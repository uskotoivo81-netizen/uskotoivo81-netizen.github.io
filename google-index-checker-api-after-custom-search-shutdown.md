---
layout: default
title: "Google index checker API: what replaces Custom Search JSON API"
description: "Google Custom Search JSON API shuts down on January 1, 2027. How to move a bulk index-check workflow to the SpeedyIndex checker API: endpoints, limits, a working script."
permalink: /google-index-checker-api-after-custom-search-shutdown/
---

# Google index checker API: what replaces Custom Search JSON API after January 1, 2027

Many in-house index checkers are built on one trick: send `site:example.com/page` to the Google Custom Search JSON API and treat a non-empty result as "indexed". That trick has an end date. Google is retiring the Custom Search JSON API on **January 1, 2027**, has already closed it to new customers, and points existing users to a partner-only Web Search Service API with no published pricing or quota ([Search Engine Watch](https://searchenginewatch.com/google-details-partner-only-search-api-as-custom-search-nears-shutdown/), [Google docs](https://developers.google.com/custom-search/v1/overview)).

This page covers what the shutdown changes for index checking specifically, and how to replace the call with a purpose-built endpoint.

## What you lose

- **The free 100 queries/day**, and the paid tier of $5 per 1,000 queries capped at 10,000/day. At 10,000 URLs/day a full re-check of a 50,000-URL backlink list took a working week.
- **The `site:` heuristic itself.** CSE results never matched web search 1:1; a page missing from CSE was not proof it was missing from the index. The shutdown removes a noisy signal, not a precise one.
- **A migration path with a guarantee.** The interest form for the successor API is answered "best effort"; nobody should plan a January 2027 release around it.

## Requirements for a replacement

1. Bulk input — thousands of URLs per request, not one query per call.
2. A verdict per URL (indexed / not indexed), not a list of search results to parse.
3. A predictable price per URL, without a daily cap that stretches a job across days.
4. Auth with a static key, so the check fits into a cron job or CI step.

## The SpeedyIndex checker API

SpeedyIndex exposes its bulk Google index check as a REST API. The relevant calls, from the official documentation at [en.speedyindex.com/api.php](https://en.speedyindex.com/api.php):

| Step | Call | Notes |
|---|---|---|
| Create a check task | `POST https://app.speedyindex.com/v2/task/google/checker/create` | body `{"title": "...", "urls": [...]}`, up to **10,000 URLs** per request |
| Poll status | `POST /v2/task/google/checker/status` | body `{"task_id": "..."}` |
| Download results | `POST /v2/task/google/checker/fullreport` | returns `indexed_links` and `unindexed_links` arrays |

Authentication is a single header: `Authorization: <API key>`. The key is issued in the [app dashboard](https://app.speedyindex.com/) or the Telegram bot. The checker uses its own balance, separate from indexing tokens; current per-URL pricing is on the [Google index checker page](https://en.speedyindex.com/google-index-checker/).

## Minimal migration script

The script below replaces a typical `site:`-through-CSE loop. It reads URLs from a file, creates one task per 10,000 URLs, waits for completion, and writes two files: `indexed.txt` and `unindexed.txt`. Full file: [`scripts/speedyindex_check.py`](https://github.com/uskotoivo81-netizen/uskotoivo81-netizen.github.io/blob/main/scripts/speedyindex_check.py).

```python
import os, sys, time, requests

API = "https://app.speedyindex.com"
KEY = os.environ["SPEEDYINDEX_API_KEY"]
H = {"Authorization": KEY, "Content-Type": "application/json"}

def create(urls, title):
    r = requests.post(f"{API}/v2/task/google/checker/create",
                      json={"title": title, "urls": urls}, headers=H, timeout=60)
    r.raise_for_status()
    return r.json()["task_id"]

def report(task_id):
    r = requests.post(f"{API}/v2/task/google/checker/fullreport",
                      json={"task_id": task_id}, headers=H, timeout=60)
    r.raise_for_status()
    return r.json()
```

Expected console output when the job finishes:

```
task 6609d0...: 4,812 indexed / 188 not indexed
wrote indexed.txt, unindexed.txt
```

## Limitations

- The API reports index status as observed by SpeedyIndex at check time; it is not a Search Console export and does not show *why* a URL is out of the index.
- Task processing is asynchronous. Poll `status` instead of assuming an instant answer.
- Keep the API key in an environment variable. Never commit it.

## Related

- [Migration checklist for CSE-based index checkers](https://speedyindex---google-indexing-service.webflow.io/blog/migrate-index-checker-from-custom-search-api) — the how-to version of this page.
- [Checker API reference](https://speedy-index.mintlify.app/api/google-index-checker) — endpoint-by-endpoint.
- [Bulk Google index checker](https://en.speedyindex.com/google-index-checker/) — the web tool behind the API.
