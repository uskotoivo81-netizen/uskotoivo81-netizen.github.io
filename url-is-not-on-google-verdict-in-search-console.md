---
layout: default
title: "The \"URL is not on Google\" verdict in Search Console: what every status means and what to do next"
description: "What the url is not on google verdict in search console really says, how it differs from the live test, how to read Page indexing, plus a Python logger."
permalink: /url-is-not-on-google-verdict-in-search-console/
---

# The "URL is not on Google" verdict in Search Console: what every status means and what to do next

The url is not on google verdict in search console sends most people straight to the "Request indexing" button, and that is usually the wrong first move. The verdict is a summary; the reason sits lower, in the Page indexing section, and the fix depends on which field there is red. This page covers all seven verdicts the URL Inspection tool can produce (four for the indexed version, three for the live test), shows how to read the fields underneath them, and ends with a working Python script that logs verdicts for a whole list of URLs through the official URL Inspection API.

## Two inspections, two different questions

**The indexed version** reports what Google holds in its index for the URL right now: the last crawl, the canonical Google chose, and whether the page is eligible to appear in Search. This is the default view.

**The live test** ("Test live URL") fetches the page at this moment with Google-InspectionTool and checks whether the fetch, robots.txt and indexing directives would allow indexing. It does not consult the index and does not predict Google's decision; the help page states plainly that no test can guarantee a page will be included in the index. The live test has a per-property daily limit and needs a page reachable without a login.

## The four indexed-version verdicts

### URL is on Google

Indexed and eligible to appear in Search results. Eligibility is not a ranking promise and, as the help page notes, not even a promise that the page is being shown; a `site:` query settles that. Nothing to fix at the indexing level.

### URL is on Google, but has issues

In the index, but something attached to the page is broken: malformed structured data, an invalid AMP alternate, and similar enhancement-level problems. The page can still rank; it may just lose the rich result it was built for. Open the enhancement report named in the verdict card, fix the markup, re-run the live test.

### URL is not on Google

The URL will not appear in Search results. This verdict alone is never the diagnosis; the Page indexing section always carries the reason: robots.txt, noindex, a fetch failure, a canonical pointing elsewhere, or a crawl that did not lead to indexing.

### URL is an alternate version

The inspected URL is an AMP page serving as the alternate of a canonical non-AMP page. Usually no action is required; inspect the canonical instead.

## The three live-test verdicts

**URL is available to Google.** Not blocked, no detectable errors that would prevent indexing. The green light for "Request indexing" after a fix, but it says nothing about whether the page is in the index now.

**URL is available to Google, but has issues.** Indexable, but some enhancements may not show. Fix the markup, test again.

**URL is not available to Google.** A critical issue prevents the page from appearing in Search; the Availability section names it (robots.txt block, noindex, server error, redirect, soft 404). Fix the cause first: the tool will not accept an indexing request while the live test says the page is non-indexable.

## What the live test deliberately does not check

A passing live test still leaves several causes of a missing page untouched. According to Google's documentation it does not evaluate:

- manual actions, content removals, quality and security guidelines, or temporarily blocked URLs;
- whether the URL is listed in any sitemap or linked from any referring page;
- duplicate or canonical selection, which only happens at indexing time;
- the "crawled, currently not indexed" and "discovered, currently not indexed" states;
- whether a detected video is actually indexed.

So "available to Google" plus "not on Google" is a consistent pair: the page is indexable and Google has chosen not to index it. That needs a different playbook than a robots.txt block.

## How to read the Page indexing section

This is where the verdict turns into a cause. The section has three groups.

**Discovery.** *Sitemaps* lists the sitemaps that reference the URL as far as Google knows; "No referring sitemap" is not fatal, but a page absent from every sitemap and every internal link is easy to deprioritise. *Referring page* shows a page that may have led Google to the URL; its absence does not prove there is none.

**Crawl.** *Last crawl* is the timestamp every other field is based on; if it is empty, Google has never successfully crawled the page. *Crawled as* shows the desktop or smartphone crawler. *Crawl allowed?* reflects robots.txt. *Page fetch* shows Successful, Failed with a reason, or N/A. *Indexing allowed?* reflects a noindex rule in the meta tag or the X-Robots-Tag header. One documented quirk: when robots.txt blocks crawling, "Indexing allowed?" always reads Yes, because Google could not read the page to find a noindex.

**Indexing.** *User-declared canonical* is what the page declares (link tag, HTTP header or sitemap). *Google-selected canonical* is the URL Google decided to index. When they differ, the inspected URL is treated as a duplicate of the selected one; the Google-selected value can lag the index by a few hours.

Read these fields top to bottom and stop at the first problem:

| What the report shows | Likely cause | Next step |
|---|---|---|
| Crawl allowed? = No | robots.txt disallow | Remove the rule. robots.txt is not a removal mechanism: a blocked URL can still sit in the index without a snippet; use noindex or a password to keep a page out. |
| Page fetch = Failed (server error) | 5xx, timeout, firewall blocking Googlebot | Fix the server, then live-test and request indexing. |
| Page fetch = Failed (redirect) | URL redirects | Inspection tools do not follow redirects. Inspect the final URL; fix chains and loops. |
| Page fetch = Failed (not found / soft 404) | 404, 410 or a thin page returning 200 | Restore the content or let the URL drop out; do not request indexing of a 404. |
| Indexing allowed? = No | noindex in meta or X-Robots-Tag | Remove the directive on the page and on any template that injects it. |
| Google-selected canonical differs from user-declared | Duplicates, inconsistent canonicals, parameter variants | Decide which URL should win, make every signal (canonical tag, internal links, sitemap, redirects) agree, inspect the winner. |
| All clean, Last crawl present | Crawled, currently not indexed | A quality and link problem, not a technical one. |
| All clean, Last crawl empty | Discovered, currently not indexed | Google knows the URL but has not fetched it; internal links and sitemaps are the lever. |

The last two rows are the frustrating ones because nothing in the report is red. For those cases the separate [guide to the crawled, currently not indexed error](https://en.speedyindex.com/fix-crawled-currently-not-indexed/) walks through the quality-side causes and what tends to move such pages.

## Logging verdicts for a URL list with the URL Inspection API

Inspecting pages one at a time stops being practical past a few dozen URLs. The same data is available through the Search Console API method `urlInspection.index.inspect` (`POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect`). The request takes two required fields, `inspectionUrl` and `siteUrl`, plus an optional `languageCode`; `inspectionUrl` must belong to the property named in `siteUrl`, written exactly as in Search Console (`sc-domain:example.com` for a Domain property, or a URL-prefix property with its trailing slash). Either the `webmasters` or `webmasters.readonly` scope is accepted.

The response object `inspectionResult.indexStatusResult` carries the fields that matter:

- `verdict` — `PASS` (equivalent to Valid in Search Console), `FAIL` (Error or Invalid), `NEUTRAL` (Excluded) or `VERDICT_UNSPECIFIED`; `PARTIAL` is reserved and no longer used.
- `coverageState` — a text label describing whether Google could find and index the page.
- `indexingState`, `robotsTxtState`, `pageFetchState` — the noindex, robots.txt and page-fetch states.
- `lastCrawlTime`, `crawledAs`, `userCanonical`, `googleCanonical`, `sitemap`, `referringUrls` — the Discovery, Crawl and Indexing data the UI shows.

`inspectionResult.inspectionResultLink` opens the same inspection in the Search Console UI.

Quotas per property are 2,000 queries per day and 600 per minute. The script below spaces calls to stay under the per-minute cap, stops at the daily cap, backs off on HTTP 429 and 5xx responses, and writes every row to CSV as it goes so a crash does not lose work.

```python
#!/usr/bin/env python3
"""
inspect_urls.py -- log URL Inspection verdicts for a list of URLs
that belong to one of your own Search Console properties.

Install:
    pip install google-api-python-client google-auth

Setup:
    1. In Google Cloud, create a service account, enable the
       "Google Search Console API" for the project and download the
       service account's JSON key.
    2. In Search Console (Settings -> Users and permissions), add the
       service account's email address as a user of the property.
    3. Put one URL per line in urls.txt. Every URL must sit inside the
       property given in --site, or the API rejects it.

Run:
    python inspect_urls.py --site "sc-domain:example.com" \\
        --key service-account.json --input urls.txt --output verdicts.csv
"""

import argparse
import csv
import sys
import time

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
PER_MINUTE_CAP = 600          # queries per minute per property
PER_DAY_CAP = 2000            # queries per day per property
MIN_INTERVAL = 60.0 / PER_MINUTE_CAP

INDEX_FIELDS = [
    "verdict",
    "coverageState",
    "indexingState",
    "robotsTxtState",
    "pageFetchState",
    "lastCrawlTime",
    "crawledAs",
    "userCanonical",
    "googleCanonical",
]
COLUMNS = ["url"] + INDEX_FIELDS + ["inspectionResultLink", "error"]


def load_urls(path):
    seen, urls = set(), []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            url = line.strip()
            if url and not url.startswith("#") and url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def inspect(service, site, url, retries=4):
    body = {"inspectionUrl": url, "siteUrl": site}
    for attempt in range(retries):
        try:
            return service.urlInspection().index().inspect(body=body).execute()
        except HttpError as err:
            status = err.resp.status
            retryable = status == 429 or status >= 500
            if retryable and attempt < retries - 1:
                time.sleep(5 * (2 ** attempt))
                continue
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", required=True,
                        help='Property as shown in Search Console, e.g. "sc-domain:example.com" '
                             'or "https://www.example.com/"')
    parser.add_argument("--key", required=True, help="Path to the service account JSON key")
    parser.add_argument("--input", default="urls.txt", help="Text file, one URL per line")
    parser.add_argument("--output", default="verdicts.csv", help="CSV file to write")
    args = parser.parse_args()

    urls = load_urls(args.input)
    if not urls:
        sys.exit("No URLs found in " + args.input)
    if len(urls) > PER_DAY_CAP:
        print(f"{len(urls)} URLs listed; only the first {PER_DAY_CAP} will be inspected today "
              f"(per-property daily quota).", file=sys.stderr)
        urls = urls[:PER_DAY_CAP]

    creds = service_account.Credentials.from_service_account_file(args.key, scopes=SCOPES)
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    with open(args.output, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS)
        writer.writeheader()

        for n, url in enumerate(urls, start=1):
            started = time.monotonic()
            row = {col: "" for col in COLUMNS}
            row["url"] = url
            try:
                data = inspect(service, args.site, url)
                result = data.get("inspectionResult", {})
                index_status = result.get("indexStatusResult", {})
                for field in INDEX_FIELDS:
                    row[field] = index_status.get(field, "")
                row["inspectionResultLink"] = result.get("inspectionResultLink", "")
            except HttpError as err:
                row["error"] = f"HTTP {err.resp.status}"
            writer.writerow(row)
            out.flush()
            print(f"[{n}/{len(urls)}] {row['verdict'] or row['error']:<10} {url}")

            # stay under the per-minute quota
            elapsed = time.monotonic() - started
            if elapsed < MIN_INTERVAL:
                time.sleep(MIN_INTERVAL - elapsed)

    print(f"Done. {len(urls)} rows written to {args.output}")


if __name__ == "__main__":
    main()
```

Sort the CSV by `verdict`, then by `coverageState`, and the "URL is not on Google" set splits into technical buckets (robots, noindex, fetch failures, canonical conflicts) and the quality bucket where every field is clean. A `NEUTRAL` verdict with a successful fetch and a self-canonical is the API-side signature of the crawled-but-not-indexed case.

## Where the API stops

The API has one hard boundary: `inspectionUrl` must be inside the property named in `siteUrl`. It cannot inspect a backlink on someone else's domain, a syndicated copy, or a client site that has not granted access. For those URLs, [checking indexation without Search Console](https://en.speedyindex.com/google-index-checker/) is the only option, and an external checker that accepts arbitrary URLs is the practical tool for link audits. Search Console stays the source of truth for your own pages; the external check covers everything else.

## FAQ

**Does "URL is on Google" mean the page ranks?**
No. It means the page is indexed and eligible to appear. The help page says outright that the status does not guarantee the page is shown in results; ranking is a separate question of relevance and links.

**The live test says "available to Google" but the indexed version says "not on Google". Which one is right?**
Both. The live test only confirms that the page can be fetched and is not blocked; the indexed version reflects what Google actually decided. Treat the pair as "indexable but not indexed" and look at links, sitemaps and content rather than at technical blocks.

**Why does "Indexing allowed?" say Yes when the page has a noindex tag?**
If robots.txt blocks crawling, Google cannot read the page, so it cannot see the noindex and the field always reads Yes. Lift the robots.txt block first; the noindex will be detected on the next crawl.

**Can the URL Inspection API check pages on other websites?**
No. Every request is scoped to a verified property, and the inspected URL must belong to it. Pages on other domains need an external index check.

**How many URLs can be inspected through the API?**
Per property: 2,000 queries per day and 600 per minute. Larger sites have to choose which URLs to log each day; sorting by business value or by recent changes is a common approach.

## Sources

- URL Inspection Tool, Search Console Help — https://support.google.com/webmasters/answer/9012289
- Method urlInspection.index.inspect, Search Console API reference — https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect
- UrlInspectionResult and IndexStatusInspectionResult, Search Console API reference — https://developers.google.com/webmaster-tools/v1/UrlInspectionResult
- Usage limits, Search Console API — https://developers.google.com/webmaster-tools/limits
- Redirects and Google Search (inspection tools do not follow redirects) — https://developers.google.com/search/docs/crawling-indexing/301-redirects
- Introduction to robots.txt (robots.txt is not a mechanism for keeping a page out of Google) — https://developers.google.com/search/docs/crawling-indexing/robots/intro
