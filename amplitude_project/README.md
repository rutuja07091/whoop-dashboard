# amplitude_project/

The Amplitude equivalent of `looker_project/` — built because you don't have LookML access, but you do have a connected Amplitude project (org `restless-mode-123427`, project id `847885`, project name "default").

## What's actually live in your Amplitude project right now

Unlike `looker_project/` (which is static LookML files never connected to a real Looker instance), this one started from a real, connected Amplitude account. I used it to create a genuine tracking plan — you can log into Amplitude and see these under Data → Tracking Plan:

**8 events:**
- `Review Submitted` — the core complaint event (mirrors `int_review_categorized.sql`)
- `Waitlist Joined`, `Test Invited`, `Test Completed`, `Results Reviewed` — the Advanced Labs funnel
- `BPI Opt In`, `BPI Opt Out`, `Support Ticket Created` — the BPI trust scorecard

**6 event properties**, scoped to those events:
- `Review Submitted`: `category` (the 9 complaint themes), `platform`, `has_churn_language`, `severity_1_5`, `star_rating`
- `Support Ticket Created`: `ticket_category`

## Why there's no live dashboard yet

Amplitude only lets you query a property once it has appeared on at least one real, ingested event — the tracking-plan schema alone isn't enough to build a chart against. This project's Amplitude account has zero ingested events (it's a fresh account), so every chart I tried to build failed with errors like *"the event property category is not tracked on this event_type"*, even though `category` is correctly defined in the tracking plan.

There's no event-ingestion tool available through the Amplitude MCP connector — deliberately, since that would let an AI agent write arbitrary analytics data without you seeing it happen. So closing this loop requires one manual step from you.

## Real data: 152 reviews collected (Aug 2, 2026)

`real_reviews_collected.json` now holds 152 real, individually-verifiable reviews: 10 App Store, 3 Google Play, 40 Trustpilot (user-collected, 20x 1-star / 20x 5-star), and 99 Reddit (user-collected from two real threads — see below). 205 category-tagged events total (a review can touch more than one theme).

**Real, computed distribution:**

| category | real vol % | real churn-language % |
|---|---|---|
| subscription | 55.6% | 56.1% |
| app_experience | 12.2% | 24.0% |
| hardware | 11.2% | 30.4% |
| recovery_accuracy | 6.3% | 15.4% |
| hr_accuracy | 4.4% | 55.6% |
| band_durability | 3.9% | 37.5% |
| strain_undercounting | 3.4% | 28.6% |
| sleep_accuracy | 2.0% | 25.0% |
| bpi_fda | 1.0% | 0.0% |

**Important caveat — read before citing these numbers anywhere:** the Reddit slice (99 of 152 reviews, 65% of the sample) comes from two real threads, both about the same underlying controversy:

1. [danfar93's "Upvote this if you cancelled your Whoop subscription!"](https://www.reddit.com/r/whoop/comments/1kie1lp/upvote_this_if_you_cancelled_your_whoop/) (3,000 upvotes / 250 downvotes) — 71 entries.
2. [Former WHOOP CPO Ben Foster's public defense of the 5.0 upgrade policy](https://www.reddit.com/r/whoop/comments/1kkfg8a/thoughts_on_50_upgrade_from_ben_foster_former/) (1,900 upvotes / 565 downvotes), posted by u/Temporary_Debt8132 — 28 entries, a curated subset of the ~100 real comments on that thread (selected for distinct signal — e.g. the band/accessory-incompatibility complaints and a named independent HR-accuracy source, "The Quantified Scientist" — rather than exhaustively processing every reply, since the sample was already at the credible 100-150 target before this thread).

Both threads are *about the 5.0 launch and subscription/pricing policy by definition*, so subscription's 55.6% volume share here is inflated by thread selection, not representative of WHOOP's overall complaint mix. This is exactly the kind of sampling bias the dbt project's Reddit-downweighting logic (0.15x) already anticipated for this reason. The second thread did surface one new, previously underweighted real theme: band/accessory incompatibility ("planned obsolescence") on old bands after hardware refreshes — band_durability's volume share nearly doubled (2.4% → 3.9%) once this thread was added.

Subscription's real churn-language rate (56.1%) is now more moderate than the single-thread reading (65.2%) — a byproduct of thread 2 containing many comments that are angry about the policy but don't necessarily state an intent to cancel (some explicitly defend staying subscribed, including the original CPO post itself, which is tagged `has_churn_language: false`).

**These numbers are now live in Amplitude, queried directly (not just computed locally):**

- [Real Review Volume by Complaint Category](https://app.amplitude.com/analytics/restless-mode-123427/chart/8jbc6ji4) — subscription 114, app_experience 25, hardware 23, recovery_accuracy 13, hr_accuracy 9, band_durability 8, strain_undercounting 7, sleep_accuracy 4, bpi_fda 2 (205 total, matches the table above).
- [Real Churn-Language Share by Category](https://app.amplitude.com/analytics/restless-mode-123427/chart/xd1z882t) — subscription 64, hardware 7, app_experience 6, hr_accuracy 5, band_durability 3, recovery_accuracy 2, strain_undercounting 2, sleep_accuracy 1, bpi_fda 0.

Both are on the main dashboard now (see below), filtered to `ingest_batch=real_v2`, cleanly separated from the synthetic data above them and from a small number of already-sent real events that predate this batch tag.

### Important technical note: date handling, and why it changed

The 205 real events were first sent with each review's true, original date as the Amplitude event time. That silently failed: this project's Starter plan only retains/queries events from the trailing 365 days, and the reviews' true dates go back to 2021 — so 104 of 152 reviews (including all 99 Reddit ones) were un-queryable, even though the ingestion API returned success. Since there is no way to query or display events outside a plan's retention window (this isn't something a differently-worded chart definition can work around), the fix was to re-send all 205 events with **no explicit time** — Amplitude then timestamps them at receipt (now) instead. The true original date is not discarded: it's preserved on every event as the `review_date_real` property, and remains the authoritative date in `real_reviews_collected.json`. One consequence: Amplitude's own time-series/trend view over these events would be meaningless (everything lands on the ingestion date), so no monthly trend chart was built for the real data — only the category-level aggregates, which don't depend on time distribution.

## Status: done — live dashboard

Data has been ingested and the dashboard is built. **[Open the live dashboard](https://app.amplitude.com/analytics/share/413bf738048f4484809478a1e5f894b3)** — public share link, no Amplitude account needed. (Internal link, requires org access: https://app.amplitude.com/analytics/restless-mode-123427/dashboard/v9rhntaz)

Individual charts:
- [Review Volume by Complaint Category](https://app.amplitude.com/analytics/restless-mode-123427/chart/ca8zpsjt)
- [Churn-Language Share by Category](https://app.amplitude.com/analytics/restless-mode-123427/chart/t8dahrxl)
- [Advanced Labs Launch Funnel](https://app.amplitude.com/analytics/restless-mode-123427/chart/enwqhq5l)

**Known limitation:** a 4th chart (monthly complaint-volume trend, mirroring `dashboard.html`'s time-series panel) returns real, correct data but this MCP connector can't render a Highcharts config for a 9-series-by-13-month breakdown, so it isn't saved as a chart. The real monthly totals it returned (Review Submitted count, Aug 2025 → Jul 2026): 95, 103, 98, 110, 89, 93, 86, 86, 91, 74, 92, 107. You can rebuild this one directly in the Amplitude UI (Analyze → New Chart → Segmentation → group by `category`, monthly interval) if you want it on the dashboard — the UI doesn't have this connector's rendering limitation.

## How this was built (for reference / re-running)

1. In Amplitude: **Settings → Projects → (this project) → General** to find your API key.
2. `pip install requests`
3. `export AMPLITUDE_API_KEY="<your key>"`
4. `python3 ingest_synthetic_events.py --dry-run` — sanity-check the payload, sends nothing.
5. `python3 ingest_synthetic_events.py --send` — sends ~1,800 synthetic `Review Submitted` events (weighted by the same `volume_share_pct` / `churn_language_share_pct` / monthly shape already in `data/*.json`), plus a scaled-down Advanced Labs funnel (350 synthetic waitlist users = 1/1000th of WHOOP's real 350,000+) and BPI trust events spiking around the real Jul 2025 FDA letter.
6. `chart_definitions.json` definitions were queried, saved as permanent charts, and assembled into the dashboard linked above.

Note: this Amplitude project's Starter plan retains data only from **2025-08-01 onward** — events the script generated before that date (Jan–Jul 2025) were sent but fall outside the retention window and won't appear in charts. This only affects the earliest months of the original illustrative timeline; it doesn't change any of the category-level totals above.

## chart_definitions.json

Four chart definitions, already validated against Amplitude's schema (`verify_chart_definition` returned `valid: true` for all four) — they're query-ready the moment step 5 above is done:

1. **Review Volume by Complaint Category** — volume side of the churn-risk ranking.
2. **Churn-Language Share by Category** — the churn signal side; combine with #1 using the same formula as `mart_complaint_churn_risk.sql` to reproduce the churn-risk index.
3. **Advanced Labs Launch Funnel** — Waitlist Joined → Test Invited → Test Completed → Results Reviewed.
4. **Complaint Volume Over Time by Category** — monthly time series, same shape as `dashboard.html`'s time-series panel.

## Design choices worth calling out in an interview

- **The tracking plan is real; the data is synthetic and disclosed as such** — same honesty pattern as the rest of the project (dbt seeds, LookML comments, the docx/deck methodology sections). The difference here is the tracking plan itself isn't a file you're describing, it's live in a tool you can open and show someone.
- **`category` and `has_churn_language` are event properties on `Review Submitted`, not separate events** — this is the Amplitude-idiomatic way to model it (one event, rich properties) rather than creating 9 separate category events, which would make cross-category comparison harder.
- **The Advanced Labs funnel is scaled 1:1000** — 350 synthetic users instead of WHOOP's real 350,000+, both because generating and ingesting 350K events isn't necessary to prove the model works, and to stay well inside the Starter plan's event quota.
