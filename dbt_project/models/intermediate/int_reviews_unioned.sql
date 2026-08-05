-- int_reviews_unioned.sql
-- Standardizes App Store, Google Play, and Trustpilot reviews into one grain
-- (one row per review). Reddit is intentionally excluded here and modeled
-- separately in int_reddit_signal.sql because it's a different unit
-- (post/thread with upvotes, not a star-rated review).

with app_store as (

    select
        review_id,
        submitted_at,
        star_rating,
        review_title,
        review_body,
        platform,
        app_version,
        cast(null as varchar)  as reviewer_country
    from {{ ref('stg_app_store_reviews') }}

),

trustpilot as (

    select
        review_id,
        submitted_at,
        star_rating,
        review_title,
        review_body,
        platform,
        cast(null as varchar)  as app_version,
        reviewer_country
    from {{ ref('stg_trustpilot_reviews') }}

)

select * from app_store
union all
select * from trustpilot
