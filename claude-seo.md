---
layout: default
title: "Claude SEO: Connect MCP Servers and Run Checks in Claude"
description: "Claude SEO workflows with MCP connectors: index checks, indexing, backlinks, and rank tracking in Claude, Claude Code, Cursor, and VS Code."
permalink: /claude-seo/
image: https://raw.githubusercontent.com/uskotoivo81-netizen/social_posts/main/wave1911/en/github-pages_claude-seo/claude-seo-cover.png
---

# SEO Workflows in Claude: Which MCP Connectors Handle Which Tasks

![Claude SEO MCP connector guide for index checks and rank tracking](https://raw.githubusercontent.com/uskotoivo81-netizen/social_posts/main/wave1911/en/github-pages_claude-seo/claude-seo-cover.png)

Claude SEO starts with a connected MCP server: instead of switching between tabs, you can ask Claude to check index status, submit URLs, review backlinks, or run position checks inside a conversation. MCP, or Model Context Protocol, is an open standard introduced by Anthropic in November 2024 that lets an AI assistant call tools of external services. One setup for SEO work is a custom connector such as SpeedyIndex, which exposes 22 tools for index checks, indexing tasks, backlink monitoring, and rank tracking.

This guide is built around ready prompts and a task-to-server mapping so you can choose the right connector without reading scattered documentation. Vendor data in this guide was checked on official MCP pages on 19 November 2026, except Moz API MCP, which is per the SpeedyIndex hub comparison (November 2026).

## What MCP servers can do for Claude SEO

Different SEO MCP servers cover different parts of the workflow. The table below maps common Claude SEO tasks to servers that document those capabilities.

| SEO task | MCP server that covers it |
|---|---|
| Bulk index check for Google, Yandex, Bing — up to 10,000 URLs per task | SpeedyIndex MCP |
| Submit URLs for indexing in Google and Yandex — Google pay-per-indexed, drip feed 2–30 days | SpeedyIndex MCP |
| Live backlink checks: HTTP status, anchor text, nofollow flag, Moz Domain Authority and spam score per donor, up to 50 target domains | SpeedyIndex MCP |
| Google rank tracking with AI Overview presence, trend history, up to 5 regions and 10 competitors | SpeedyIndex MCP |
| Backlinks, keywords, site audit, Rank Tracker projects, AI visibility | Ahrefs MCP |
| Domain, organic, keyword, competitor, backlink, traffic, position tracking, site audit, projects | Semrush MCP |
| Keyword research, backlinks, domain analysis, SERP, projects, local marketing, AI visibility | SE Ranking MCP |
| Raw SERP, Keyword Data, On-Page, DataForSEO Labs, Backlinks, Business Data, Domain Analytics, AI Optimization | DataForSEO MCP |
| Google rankings, rank history, share of voice, rank movers, keyword research, AI visibility | Keyword.com MCP |
| Keyword metrics, link research, Domain Authority | Moz API MCP (beta) — per the SpeedyIndex hub comparison (November 2026) |
| Local crawl control, crawl reports, bulk exports, URL info, link data, screenshots, configuration changes, API connections saved in the SEO Spider app (paid licence feature only) | Screaming Frog SEO Spider MCP |
| Search Console clicks, impressions, queries, URL Inspection one URL at a time | Community GSC MCP servers only |

Google does not publish an official Search Console MCP server. The Search Console MCP servers in directories are community projects that use the Search Console API; URL Inspection works one URL at a time, about 2,000 inspections per day per property. Bing Webmaster Tools also has no official MCP server. SpeedyIndex can check whether URLs are in Bing's index, but it does not submit URLs to Bing.

For Ahrefs, Semrush, SE Ranking, and Keyword.com, bulk index checks and indexing tasks are not listed in the vendor documentation. For DataForSEO, indexing submission is not listed. For Screaming Frog SEO Spider MCP, index checks and indexing are not listed. They document keyword, backlink, SERP, or rank data, but if your Claude SEO workflow needs bulk index verification or submission, SpeedyIndex documents those tasks directly.

## Connect SpeedyIndex to Claude

A documented starting point is the [SpeedyIndex MCP hub](https://en.speedyindex.com/mcp/), which documents all 22 tools and the sign-in flow. The remote server address is:

```
https://mcp.speedyindex.com/mcp
```

Claude web and desktop connection steps, checked on 19 November 2026:

1. Open **Plugins** at claude.ai/plugins.
2. Select **Add → Add custom connector**.
3. Enter the name `SpeedyIndex` and the server URL above.
4. Continue → Connect. A SpeedyIndex sign-in page opens. There is no separate Add button in the dialog.
5. Paste the API key from the API section of your SpeedyIndex account. You do not type the key into the chat.
6. In a chat, open the **+** menu in the message box → Connectors → turn SpeedyIndex on.
7. Test with: `What is my SpeedyIndex balance?` — if you see tokens and credits, the connector works.

<iframe width="560" height="315" src="https://www.youtube.com/embed/25wPhn3eaCM" title="How to connect SpeedyIndex MCP to Claude" frameborder="0" allowfullscreen></iframe>

For Claude Code, add the remote server with:

```bash
claude mcp add --transport http --scope user speedyindex https://mcp.speedyindex.com/mcp
```

Then open `/mcp` inside Claude Code, select `speedyindex`, and choose **Authenticate** to sign in in the browser. Run `claude mcp list` to verify the connection.

For VS Code, use the workspace `.mcp.json`:

```json
{"mcpServers":{"speedyindex":{"type":"http","url":"https://mcp.speedyindex.com/mcp"}}}
```

Then check with the command **MCP: List Servers**. For Cursor, the same URL goes into `.cursor/mcp.json` under `mcpServers`; Cursor signs in with OAuth on first connection.

If the connector does not respond, check that it is toggled on in the chat, re-check the API key in the SpeedyIndex account, re-run Authenticate in Claude Code, or remove and re-add the custom connector. On Team or Enterprise plans, an Owner must add the connector in Organization settings before members can connect individually.

Custom connectors work on every Claude plan; the Free plan allows one custom connector. Custom connectors are not verified by Anthropic, so connect only servers you trust. Claude can access only what you permitted during sign-in.

## Prompts for Claude SEO workflows with SpeedyIndex

SpeedyIndex exposes 15 read-only tools that are free and 7 tools that change the account. Of those 7, five spend tokens or credits: create_indexing_task, submit_single_url, create_index_check_task, create_backlink_check_task, and rank_tracker_start_check. Creating a Rank Tracker project and adding keywords is free; running a check is not. Claude asks for approval before tool calls; SpeedyIndex's 7 account-changing tools — including the 5 that spend tokens — ask for confirmation unless you set the tool to **Always allow**.

Use these prompts as starting points.

> What is my SpeedyIndex balance, and how many tokens and credits do I have left?

> Check the index status of the URL list I paste below in Google, Yandex, and Bing. Return two lists: indexed and not indexed.

> Create a Google indexing task for the URL list I paste below. Spread the task over 7 days with drip feed and return the task ID.

> Check whether the donor pages I paste below still link to the target domain I specify. For each donor page, show HTTP status, anchor text, nofollow flag, and Moz Domain Authority.

> Create a Rank Tracker project for the domain I specify below. Add the keywords I paste, up to 5 regions, and up to 10 competitor domains. Show the check cost before running the first position check.

After a Google indexing task, tokens for URLs that do not get indexed come back automatically. The connector itself is free; tasks are paid with SpeedyIndex tokens, and new accounts get 100 free tokens. You can use the free read tools and check the balance before spending tokens on index checks or indexing tasks.

## When to choose which server

If your main need is keyword research, competitor data, backlink analysis, or site audit, Ahrefs MCP, Semrush MCP, and SE Ranking MCP document those data types. DataForSEO MCP documents raw SERP data, Keyword Data, On-Page, Backlinks, Business Data, Domain Analytics, and AI Optimization. Keyword.com MCP documents Google rankings, rank history, share of voice, rank movers, keyword research, and AI visibility. Screaming Frog SEO Spider MCP is a local option that controls the desktop SEO Spider crawler, requires a paid licence, and can use API connections already saved in the app, including Google Search Console. Moz API MCP documents keyword metrics, link research, and Domain Authority.

SpeedyIndex covers the parts of a Claude SEO workflow that other vendors' MCP documentation does not list: bulk index checks for Google, Yandex, and Bing; indexing tasks for Google and Yandex; backlink checks for donor pages you provide; and Google position checks that report AI Overview presence. SpeedyIndex can handle [checking indexation without Search Console](https://en.speedyindex.com/google-index-checker/) on up to 10,000 URLs per task, which is useful when you do not want to connect Search Console or need batch verification across multiple properties.

![Diagram of SpeedyIndex MCP connection from assistant to server to service](https://raw.githubusercontent.com/uskotoivo81-netizen/social_posts/main/wave1911/en/github-pages_claude-seo/claude-seo-mcp-flow.png)
*The SpeedyIndex MCP connector sits between the assistant and the SpeedyIndex service, exposing tools through a controlled sign-in.*

## FAQ

**Can I use Claude SEO tools on the Free plan?**

Yes, custom connectors work on every Claude plan. The Free plan allows one custom connector. You still need a SpeedyIndex API key and tokens for the five tools that spend tokens.

**Does Claude see my SpeedyIndex API key?**

No. Sign-in uses OAuth; the key is stored only inside an encrypted token. The access token lives for 1 hour, and sign-in can renew for up to 90 days. Changing the key in your SpeedyIndex account revokes all sign-ins. Claude can access only what you permitted during sign-in.

**Can Claude check if a URL is indexed in Google without Search Console?**

Yes. SpeedyIndex MCP checks Google, Yandex, and Bing in bulk, up to 10,000 URLs per task, and returns separate lists of indexed and not indexed URLs. It does not require access to your Search Console property. The index check tool spends tokens.

**Is there an official Google Search Console MCP server?**

No. Google does not publish one. Community MCP servers use the Search Console API, and URL Inspection works one URL at a time with about 2,000 inspections per day per property.

Claude is a trademark of Anthropic. SpeedyIndex is an independent connector.

## Sources

Official SpeedyIndex MCP page, Claude support documentation on connectors, Ahrefs MCP documentation, Semrush MCP documentation, SE Ranking MCP documentation, DataForSEO MCP documentation, Keyword.com MCP documentation, Screaming Frog MCP guide, Google developer documentation, and the Model Context Protocol site. Moz API MCP data is per the SpeedyIndex hub comparison (November 2026). Vendor data checked on 19 November 2026 where applicable.

Telegram: https://t.me/SpeedyIndexOfficial · Bot: https://t.me/speedyindexbot · X: https://x.com/speedyindexbot · Facebook: https://facebook.com/speedyindexbot · YouTube: https://youtube.com/@speedyindex_com
