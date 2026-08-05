-- mart_complaint_churn_risk.sql
-- The core analytical output: one row per complaint category, ranked by
-- churn-risk, with an illustrative revenue-at-risk figure. This is the model
-- that feeds the executive dashboard's "churn-risk ranking" and "revenue
-- exposure" panels.
--
-- churn_risk_index  = (category's share of total weighted complaint volume)
--                      x (share of that category's complaints with churn language)
--                      re-normalized to sum to 100 across categories.
--
-- revenue_at_risk_usd = churn_risk_share x at_risk_revenue_pool, where
-- at_risk_revenue_pool = total_members x illustrative_churn_rate x avg_acv.
-- The illustrative churn rate is a named, tunable assumption stored in
-- {{ ref('churn_model_assumptions') }} -- swap in a measured attrition rate
-- once cohort-level billing/cancellation data is joined in.

with review_categorized as (
    select * from {{ ref('int_review_categorized') }}
),

reddit_signal as (
    select * from {{ ref('int_reddit_signal') }}
),

-- reviews count as weight 1 each; Reddit posts are weighted by engagement
-- but downweighted overall (0.15x) since the source structurally over-indexes
-- on power users relative to the app-store/Trustpilot review population
review_weighted as (
    select category_id, category_name, owning_team, severity_1_5,
           1.0 as weight,
           has_churn_language
    from review_categorized
),

reddit_weighted as (
    select category_id, category_name, owning_team, severity_1_5,
           0.15 * engagement_weight as weight,
           has_churn_language
    from reddit_signal
),

all_weighted as (
    select * from review_weighted
    union all
    select * from reddit_weighted
),

category_totals as (
    select
        category_id,
        any_value(category_name)  as category_name,
        any_value(owning_team)    as owning_team,
        any_value(severity_1_5)   as severity_1_5,
        sum(weight)                                          as total_weight,
        sum(case when has_churn_language then weight else 0 end) as churn_weight
    from all_weighted
    group by category_id
),

shares as (
    select
        *,
        total_weight / sum(total_weight) over ()        as volume_share,
        churn_weight / nullif(total_weight, 0)           as churn_language_share
    from category_totals
),

risk as (
    select
        *,
        volume_share * churn_language_share              as raw_churn_weighted_volume
    from shares
),

assumptions as (
    select * from {{ ref('churn_model_assumptions') }}
),

final as (
    select
        r.category_id,
        r.category_name,
        r.owning_team,
        r.severity_1_5,
        round(r.volume_share * 100, 1)                                  as volume_share_pct,
        round(r.churn_language_share * 100, 1)                          as churn_language_share_pct,
        round(
            r.raw_churn_weighted_volume
            / sum(r.raw_churn_weighted_volume) over () * 100
        , 1)                                                             as churn_risk_index_0_100,
        round(
            (r.raw_churn_weighted_volume / sum(r.raw_churn_weighted_volume) over ())
            * (a.total_members * a.illustrative_churn_rate_pct / 100.0 * a.avg_annual_revenue_per_member_usd)
        , 0)                                                              as illustrative_annual_revenue_at_risk_usd
    from risk r
    cross join assumptions a
)

select * from final
order by churn_risk_index_0_100 desc
