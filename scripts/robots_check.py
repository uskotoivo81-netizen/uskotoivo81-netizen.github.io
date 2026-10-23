#!/usr/bin/env python3
"""robots_check.py - test URLs against a robots.txt file using Google's matching rules.

Usage:
    python robots_check.py robots.txt Googlebot /path1 "/path2?q=1" ...

Rules implemented (Google Search Central, robots.txt specification):
  * one group per crawler: the group with the most specific matching user-agent,
    groups naming the same user-agent are merged, otherwise the * group;
  * the longest matching rule path wins;
  * on a tie between allow and disallow, allow (the least restrictive) wins;
  * '*' matches any sequence of characters, '$' anchors the end of the URL;
  * paths are case-sensitive, field names and user-agent values are not.
Unsupported lines (crawl-delay, host, ...) are reported and ignored.
"""
import re
import sys


def parse(text):
    groups, current, last_was_agent, unsupported = [], None, False, []
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
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
    agent = agent.lower()
    best_len, rules = -1, []
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
    best = None  # (length, is_allow, rule, line)
    for kind, path, line in rules:
        if kind == "disallow" and path == "":
            continue  # empty Disallow allows everything
        if to_regex(path).match(url_path):
            cand = (len(path), kind == "allow", f"{kind.capitalize()}: {path}", line)
            if best is None or cand[:2] > best[:2]:
                best = cand
    if best is None:
        return "allowed", "no matching rule"
    return ("allowed" if best[1] else "blocked"), f"line {best[3]}: {best[2]}"


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    text = open(sys.argv[1], encoding="utf-8").read()
    groups, unsupported = parse(text)
    rules = pick_rules(groups, sys.argv[2])
    for path in sys.argv[3:]:
        verdict, why = decide(rules, path)
        print(f"{verdict:8} {path}  ({why})")
    for n, raw in unsupported:
        print(f"ignored  line {n}: {raw}")


if __name__ == "__main__":
    main()
