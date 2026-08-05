-- mart_complaint_timeseries.sql
-- Monthly complaint-volume index per category, for overlaying against known
-- product/regulatory events (launch dates, FDA filings, redesigns). Powers
-- the dashboard's time-series panel.

with review_categorized as (
    select * from {{ ref('int_review_categorized') }}
),

monthly as (
    select
        date_trunc('month', submitted_at)  as month,
        category_id,
        count(*)                             as review_count,
        sum(case when has_churn_language then 1 else 0 end) as churn_flagged_count
    from review_categorized
    group by 1, 2
),

indexed as (
    select
        month,
        category_id,
        review_count,
        churn_flagged_count,
        -- index each category to its own trailing-12-month peak = 100, so
        -- categories are comparable regardless of absolute volume
        round(
            review_count * 100.0
            / nullif(max(review_count) over (
                partition by category_id
                order by month
                rows between 11 preceding and current row
              ), 0)
        , 1) as relative_intensity_index
    from monthly
)

select
    i.month,
    i.category_id,
    c.category_name,
    i.review_count,
    i.churn_flagged_count,
    i.relative_intensity_index
from indexed i
join {{ ref('category_reference') }} c using (category_id)
order by i.month, i.category_id
