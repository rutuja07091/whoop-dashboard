-- int_reddit_signal.sql
-- Reddit posts, tagged the same way as reviews, but keeping upvotes/comments
-- as an engagement-weight so a single 2,400-upvote post can be weighted
-- against thousands of individually-rated app store reviews without simply
-- counting it as "1 data point". Reddit is downweighted overall in the churn
-- model (see mart_complaint_churn_risk.sql) because it structurally
-- over-indexes on power users with strong opinions about commercial policy.

with posts as (

    select * from {{ ref('stg_reddit_posts') }}

),

categories as (

    select * from {{ ref('category_reference') }}

),

matched as (

    select
        p.post_id,
        p.submitted_at,
        p.upvotes,
        p.num_comments,
        c.category_id,
        c.category_name,
        c.owning_team,
        c.severity_1_5,
        case
            when regexp_like(lower(p.post_title || ' ' || p.post_body), lower(c.keyword_pattern))
            then true else false
        end as is_category_match,
        case
            when regexp_like(
                lower(p.post_title || ' ' || p.post_body),
                'cancel|canceled|cancelled|switch(ed)? to|refund|won''t renew|not renewing'
            )
            then true else false
        end as has_churn_language
    from posts p
    cross join categories c

)

select
    post_id,
    submitted_at,
    upvotes,
    num_comments,
    category_id,
    category_name,
    owning_team,
    severity_1_5,
    has_churn_language,
    -- engagement weight: log-scaled so viral posts count more without
    -- swamping the whole model
    ln(upvotes + num_comments + 1) as engagement_weight
from matched
where is_category_match
