---
layout: default
title: "Fix PDF indexing problems in Google: a field guide"
description: "Why Google skips your PDF and how to fix it: text layer, crawl access, X-Robots-Tag, canonical signals, and how to confirm the file is actually in the index."
permalink: /fix-pdf-indexing-problems-in-google/
---

# Fix PDF indexing problems in Google: a field guide

A PDF that does not appear in Google search is usually missing one of four things: a real text layer, an open crawl path, correct indexing directives, or a clear canonical signal. Work through the list in that order — each layer is a prerequisite for the next.

## 1. Confirm the document has a real text layer

Open the PDF and try selecting a word with your cursor. Paste the selection into a plain-text editor. If you get garbled characters, blank output, or nothing at all, the document contains images of text rather than actual text. Google can apply optical character recognition to scanned PDFs, but the result is less reliable than a native text layer and may not cover all pages.

To fix this:

- Re-export the document from its source application and choose a format that embeds text rather than rasterising it.
- For scanned originals, run OCR and review the output. Check reading order in columns and tables, confirm that headings copy correctly, and verify that numbers and names come out without substitutions.
- Google indexes the full text of PDFs with a text layer. For image-only PDFs, it attempts OCR on the first few pages only.

After correcting the document, check file size. Google documents a 10 MB limit for PDF indexing; files above that threshold may be partially or fully skipped.

## 2. Verify that Google can crawl the URL

A correct text layer does nothing if the crawler cannot reach the file. The most common obstacles:

**robots.txt disallow.** Open the site's `robots.txt` and search for any `Disallow` rule that covers the PDF's path. If the path is blocked, Google will not fetch the file and cannot read any directive inside the response — including a `noindex` header, which means it cannot clear the file from results either.

**Authentication.** PDFs behind a login, IP allow-list, or token-gated URL will not be crawled. The file must be publicly accessible without redirects to a login page.

**Redirect chain ending at a non-PDF.** If the PDF URL redirects to an HTML error page or a dashboard, Google sees the destination, not the document.

To test, request the URL with a tool that mimics Googlebot's mobile crawler User-Agent and check that the server returns HTTP 200 and a `Content-Type: application/pdf` response with no intervening redirects.

## 3. Check the X-Robots-Tag response header

Unlike HTML pages, PDFs cannot carry a `<meta name="robots">` tag inside the document body. The equivalent for non-HTML files is the HTTP response header `X-Robots-Tag`. A `noindex` directive in this header blocks the file from search results:

```
X-Robots-Tag: noindex
```

Inspect the raw response headers for the PDF URL. The header can be set at the server, CDN, or application layer and is easy to overlook after a migration or CDN configuration change.

Note: if `robots.txt` disallows the path, Google will not crawl the file and therefore cannot read the `X-Robots-Tag` header. Fix `robots.txt` first, then check the header.

## 4. Resolve duplicate URLs and set a canonical signal

If the same PDF is accessible at more than one URL — `http` vs `https`, `www` vs non-`www`, with and without query strings, or under multiple paths — Google will attempt to choose a canonical. When it picks a different URL than you intend, your preferred version may not rank.

For PDFs, the canonical signal goes in the HTTP response header rather than inside the file:

```http
Link: <https://example.com/files/guide.pdf>; rel="canonical"
```

Add this header to the canonical version. For duplicates that should consolidate to the canonical, a 301 redirect is cleaner than a header. Keep `sitemap.xml` and internal links consistent with the canonical URL.

## 5. Confirm the file is in the index

After fixing the issues above, submit the URL through Google Search Console's URL inspection tool to request indexing and check the crawled status. Do not rely on the `site:` operator alone — Search Console documentation notes that operator results are incomplete.

If you manage a list of PDF URLs and need to check their index status in bulk, [SpeedyIndex](https://en.speedyindex.com/) provides a URL-by-URL index check. The result shows whether each URL is indexed as of the check date and the title under which it appears in results. A title that does not match the current document heading means an older cached version is in the index.

For pages stuck in "crawled but not indexed" status after the technical issues are resolved, the walkthrough at [en.speedyindex.com/fix-crawled-currently-not-indexed](https://en.speedyindex.com/fix-crawled-currently-not-indexed/) covers the next steps.

## Diagnostic order

Work down this list and stop at the first failure:

1. **Text layer** — select text in the PDF; it should paste cleanly.
2. **File size** — under 10 MB.
3. **robots.txt** — no `Disallow` covering the PDF path.
4. **HTTP response** — 200, `Content-Type: application/pdf`, no `X-Robots-Tag: noindex`.
5. **Duplicate URLs** — one canonical URL with consistent internal links and sitemap entry.
6. **Index confirmation** — URL inspection in Search Console or a bulk index check.

## Related guides

- [Canonicalize a PDF to its HTML equivalent with an HTTP header](/canonicalize-pdf-to-html/) — when you want the HTML page to rank instead of the PDF.
- [Remove a noindex response header from a PDF](/remove-noindex-from-pdf/) — step-by-step header audit.
- [Diagnose an image-only PDF that is not indexable](/diagnose-image-only-pdf/) — OCR and text-layer checks in detail.
- [Improve PDF search ranking without creating duplicate content](/improve-pdf-search-ranking/) — signals that lift a correctly indexed PDF.
