---
layout: default
title: "How to test robots.txt rules now that Search Console has no robots.txt Tester"
description: "A robots.txt tester workflow for 2026: what the Search Console robots.txt report still shows, how Google picks the winning rule, and a Python checker you can run locally."
permalink: /test-robots-txt-rules-without-search-console-tester/
---

# How to test robots.txt rules now that Search Console has no robots.txt Tester

For years the answer to "is this URL blocked?" was the robots.txt Tester inside Search Console: paste a path, pick Googlebot, read the highlighted line. Google retired that tool in late 2023 when it launched the robots.txt report, and the report answers a different question. It tells you whether Google could fetch your file, not which rule blocks a given URL. This page shows what the report still gives you, the matching rules Google applies today, three ways to test a rule before it goes live, and a short Python checker that follows Google's precedence instead of a generic parser's.

## What the robots.txt report shows, and what it doesn't

The report sits under Settings in Search Console and is available only for domain-level properties: a Domain property, or a URL-prefix property without a path. For each robots.txt file Google found in the last 30 days it lists:

- **File path**: the full URL Google checked. A Domain property shows up to 20 hosts, chosen by crawl rate.
- **Fetch status**: Fetched, Not Fetched (Not found, 404), or Not Fetched (any other reason).
- **Checked on** and **Size**: when Google last tried, and the file size in bytes.
- **Issues**: parsing problems. Errors stop a rule from being used; warnings don't.

From the file's menu you can request a recrawl after a fix. The help page is clear that a recrawl "doesn't guarantee an immediate recrawl of unblocked URLs".

What the report does not do is evaluate a URL against your rules. For a single live URL, Google points you to the URL Inspection tool, which reports "Blocked by robots.txt" in the Page indexing section. That works only for URLs already on a live site you own, one at a time, and only against the version of the file Google has cached. It can't tell you what a draft file would do.

## How Google decides whether a URL is blocked

Every test below is only as good as the matching logic behind it. These are the rules from Google's robots.txt specification (last updated 31 August 2026):

1. **One group per crawler.** Googlebot follows the group with the most specific user-agent that matches it. Groups naming the same user-agent are merged. A specific group is never combined with the `*` group, and the order of groups in the file doesn't matter.
2. **The longest path wins.** Among the `allow` and `disallow` rules that match a URL, the one with the longest path decides.
3. **Ties go to allow.** If an `allow` and a `disallow` rule are equally specific, the least restrictive one applies.
4. **Two wildcards.** `*` matches any sequence of characters; `$` marks the end of the URL. A trailing `*` changes nothing.
5. **Paths are case-sensitive.** `Disallow: /shop/` does not block `/Shop/cart`. Field names and user-agent values are case-insensitive.
6. **Four fields.** Google supports `user-agent`, `allow`, `disallow` and `sitemap`. Everything else, including `crawl-delay`, is ignored.
7. **500 KiB.** Content past the first 500 KiB of the file is ignored.

Two operational details catch people out. Google generally caches the file for up to 24 hours, so a fix is not instant. And server errors are not neutral: on a 5xx response Google stops crawling the site for the first 12 hours while retrying, then falls back to the last good copy for up to 30 days. A 4xx other than 429 is treated as "no robots.txt", which means no restrictions at all.

## A worked example

Take this file:

```text
User-agent: *
Disallow: /shop/
Allow: /shop/catalog/
Disallow: /*?sort=
Disallow: /*.pdf$
Crawl-delay: 10

User-agent: Googlebot-Image
Disallow: /photos/
```

Here is how Googlebot reads five URLs:

| URL | Result | Deciding rule |
|---|---|---|
| `/shop/cart` | blocked | `Disallow: /shop/` |
| `/shop/catalog/shoes` | allowed | `Allow: /shop/catalog/` (14 characters beats 6) |
| `/shop/catalog/shoes?sort=price` | allowed | `Allow: /shop/catalog/` is longer than `Disallow: /*?sort=` |
| `/docs/guide.pdf` | blocked | `Disallow: /*.pdf$` |
| `/docs/guide.pdf?v=2` | allowed | `$` requires the URL to end in `.pdf`; this one doesn't |

The third row is the one most people get wrong. The site owner meant to block every sorted listing, but inside `/shop/catalog/` the longer `allow` rule wins. If sorted catalog pages must stay out of the crawl, the rule has to be at least as specific, for example `Disallow: /shop/catalog/*?sort=`.

Two more readings from the same file: `/photos/a.jpg` is allowed for Googlebot, because the `Googlebot-Image` group doesn't apply to it, while Googlebot-Image follows only its own group and is blocked there. And `Crawl-delay: 10` is ignored by Google.

## Three ways to test a rule before you publish it

### 1. Paste the draft into a browser-based tester

The fastest check is to paste the draft file, enter the user-agent token and list the paths you care about. With the IndexFix tool you can [test your robots.txt rules online](https://indexfixtools.com/robots-txt-tester/): it applies the same precedence as above, shows which line decides each URL and flags unsupported lines like `crawl-delay`. The matching runs in your browser, so a draft never leaves your machine.

### 2. Run Google's own parser

Google publishes the C++ library its crawlers use, [google/robotstxt](https://github.com/google/robotstxt). Build it once and you can check a URL against a file from the command line:

```bash
git clone https://github.com/google/robotstxt.git && cd robotstxt
bazel build :robots_main
bazel-bin/robots_main ~/robots.txt Googlebot https://example.com/shop/catalog/shoes?sort=price
```

This is the reference implementation, so it's the right tool for settling an argument. It needs a build toolchain, which is why most teams keep a lighter check for everyday edits.

### 3. Script the check in Python, but not with the standard library

`urllib.robotparser` ships with Python, but it was not written to Google's rules. On the example file above, Python 3.13's parser reports `/shop/catalog/shoes?sort=price` as blocked, while Google's longest-match rule allows it. The script below implements the Google rules from the specification and nothing else (also saved as [scripts/robots_check.py](https://github.com/uskotoivo81-netizen/uskotoivo81-netizen.github.io/blob/main/scripts/robots_check.py)):

```python
#!/usr/bin/env python3
"""robots_check.py - test URLs against robots.txt with Google's matching rules.
Usage: python robots_check.py robots.txt Googlebot /path1 "/path2?q=1"
"""
import re, sys

def parse(text):
    groups, current, last_was_agent, unsupported = [], None, False, []
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, value = (p.strip() for p in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            if not last_was_agent:
                current = {"agents": [], "rules": []}
                groups.append(current)
            current["agents"].append(value.lower())
            last_was_agent = True
            continue
        last_was_agent = False
        if field in ("allow", "disallow") and current is not None:
            current["rules"].append((field, value, n))
        elif field != "sitemap":
            unsupported.append((n, raw.strip()))
    return groups, unsupported

def pick_rules(groups, agent):
    agent, best_len, rules = agent.lower(), -1, []
    for g in groups:
        for a in g["agents"]:
            if a != "*" and agent.startswith(a):
                if len(a) > best_len:
                    best_len, rules = len(a), list(g["rules"])
                elif len(a) == best_len:
                    rules += g["rules"]
    if best_len >= 0:
        return rules
    return [r for g in groups if "*" in g["agents"] for r in g["rules"]]

def to_regex(path):
    anchored = path.endswith("$")
    body = re.escape(path[:-1] if anchored else path).replace(r"\*", ".*")
    return re.compile("^" + body + ("$" if anchored else ""))

def decide(rules, url_path):
    best = None
    for kind, path, line in rules:
        if kind == "disallow" and path == "":
            continue
        if to_regex(path).match(url_path):
            cand = (len(path), kind == "allow", f"{kind.capitalize()}: {path}", line)
            if best is None or cand[:2] > best[:2]:
                best = cand
    if best is None:
        return "allowed", "no matching rule"
    return ("allowed" if best[1] else "blocked"), f"line {best[3]}: {best[2]}"

if __name__ == "__main__":
    groups, unsupported = parse(open(sys.argv[1], encoding="utf-8").read())
    rules = pick_rules(groups, sys.argv[2])
    for path in sys.argv[3:]:
        verdict, why = decide(rules, path)
        print(f"{verdict:8} {path}  ({why})")
    for n, raw in unsupported:
        print(f"ignored  line {n}: {raw}")
```

Output for the example file:

```text
$ python robots_check.py robots.txt Googlebot /shop/cart "/shop/catalog/shoes?sort=price" /docs/guide.pdf
blocked  /shop/cart  (line 2: Disallow: /shop/)
allowed  /shop/catalog/shoes?sort=price  (line 3: Allow: /shop/catalog/)
blocked  /docs/guide.pdf  (line 5: Disallow: /*.pdf$)
ignored  line 6: Crawl-delay: 10
```

Pass paths with their query string, exactly as they appear after the host. Put the script in CI with a list of URLs that must stay crawlable, and a bad deploy of robots.txt fails the build instead of quietly blocking a section.

## After the file is live

1. Open the robots.txt report and confirm the new version shows **Fetched** with no errors. Request a recrawl if the change is urgent.
2. Inspect one representative URL from each section you changed. "Crawl allowed? Yes" in URL Inspection is the confirmation from Google's side.
3. Remember what robots.txt can't do. A blocked page isn't crawled, so Google never sees a `noindex` on it, and the URL can still appear in results if other pages link to it. To keep a page out of the index, allow crawling and use `noindex`; you can confirm that the tag or header is actually served with the [noindex tag checker](https://en.speedyindex.com/noindex-tag-checker/).
4. Watch the Page indexing report over the following weeks. A rise in "Blocked by robots.txt" for URLs you meant to keep is the sign a rule is broader than intended.

## FAQ

**Is there still a robots.txt Tester in Search Console?**
No. Search Console now has the robots.txt report, which shows fetch status and parsing issues. To test a URL against rules, use URL Inspection for live URLs or an external tester for drafts.

**Which rule wins when Allow and Disallow both match?**
The one with the longer path. If both are the same length, Allow wins.

**Does Google respect crawl-delay?**
No. Google supports only user-agent, allow, disallow and sitemap.

**Are robots.txt paths case-sensitive?**
Yes. `/Private/` and `/private/` are different paths.

**How quickly does Google pick up a change?**
Google usually caches robots.txt for up to 24 hours. You can request a recrawl from the robots.txt report.

## Sources

- How Google interprets the robots.txt specification, Google Search Central: https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt
- robots.txt report, Search Console Help: https://support.google.com/webmasters/answer/6062598
- Google's robots.txt parser and matcher library: https://github.com/google/robotstxt
