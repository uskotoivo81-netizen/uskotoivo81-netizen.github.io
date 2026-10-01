---
layout: default
title: "Detect 'Discovered – currently not indexed' with the URL Inspection API"
description: "Python script that pulls coverage verdicts for a URL list through Google's URL Inspection API and flags pages stuck in Discovered – currently not indexed."
permalink: /detect-discovered-currently-not-indexed-url-inspection-api/
---

# Detect "Discovered – currently not indexed" with the URL Inspection API

This page shows a Python script that takes a list of URLs from a property you own, queries Google's URL Inspection API for each one, and prints the coverage state — so pages sitting in `Discovered - currently not indexed` or `Crawled - currently not indexed` surface as a flat CSV instead of one-by-one clicks in Search Console. Use it when a section of your site, or a batch of pages you point links at, stalls before the crawl stage.

One hard limit first: the API inspects only URLs inside properties verified in your own Search Console account. It does not accept third-party donor pages. For URLs outside your properties, the workable path is a bulk check against the live index — for example, [verify the indexing status of a URL list](https://en.speedyindex.com/google-index-checker/) — and that is a different mechanism: parsing what Google actually serves, not asking the API what it thinks.

## Requirements

- A Search Console property (domain or URL-prefix) where the target URLs live.
- A Google Cloud service account added to that property as a user, with the Search Console API enabled.
- Python 3.10+, packages `google-api-python-client` and `google-auth`.
- The service-account JSON key, exposed through an environment variable — never hard-coded.

## The script

Full file: [scripts/inspect_url_status.py](https://github.com/uskotoivo81-netizen/uskotoivo81-netizen.github.io/blob/main/scripts/inspect_url_status.py)

```python
{% raw %}# see scripts/inspect_url_status.py in this repository{% endraw %}
```

The script reads `urls.txt` (one URL per line), calls `urlInspection.index.inspect` for each, and writes `inspection_report.csv` with three columns: URL, `coverageState`, `lastCrawlTime`.

## How to run

1. Export the key path: `export GOOGLE_APPLICATION_CREDENTIALS=~/keys/gsc-sa.json`. The shell prints nothing — silence is success.
2. Put your URLs into `urls.txt` and run `python inspect_url_status.py sc-domain:example.com`. Expected console output per URL: `https://example.com/page -> Discovered - currently not indexed | last crawl: none`.
3. Open `inspection_report.csv`. Rows where `coverageState` is `Discovered - currently not indexed` and `lastCrawlTime` is empty are pages Google knows about but has never fetched.
4. Mind the quota: Google documents a limit of 2,000 inspection calls per property per day and 600 per minute. The script sleeps 150 ms between calls; a 10,000-URL list needs to be split across days or properties.

## Limitations

- Only your verified properties. Donor pages on other people's sites are out of scope by design.
- The verdict is Google's internal state, which can lag the live index by days. A page can serve in search while the API still reports an older state, and the reverse.
- `Discovered - currently not indexed` means the URL was never fetched; `Crawled - currently not indexed` means it was fetched and declined. The [crawled but not indexed status](https://en.speedyindex.com/fix-crawled-currently-not-indexed/) needs content-side fixes, while a discovered-only page usually needs crawl paths: internal links, sitemap freshness, server response time.
- The script does not request indexing. The Indexing API is a separate endpoint restricted to job postings and broadcast events, and this page does not pretend otherwise.

## Further

- Official reference: [Method: index.inspect](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect) — request body, response fields, quotas.
- Previous build in this series: [Google index checker API after the Custom Search shutdown](https://uskotoivo81-netizen.github.io/google-index-checker-api-after-custom-search-shutdown/).
