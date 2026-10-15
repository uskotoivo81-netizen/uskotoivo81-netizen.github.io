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
