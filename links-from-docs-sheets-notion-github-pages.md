---
layout: page
title: "Do links from Google Docs, Sheets, Notion and GitHub Pages get indexed?"
description: "Do links from Google Docs, Sheets, Notion and GitHub Pages get indexed? In our sample the host page and the outbound href are two checks, not one."
permalink: /links-from-docs-sheets-notion-github-pages/
---

# Host page versus outbound href on document platforms

Do links from Google Docs, Sheets, Notion and GitHub Pages get indexed is two questions wearing one sentence. The first is whether Google holds the public URL of the document host itself. The second is whether an outbound `href` on that host is a path the crawler can use. Mixing them produces a false "the link is live, so the target is in the index" story. In our sample they are logged as separate columns.

A person with the URL can open a Docs file, a Sheet, a Notion page or a GitHub Pages URL. That is access. Access is not a search listing. Google's own [privacy help for Docs, Sheets and Slides](https://support.google.com/docs/answer/10381817?hl=en) draws the same line for one sharing mode: "Anyone with the link" is not crawled or listed unless that exact URL is posted on a public, crawlable page. Publish to the web is a different control: it creates a public URL or an embed. The publish article does not say Google will index that URL. This hub does not fill that silence with a rate.

## What was journaled

Each row is a public host URL older than 14 days on 9 November 2026. Hosts in the journal:

| Host | URL shape in the journal | What "public" meant here |
|---|---|---|
| Notion | Published site URL, not a workspace share dialog | Page opened via Share → Publish, not only "anyone with the link" |
| GitHub Pages | `username.github.io` (or project path) | HTML the author publishes; `rel` is whatever that HTML contains |
| GitHub Gist | Public gist HTML | Renderer-controlled markup; outbound `rel` is read from the live page |
| Google Sites | Published site URL | Public site, not a restricted Workspace file |
| Telegraph | `telegra.ph` page | Public note URL |
| HackMD | Published note URL | The published document, not the unpublished draft |

Docs and Sheets join this question only when the file has a public URL worth journaling. "Anyone with the link" is not that URL. A `/pub` or `/pubhtml` address from Publish to web is public. It still is not a stored listing.

Sample size: 44 URLs. Age filter: older than 14 days on 9 November 2026. After the journal was frozen, each host URL went through a bulk index check on the same day.

**Important limit of this sample:** every one of the 44 URLs had also been submitted by us to an indexing service before the check. This is a "published and submitted" sample, not a measure of how pages behave when they are left for Google to find on its own.

Results for that sample:

| Host | URLs checked | In the Google index |
|---|---|---|
| GitHub Pages | 6 | 6 |
| GitHub Gist | 7 | 7 |
| HackMD | 6 | 6 |
| Google Sites | 12 | 11 |
| Notion | 7 | 5 |
| Telegraph | 6 | 4 |
| **Total** | **44** | **39** |

Read the table as "in our sample...", not as a platform-wide conversion rate. A different age cut, a different mix of thin pages, a different submission history or a later date can move every cell. Docs and Sheets are not rows in this table: no file of those two types was in the journal.

## Host in the index is not the href

Three failures hide under one complaint.

**The host was never a public crawlable page.** A Docs file set to "Anyone with the link" can be opened by anyone who already has the string. Google's privacy article states that search engines do not crawl or index that file unless the link is posted on a public crawlable page. Pasting the same string into Slack or an email thread does not create that page. Posting it on a public blog, a forum, or another indexed HTML document can.

**The host is public and still absent from the index column.** Publish to the web produces a URL a stranger can load. That is the condition for a crawl, not a listing. Notion's publish settings include a search-engine indexing toggle; GitHub Pages can ship `noindex`; a HackMD draft can sit behind `noindex, nofollow` until it is actually published. The sample records the live URL, not the author's intent.

**The host is in the index column, and the outbound `href` still does nothing useful.** The crawler has to see a real `<a href>` in HTML it can fetch. A comment, a citation chip, or a script-only button is not that tag. Qualifying `rel` values (`nofollow`, `ugc`, `sponsored`) are hints: Google says such links are generally not followed, and the target may still be found some other way. In our sample, `rel` is a separate table, not a synonym for "not indexed".

Before any index column is trusted, [confirm the href is actually on the page](https://en.speedyindex.com/backlink-checker/). A "went live" report is not a parse of the HTML. If the anchor is missing, qualified in a way the sample cares about, or pointing at a redirect, the index row is answering a different URL.

## How the sample was built

1. Write down the public URL of the host, copied from the address bar of the published view, not from an editor or a share modal.
2. Open the published HTML. Find the outbound `<a href>` to the target. If it is not in the source the crawler would get, stop. Do not journal a screenshot of the editor.
3. Keep the row only if that host URL is older than 14 days on 9 November 2026. Newer URLs are not "too early"; they are out of this sample.
4. Run a bulk index check on the frozen list of host URLs (44).
5. On the same HTML, record outbound `rel` values for the target `href`. That harvest is the table in the next section.
6. Optionally check the target URL as its own row. Do not collapse host and target into one percentage.

The 14-day floor is a filter for this journal, not a calendar Google published. It only answers "these URLs had time to be found if they were going to show in this slice". It does not say when a new page will appear.

## Outbound `rel` in the same HTML

The `rel` harvest covers 12 of the 44 pages: two per host, opened in a browser on 9 November 2026. It is a smaller sample than the index check.

| Host | Pages read | `rel` on the outbound link to the target |
|---|---|---|
| GitHub Pages | 2 | none |
| Google Sites | 2 | none |
| Telegraph | 2 | none on body links (the author byline link carries `rel="author"`) |
| Notion | 2 | not collected |
| HackMD | 2 | not collected |
| GitHub Gist | 2 | not collected |

"Not collected" means we did not get a reliable reading of the links from the rendered page. It does not mean the `rel` is empty.

On GitHub Pages the HTML is the author's: empty `rel` is possible and is still not a ranking claim. On a gist, GitHub's renderer owns the markup. Notion, Telegraph, HackMD and Google Sites each have their own templates. The table is an observation of 9 November 2026, not a lifetime policy.

Google treats `nofollow`, `ugc` and `sponsored` as hints: generally not followed; the target may still be found from a sitemap or another site. In our sample, a `nofollow` edge would be "not a follow path in this HTML", not "this target cannot be in Google".

## Docs, Sheets, Notion, GitHub Pages: four different doors

**Google Docs and Sheets.** Restricted is the default. "Anyone with the link" is a capability URL, not a listing. Publish to the web mints `/pub` or `/pubhtml` (and an embed). Stop publishing removes that public view. Workspace admins can disable publish. None of those switches is an index report. If the outbound link lives only inside the editor and never in the published HTML, there is no host page to journal.

**Notion.** Share → Publish is not the same as "anyone with the link" in the Share tab. The indexing toggle is a Notion setting that allows search engines to consider the published page. It does not replace a crawl.

**GitHub Pages.** The site is ordinary public HTML on `github.io` (or a custom domain). `robots.txt` and `meta robots` behave like any other static host you own. Outbound `rel` is yours. A thin page whose only job is a list of promotional links is still a page Google can ignore for quality reasons; this hub does not score that.

**Gist, Google Sites, Telegraph, HackMD.** They are in the journal because they are common places people paste a URL and then ask why Google does not list the target. Each row still splits: is the note itself in the index column, and what `rel` sits on the outbound tag.

## What to do with a list of such links

- Drop editor URLs, share-dialog URLs, and "anyone with the link" Docs/Sheets files that were never published to the web and never placed on a public crawlable page.
- Keep published host URLs that actually contain the `href`.
- Record `rel` from the live HTML, not from memory of the platform's reputation.
- Check the host and the target as two lists. A target can be in Google with no help from this host. A host can be in Google with a `nofollow` edge that is not a follow path.
- After the HTML is honest, further work on lists that are already crawlable is a [SpeedyIndex](https://en.speedyindex.com/) problem of discovery and status, not a problem of inventing a platform-wide index rate.

Do not treat a green "published" badge as a search listing. Do not treat a `nofollow` hint as proof the target is unreachable. Do not average our sample into a forecast for next week's URLs.

## FAQ

### If a Doc is "Anyone with the link", will Google list it?

Not from that setting alone. Google's privacy help says search engines do not crawl or index it unless that link is posted on a public crawlable page.

### Does Publish to the web mean the Doc is in Google?

It means there is a public URL or embed. The publish article does not say Google will index it. In our sample, published URLs are hosts to check, not a guaranteed column of "yes".

### If GitHub Pages has no `rel`, is the outbound link a follow path?

The live tag has no qualifying `rel` in that HTML. Google's hint model applies only when `nofollow` / `ugc` / `sponsored` are present. Absence of `rel` is not a ranking promise for the target.

### Why journal pages older than 14 days?

So this slice is not a pile of URLs published yesterday. It is an age filter for 9 November 2026, not a published Google SLA.

Telegram: https://t.me/SpeedyIndexOfficial · Bot: https://t.me/speedyindexbot · X: https://x.com/speedyindexbot · Facebook: https://facebook.com/speedyindexbot · YouTube: https://youtube.com/@speedyindex_com
