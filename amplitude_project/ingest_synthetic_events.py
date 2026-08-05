#!/usr/bin/env python3
"""
ingest_synthetic_events.py
---------------------------
Sends the same illustrative WHOOP complaint-model data that powers dashboard.html
and the dbt/Looker projects into a REAL Amplitude project as actual events, using
Amplitude's HTTP Event Ingestion API (https://api2.amplitude.com/2/httpapi).

WHY THIS SCRIPT EXISTS
-----------------------
The Amplitude tracking plan for this project (8 events, 6 properties) was already
created live in your Amplitude project via the MCP connector. But Amplitude's query
engine only lets you build charts against properties/events that have actually been
INGESTED at least once -- the tracking-plan schema alone isn't enough. There is no
event-ingestion tool exposed through the MCP connector (for good reason -- it would
mean an AI agent could silently write arbitrary analytics data on your behalf).
So this script exists to be run BY YOU, with YOUR OWN API key, so the choice to
write data is explicit and in your hands.

Once you run this, every chart definition in chart_definitions.json will return
real data and can be saved + assembled into a live dashboard (ask me to do that
next, or build it yourself in the Amplitude UI).

WHAT IT SENDS (all synthetic, generated from data/*.json in this project --
same numbers already disclosed as "illustrative" in the dashboard/case study)
-----------------------------------------------------------------------------
1. "Review Submitted" events -- TOTAL_REVIEWS events distributed across the 9
   complaint categories by volume_share_pct, flagged has_churn_language by
   churn_language_share_pct, dated across Jan 2025-Jul 2026 weighted by the
   monthly_timeseries shape, and tagged with a platform.
2. Advanced Labs funnel events ("Waitlist Joined" -> "Test Invited" ->
   "Test Completed" -> "Results Reviewed") for WAITLIST_USERS synthetic users,
   attriting at each step per the illustrative 40% / 65% / 85% conversion
   assumptions in WHOOP_Healthcare_Product_Case_Study.docx. Multiply results
   by SCALE_FACTOR (default 1000) to map back to WHOOP's real reported
   350,000+ waitlist size -- this script uses a representative sample, not
   the literal member count.
3. "BPI Opt In" / "BPI Opt Out" / "Support Ticket Created" events, weighted
   to spike around the real Jul 2025 FDA warning letter and fade toward the
   Jun 2026 closeout, per bpi_healthcare_regulatory in monthly_timeseries.json.

USAGE
-----
    pip install requests
    export AMPLITUDE_API_KEY="<your project's API key>"   # Amplitude UI -> Settings -> Projects -> (this project) -> General
    python3 ingest_synthetic_events.py --dry-run     # prints a sample, sends nothing
    python3 ingest_synthetic_events.py --send        # actually POSTs to Amplitude

Get the API key from the SAME Amplitude project the tracking plan was created in
(project id 847885, org "restless-mode-123427") -- Amplitude Settings -> Projects.
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

AMPLITUDE_HTTPAPI_URL = "https://api2.amplitude.com/2/httpapi"
BATCH_SIZE = 50

TOTAL_REVIEWS = 1800          # representative sample size for "Review Submitted"
WAITLIST_USERS = 350          # 1/1000th of WHOOP's real 350,000+ waitlist (SCALE_FACTOR below)
SCALE_FACTOR = 1000

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PLATFORMS = ["iOS", "Android", "Trustpilot", "Reddit", "BBB"]
PLATFORM_WEIGHTS = [0.30, 0.20, 0.30, 0.15, 0.05]

# Maps each of the 9 complaint categories to the monthly_timeseries.json column
# that shapes its volume over time.
CATEGORY_TO_TIMESERIES_COL = {
    "subscription": "subscription_billing_support",
    "hardware": "hardware_reliability",
    "band_durability": "hardware_reliability",
    "app_experience": "app_experience",
    "bpi_fda": "bpi_healthcare_regulatory",
    "recovery_accuracy": "accuracy_metrics_blended",
    "strain_undercounting": "accuracy_metrics_blended",
    "hr_accuracy": "accuracy_metrics_blended",
    "sleep_accuracy": "accuracy_metrics_blended",
}


def load_json(name):
    with open(DATA_DIR / name) as f:
        return json.load(f)


def month_to_ts(month_str, day=None):
    """'2025-05' -> ms epoch timestamp for a (random, if day is None) day in that month."""
    year, mon = map(int, month_str.split("-"))
    if day is None:
        day = random.randint(1, 27)
    dt = datetime(year, mon, day, random.randint(0, 23), random.randint(0, 59), tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


def build_review_events():
    kpis = load_json("category_kpis.json")["categories"]
    timeseries = load_json("monthly_timeseries.json")
    events = []
    cat_weights = [c["volume_share_pct"] for c in kpis]

    for i in range(TOTAL_REVIEWS):
        cat = weighted_choice(kpis, cat_weights)
        col = CATEGORY_TO_TIMESERIES_COL[cat["id"]]
        month_weights = [row[col] for row in timeseries]
        month_row = weighted_choice(timeseries, month_weights)
        has_churn = random.random() * 100 < cat["churn_language_share_pct"]
        platform = weighted_choice(PLATFORMS, PLATFORM_WEIGHTS)
        star_rating = random.choice([1, 1, 2, 2, 3, 4, 5]) if has_churn else random.choice([2, 3, 4, 4, 5, 5, 5])

        events.append({
            "user_id": f"whoop_review_user_{i:05d}",
            "event_type": "Review Submitted",
            "time": month_to_ts(month_row["month"]),
            "event_properties": {
                "category": cat["id"],
                "platform": platform,
                "has_churn_language": has_churn,
                "severity_1_5": cat["severity_1_5"],
                "star_rating": star_rating,
            },
        })
    return events


def build_advanced_labs_funnel_events():
    events = []
    # Waitlist opened with the Advanced Labs announcement (~May 2025), first
    # cohort of test invites started after the Sept 30 2025 launch.
    waitlist_start = datetime(2025, 5, 15, tzinfo=timezone.utc)
    waitlist_end = datetime(2026, 6, 30, tzinfo=timezone.utc)
    span_days = (waitlist_end - waitlist_start).days

    for i in range(WAITLIST_USERS):
        user_id = f"whoop_labs_user_{i:05d}"
        join_dt = waitlist_start + timedelta(days=random.randint(0, span_days))
        events.append({
            "user_id": user_id, "event_type": "Waitlist Joined",
            "time": int(join_dt.timestamp() * 1000),
        })
        if random.random() < 0.40:  # invited & test booked
            invite_dt = join_dt + timedelta(days=random.randint(14, 90))
            events.append({"user_id": user_id, "event_type": "Test Invited", "time": int(invite_dt.timestamp() * 1000)})
            if random.random() < 0.65:  # test completed
                complete_dt = invite_dt + timedelta(days=random.randint(3, 21))
                events.append({"user_id": user_id, "event_type": "Test Completed", "time": int(complete_dt.timestamp() * 1000)})
                if random.random() < 0.85:  # results reviewed in-app
                    review_dt = complete_dt + timedelta(days=random.randint(1, 10))
                    events.append({"user_id": user_id, "event_type": "Results Reviewed", "time": int(review_dt.timestamp() * 1000)})
    return events


def build_bpi_trust_events():
    timeseries = load_json("monthly_timeseries.json")
    events = []
    uid_counter = 0
    for row in timeseries:
        weight = row["bpi_healthcare_regulatory"]
        n_this_month = max(0, int(weight * 1.5))
        for _ in range(n_this_month):
            uid_counter += 1
            user_id = f"whoop_bpi_user_{uid_counter:05d}"
            ts = month_to_ts(row["month"])
            # opt-out rate and ticket volume both track the same monthly weight,
            # i.e. they spike with the Jul 2025 FDA letter and fade after the
            # Jun 2026 closeout -- see WHOOP_Healthcare_Product_Case_Study.docx.
            if random.random() < 0.75:
                events.append({"user_id": user_id, "event_type": "BPI Opt In", "time": ts})
            else:
                events.append({"user_id": user_id, "event_type": "BPI Opt Out", "time": ts})
            if random.random() < 0.35:
                events.append({
                    "user_id": user_id, "event_type": "Support Ticket Created",
                    "time": ts + 3600_000,
                    "event_properties": {"ticket_category": "bpi_accuracy_confusion"},
                })
    return events


def send_batch(api_key, events, dry_run):
    payload = {"api_key": api_key, "events": events}
    if dry_run:
        print(json.dumps(payload, indent=2)[:2000])
        print(f"... ({len(events)} events in this batch, dry run -- nothing sent)")
        return
    resp = requests.post(AMPLITUDE_HTTPAPI_URL, json=payload, timeout=30)
    if resp.status_code != 200:
        print(f"  ! batch failed ({resp.status_code}): {resp.text[:300]}", file=sys.stderr)
    else:
        print(f"  ok: {len(events)} events accepted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="Actually POST events to Amplitude.")
    parser.add_argument("--dry-run", action="store_true", help="Print sample payloads, send nothing (default).")
    args = parser.parse_args()
    dry_run = not args.send

    if args.send:
        api_key = os.environ.get("AMPLITUDE_API_KEY")
        if not api_key:
            print("Set AMPLITUDE_API_KEY first: export AMPLITUDE_API_KEY=...", file=sys.stderr)
            sys.exit(1)
    else:
        api_key = "DRY_RUN_NO_KEY_NEEDED"

    print("Building synthetic events from data/*.json ...")
    all_events = (
        build_review_events()
        + build_advanced_labs_funnel_events()
        + build_bpi_trust_events()
    )
    random.shuffle(all_events)
    print(f"Total events to send: {len(all_events)}")
    print(f"  Reviews: {TOTAL_REVIEWS} | Waitlist users: {WAITLIST_USERS} (x{SCALE_FACTOR} = real scale) | BPI/trust events: derived from monthly weights")

    if dry_run:
        print("\n--dry-run mode (default): showing a sample batch only, sending NOTHING.\n")
        send_batch(api_key, all_events[:5], dry_run=True)
        print(f"\nRun with --send once AMPLITUDE_API_KEY is set to actually ingest all {len(all_events)} events.")
        return

    for i in range(0, len(all_events), BATCH_SIZE):
        batch = all_events[i:i + BATCH_SIZE]
        print(f"Sending batch {i // BATCH_SIZE + 1} ({len(batch)} events)...")
        send_batch(api_key, batch, dry_run=False)
        time.sleep(0.2)  # be polite to the API

    print("\nDone. Give Amplitude a minute or two to index, then charts in chart_definitions.json will be queryable.")


if __name__ == "__main__":
    main()
