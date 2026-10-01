#!/usr/bin/env python3
"""Bulk-inspect URLs through Google's URL Inspection API.

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=~/keys/gsc-sa.json
    python inspect_url_status.py sc-domain:example.com [urls.txt]

Reads one URL per line, writes inspection_report.csv with
URL, coverageState, lastCrawlTime. Flags pages stuck in
'Discovered - currently not indexed'.
"""
import csv
import os
import sys
import time

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python inspect_url_status.py <siteUrl> [urls.txt]")
        sys.exit(1)
    site_url = sys.argv[1]
    urls_file = sys.argv[2] if len(sys.argv) > 2 else "urls.txt"

    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not key_path:
        print("Error: set GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON key.")
        sys.exit(1)

    creds = service_account.Credentials.from_service_account_file(key_path, scopes=SCOPES)
    service = build("searchconsole", "v1", credentials=creds)

    try:
        with open(urls_file, encoding="utf-8") as fh:
            urls = [line.strip() for line in fh if line.strip()]
    except FileNotFoundError:
        print(f"Error: {urls_file} not found.")
        sys.exit(1)

    rows = []
    for url in urls:
        body = {"inspectionUrl": url, "siteUrl": site_url}
        try:
            resp = service.urlInspection().index().inspect(body=body).execute()
            result = resp.get("inspectionResult", {}).get("indexStatusResult", {})
            state = result.get("coverageState", "UNKNOWN")
            last_crawl = result.get("lastCrawlTime", "")
        except HttpError as err:
            state = f"HTTP {err.resp.status}"
            last_crawl = ""
            if err.resp.status == 429:
                print("Quota hit (429). Stopping; rerun tomorrow or split the list.")
                rows.append([url, state, last_crawl])
                break
        print(f"{url} -> {state} | last crawl: {last_crawl or 'none'}")
        rows.append([url, state, last_crawl])
        time.sleep(0.15)  # stay under 600 calls/minute

    with open("inspection_report.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["url", "coverageState", "lastCrawlTime"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to inspection_report.csv")


if __name__ == "__main__":
    main()
