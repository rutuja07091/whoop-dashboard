-- int_review_categorized.sql
-- Tags each review with a complaint category (regex against title+body, using
-- the keyword_pattern in the category_reference seed) and flags whether the
-- review contains explicit cancel/switch ("churn") language. A review can
-- match more than one category -- that's intentional, since e.g. a review
-- can complain about both hardware failure AND cancellation in the same text.
--
-- NOTE ON METHOD: a production version of this model would likely replace the
-- regex match with an LLM classification call (batch job through a
-- warehouse-native function or an external model) for better recall/precision
-- than keyword matching alone, with this regex version kept as a fast,
-- explainable fallback / QA baseline.

with reviews as (

    select * from {{ ref('int_reviews_unioned') }}

),

categories as (

    select * from {{ ref('category_reference') }}

),

matched as (

    select
        r.review_id,
        r.submitted_at,
        r.star_rating,
        r.platform,
        r.app_version,
        c.category_id,
        c.category_name,
        c.owning_team,
        c.severity_1_5,
        case
            when regexp_like(lower(r.review_title || ' ' || r.review_body), lower(c.keyword_pattern))
            then true else false
        end as is_category_match
    from reviews r
    cross join categories c

),

churn_flagged as (

    select
        *,
        case
            when regexp_like(
                lower(review_title_body),
                'cancel|canceled|cancelled|switch(ed)? to|refund|won''t renew|not renewing|going back to'
            )
            then true else false
        end as has_churn_language
    from (
        select m.*, (r.review_title || ' ' || r.review_body) as review_title_body
        from matched m
        join reviews r using (review_id)
    )
)

select
    review_id,
    submitted_at,
    star_rating,
    platform,
    app_version,
    category_id,
    category_name,
    owning_team,
    severity_1_5,
    has_churn_language
from churn_flagged
where is_category_match
