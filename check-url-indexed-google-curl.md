---
layout: page
title: "Check if a URL is indexed in Google with curl"
description: "A shell one-liner that tests a page for the two most common indexing blockers before you submit it: a non-200 status and a noindex directive."
permalink: /check-url-indexed-google-curl/
---

Before a URL goes into any indexing campaign, two things have to be true: the server returns `200` for the final URL, and neither the HTML nor the headers carry `noindex`. This note gives one command for both checks.

## Requirements

- `curl` 7.x or newer
- a shell (bash, zsh)

## Command

```bash
url="https://example.com/page/"
curl -sIL -A "Mozilla/5.0 (Linux; Android 10) Googlebot/2.1" "$url" | grep -iE "^HTTP/|^x-robots-tag|^location"
curl -sL -A "Mozilla/5.0 (Linux; Android 10) Googlebot/2.1" "$url" | grep -ioE '<meta[^>]+name="robots"[^>]*>'
```

## How to read the output

1. The first command prints every hop. You want exactly one `HTTP/2 200` line and no `location:` lines. A `301` followed by `200` means Google indexes the final URL, not the one you submitted; submit the final one.
2. A line `x-robots-tag: noindex` blocks indexing at the header level. Fix it on the server, then re-run.
3. The second command prints the robots meta tag if one exists. `content="noindex"` or `content="none"` blocks indexing; an empty result is what you want.

## When this is not enough

A clean `200` without `noindex` does not mean the page is indexed. It means the page is *eligible*. To see whether Google actually has it, check the URL in Search Console or run it through a bulk [Google index checker](https://en.speedyindex.com/google-index-checker/) together with the rest of your list. Google's documentation on [HTTP status codes and indexing](https://developers.google.com/crawling/docs/troubleshooting/http-status-codes) explains which codes drop a URL from the index.
