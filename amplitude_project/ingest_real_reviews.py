#!/usr/bin/env python3
"""
ingest_real_reviews.py
-----------------------
Sends the 152 REAL reviews in real_reviews_collected.json into Amplitude as
real events -- no random generation, no synthetic sampling. Every event here
maps 1:1 to an actual, individually-verifiable review or comment: 10 App
Store + 3 Google Play (collected by fetching apps.apple.com / play.google.com
directly), 40 Trustpilot, and 99 Reddit (both user-collected by hand, since
those sources are blocked/unreachable to this environment's own fetch tools).

This is deliberately separate from ingest_synthetic_events.py. Both write to
the same "Review Submitted" event, but every event from THIS script carries
event_properties.data_source = "real_appstore" / "real_googleplay" /
"real_trustpilot" / "real_reddit" (never "synthetic"), so you can build an
Amplitude chart filtered to data_source != synthetic and see ONLY real data,
cleanly separated from the earlier illustrative/synthetic exploration.

152 reviews, ~205 category-tagged events, is a real but still modest sample
-- treat percentages computed from it as directionally real, not as a
scientifically representative population statistic (especially since ~65%
of it is Reddit, which skews toward subscription/cancellation content by
construction -- see README.md's caveat section).

DATE HANDLING (v2 -- important, read this):
This project's Starter plan only retains/queries events from the trailing
365 days. The reviews' TRUE dates range from 2021 to 2026, so most of them
(104 of 152, including all 99 Reddit entries) fall outside that window and
were silently un-queryable when a first version of this script sent events
timestamped with their real review date. Fix: this version omits "time"
entirely, so Amplitude timestamps every event at receipt (now) instead --
that's the only way to make them queryable at all under this plan. The true
original date is NOT discarded: it's preserved on every event as the
`review_date_real` property, and is still the authoritative date in
real_reviews_collected.json. This means Amplitude's own time-series /
monthly-trend view over these events is meaningless (everything lands on
today) -- don't build one. Category-level aggregates (volume by category,
churn-language share) are unaffected, since they don't depend on the time
distribution.

Every event also carries `ingest_batch: "real_v2"` so charts can filter to
this clean, complete, non-duplicated batch and ignore the small number of
real events a first (date-broken) send already put in this project.

USAGE
-----
    export AMPLITUDE_API_KEY="<your project's API key>"   # same key as before
    python3 ingest_real_reviews.py --dry-run
    python3 ingest_real_reviews.py --send
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

AMPLITUDE_HTTPAPI_URL = "https://api2.amplitude.com/2/httpapi"
DATA_FILE = Path(__file__).resolve().parent / "real_reviews_collected.json"


def build_events():
    payload = json.loads(DATA_FILE.read_text())
    events = []
    for r in payload["reviews"]:
        data_source = {
            "iOS": "real_appstore",
            "Android": "real_googleplay",
            "Trustpilot": "real_trustpilot",
            "Reddit": "real_reddit",
        }.get(r["platform"], "real_other")
        # one event per category the review touches on -- a review can
        # legitimately belong to more than one theme (e.g. mentions both
        # hardware AND subscription), same as the dbt model's approach.
        if not r["categories"]:
            continue  # e.g. real_025: real review, but off-topic / no product category applies
        for category in r["categories"]:
            props = {
                "category": category,
                "platform": r["platform"],
                "has_churn_language": r["has_churn_language"],
                "data_source": data_source,
                "reviewer_handle": r["author"],
                "review_date_real": r["date"],
                "ingest_batch": "real_v2",
            }
            if r.get("star_rating") is not None:
                props["star_rating"] = r["star_rating"]
            if r.get("helpful_count") is not None:
                props["helpful_count"] = r["helpful_count"]
            events.append({
                "user_id": f"real_reviewer_{r['id']}",
                "event_type": "Review Submitted",
                # no "time" key -- Amplitude timestamps at receipt (now).
                # See DATE HANDLING note above for why.
                "insert_id": f"{r['id']}_{category}_v2",
                "event_properties": props,
            })
    return events


def send(api_key, events, dry_run):
    payload = {"api_key": api_key, "events": events}
    if dry_run:
        print(json.dumps(payload, indent=2))
        print(f"\n({len(events)} events total -- dry run, nothing sent)")
        return
    resp = requests.post(AMPLITUDE_HTTPAPI_URL, json=payload, timeout=30)
    if resp.status_code != 200:
        print(f"! failed ({resp.status_code}): {resp.text[:300]}", file=sys.stderr)
    else:
        print(f"ok: {len(events)} real-review events accepted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dry_run = not args.send

    events = build_events()
    n_reviews = len(json.loads(DATA_FILE.read_text())["reviews"])
    print(f"Built {len(events)} events from {n_reviews} real reviews (some reviews touch multiple categories).")

    if dry_run:
        send("DRY_RUN", events[:3], dry_run=True)
        print(f"\nRun with --send (AMPLITUDE_API_KEY set) to actually ingest all {len(events)} events.")
        return

    api_key = os.environ.get("AMPLITUDE_API_KEY")
    if not api_key:
        print("Set AMPLITUDE_API_KEY first: export AMPLITUDE_API_KEY=...", file=sys.stderr)
        sys.exit(1)

    send(api_key, events, dry_run=False)
    time.sleep(0.2)
    print("\nDone. Filter Amplitude charts on ingest_batch=real_v2 (and/or data_source starting with real_) to see only this clean, queryable, real-data batch.")


if __name__ == "__main__":
    main()
