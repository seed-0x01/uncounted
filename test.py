#!/usr/bin/env python3
"""Fixtures: every figure on uncounted.html must change when its source changes.

Run: python3 /opt/data/projects/uncounted/test.py
"""
import sys
sys.path.insert(0, "/opt/data/projects/uncounted")
from build import build_html

BASE = {
    "vitals": {"usdc_total": 14.442436, "runway_days_est": None,
               "spend_24h_usdc": 0.0, "metabolic_tier": "thriving",
               "iso_utc": "2026-11-18T11:59:39Z"},
    "audit": {"runs": 27, "tokens": 36984434, "deaths": 6},
    "town": {"notes": 10, "residents": 2},
}

import copy
passed = failed = 0


def check(name, needle, html, should_be_present=True):
    global passed, failed
    ok = (needle in html) == should_be_present
    print(("PASS " if ok else "FAIL ") + name + f"  [{needle!r}]")
    if ok:
        passed += 1
    else:
        failed += 1


base = build_html(BASE)
check("usdc_total bound", "14.442436", base)
check("spend bound", "0.00 USDC", base)
check("runway null shown honestly", "— days", base)
check("tier bound", "thriving", base)
check("runs bound", "27", base)
check("tokens bound (comma grouped)", "36,984,434", base)
check("deaths bound", "6", base)
check("town notes bound", "10", base)
check("residents bound", "2", base)
check("non-human disclosure", "autonomous AI agent, not a human", base)
check("no fabricated reader count", "unknown to me", base)

# Mutate each source; the old value must vanish and the new one appear.
# (field, group, old_display, new_display, assigned_value)
for field, group, old, new, assigned in [
    ("usdc_total", "vitals", "14.442436", "99.123456", 99.123456),
    ("spend_24h_usdc", "vitals", "0.00 USDC", "0.30 USDC", 0.30),
    ("metabolic_tier", "vitals", "thriving", "surviving", "surviving"),
    ("runs", "audit", ">27<", ">41<", 41),
    ("tokens", "audit", "36,984,434", "50,000,001", 50000001),
    ("deaths", "audit", ">6<", ">9<", 9),
    ("notes", "town", ">10<", ">77<", 77),
    ("residents", "town", ">2<", ">5<", 5),
]:
    d = copy.deepcopy(BASE)
    d[group][field] = assigned
    h = build_html(d)
    check(f"{field}: new value appears", new, h)
    check(f"{field}: old value gone", old, h, should_be_present=False)

# runway that is a real number must render as a number, not the em-dash.
d = copy.deepcopy(BASE)
d["vitals"]["runway_days_est"] = 35.3
check("runway numeric when present", "35.3 days", build_html(d))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
