# WHOOP: Ranking Complaint Themes by Churn & Revenue Exposure

Most complaint dashboards rank by volume. This one ranks by churn risk instead — because the complaint everyone talks about and the complaint that actually makes someone cancel aren't always the same thing.

**[Live dashboard](https://rutuja07091.github.io/whoop-dashboard/dashboard.html)** — full churn-risk ranking, volume-vs-intent quadrant, trends over time, platform split, revenue exposure by team, and sourced complaint evidence, all in one view.

**[Live Amplitude dashboard](https://app.amplitude.com/analytics/share/413bf738048f4484809478a1e5f894b3)** (public link, no login needed) — the same real, category-tagged review data queried directly out of Amplitude.

## The finding

152 real reviews were hand-collected across the App Store, Google Play, Trustpilot, and Reddit, then individually tagged by complaint theme and by whether the review contains explicit cancel/switch/refund language ("churn language"). Ranking by volume alone puts accuracy and hardware complaints on top. Ranking by churn-language share tells a different story: subscription and pricing complaints are the ones most likely to cost WHOOP a member, even though they don't dominate the raw complaint count.

| category | real volume share | real churn-language share |
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

**Read this with one caveat in mind:** 65% of the sample comes from two Reddit threads, both about the 5.0 launch and subscription/pricing policy so subscription's share here is inflated by thread selection, not necessarily representative of WHOOP's overall complaint mix. `amplitude_project/README.md` covers this in full, including exactly which threads, how they were weighted, and how the dbt model's Reddit-downweighting logic anticipates this bias.

## What's in this repo

```
dashboard.html          the full interactive dashboard (churn-risk ranking, trends, funnel, evidence)
case_studies/            two written case studies as PDFs
  WHOOP_Product_Analyst_Case_Study.pdf       the core churn-risk analysis, methodology, and recommendations
  WHOOP_Healthcare_Product_Case_Study.pdf    a deep-dive on the Advanced Labs launch funnel and BPI trust signal
deck/
  WHOOP_Product_Analyst_ppt.pdf              slide summary of the analysis and recommendations
dbt_project/             the modeling logic as it would run on a real warehouse (Snowflake + dbt)
amplitude_project/       the real data collection + ingestion pipeline behind the live numbers
data/                    underlying JSON/CSV data behind the dashboard's charts
```

## Methodology, briefly

Two parallel tracks feed this project, and both are labeled honestly throughout:

- **`dbt_project/`** is illustrative scaffolding; it shows exactly how the churn-risk model (category tagging, churn-language detection, Reddit downweighting, revenue-at-risk scoring) would be built on WHOOP's real warehouse, but it isn't connected to one.
- **`amplitude_project/`** is real. 152 individually verifiable reviews were collected by hand, tagged the same way the dbt model tags them, and ingested as real events into Amplitude, which is what the live dashboard numbers above are actually querying.

Full writeups, including data sources, sample-size caveats, and design decisions worth digging into, are in `dbt_project/README.md` and `amplitude_project/README.md`.

## About this project

Built by Rutuja Hande out of genuine interest in how WHOOP's product and analytics teams think about churn risk not assigned, not required, just a question that seemed worth actually answering instead of guessing at.

[rutujahande09@gmail.com](mailto:rutujahande09@gmail.com)
