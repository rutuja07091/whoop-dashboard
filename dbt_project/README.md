# whoop_complaint_churn_risk (dbt project)

A worked example of how the complaint-to-churn-risk analysis would be built
on WHOOP's actual stack (Snowflake + dbt). This is illustrative scaffolding,
not a project connected to a live warehouse -- it shows the modeling
approach, not executable output. (The real numbers behind the dashboard come
from a separate, real data pipeline -- see `amplitude_project/` -- not from
running this SQL against a warehouse.)

## Structure

```
models/
  staging/       -- 1:1 cleanup of raw sources (App Store, Google Play, Trustpilot, Reddit)
  intermediate/  -- category tagging + churn-language detection (the core business logic)
  marts/         -- final analytical tables behind the dashboard
seeds/
  category_reference.csv        -- the 9 complaint categories, owning team, severity, keyword patterns
  churn_model_assumptions.csv   -- the named, tunable revenue-at-risk assumptions
```

## Lineage

```
raw.app_store_reviews  ---\
raw.google_play_reviews ---+--> stg_app_store_reviews --\
raw.trustpilot_reviews  -------> stg_trustpilot_reviews  +--> int_reviews_unioned --> int_review_categorized --\
raw.reddit_posts -------------> stg_reddit_posts -------> int_reddit_signal ------------------------------------+--> mart_complaint_churn_risk
                                                                                                                  \-> mart_complaint_timeseries
```

## Design choices worth calling out

- **Category tagging starts as regex, not an LLM call.** Fast, cheap, and fully
  explainable for a v1 -- a natural v2 is swapping in an LLM classifier once
  a labeled validation set exists to measure the regex baseline against.
- **Reddit is modeled separately and downweighted (0.15x, engagement-weighted).**
  A single viral post (the 2,400-upvote cancellation thread) is real signal,
  but Reddit structurally over-represents power users with strong opinions
  about commercial policy -- treating it identically to a star-rated review
  would bias the model toward subscription/billing complaints more than the
  underlying member base likely warrants.
- **Revenue-at-risk assumptions live in a seed table, not hardcoded in SQL.**
  `churn_model_assumptions.csv` is the one place a stakeholder (or a future
  version of this analysis, once real cohort/billing data exists) would need
  to edit to update every downstream number -- a self-serve pattern that lets
  stakeholders update assumptions without waiting on an analyst.
- **`mart_complaint_churn_risk` separates volume share from churn-language
  share deliberately.** The single most decision-relevant number in this
  entire project is that they diverge: accuracy-related complaints
  (recovery/strain/HR) make up a large share of volume but a small share of
  churn-risk, while subscription/billing and hardware failures are the
  reverse. Collapsing this into one "complaint score" would hide that.

## What's illustrative vs. what's real

This SQL is illustrative -- it shows how the pipeline would be built on
WHOOP's actual warehouse, but isn't connected to a live one. The `raw.*`
sources referenced above are the real integration points a production build
would use.

The dashboard's real numbers come from a separate, genuinely real pipeline:
152 hand-collected reviews (App Store, Google Play, Trustpilot, Reddit),
individually tagged by category and churn-language, ingested as real events
into Amplitude and queried live from there. See `amplitude_project/README.md`
for the full data-collection and ingestion writeup, including sourcing and
sample-bias caveats. This dbt project and that Amplitude pipeline model the
same underlying logic (category tagging, churn-language detection, Reddit
downweighting) -- one on illustrative SQL, one on real, queryable data.
