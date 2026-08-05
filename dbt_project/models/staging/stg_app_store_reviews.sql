-- stg_app_store_reviews.sql
-- Source: raw.app_store_reviews (loaded via an ELT job hitting the Apple RSS
-- customer-reviews feed: itunes.apple.com/us/rss/customerreviews/id=933944389)
-- and raw.google_play_reviews (loaded via a scheduled Play Store export job).
--
-- This model does light cleanup only -- casting, trimming, platform tagging.
-- Business logic (category tagging, churn-language detection) lives downstream
-- in the intermediate layer so it stays testable and reusable.

with ios as (

    select
        review_id,
        cast(submitted_at as timestamp)  as submitted_at,
        rating                            as star_rating,
        trim(title)                       as review_title,
        trim(body)                        as review_body,
        app_version,
        'ios'                             as platform
    from {{ source('raw', 'app_store_reviews') }}

),

android as (

    select
        review_id,
        cast(submitted_at as timestamp)  as submitted_at,
        rating                            as star_rating,
        trim(title)                       as review_title,
        trim(body)                        as review_body,
        app_version,
        'android'                          as platform
    from {{ source('raw', 'google_play_reviews') }}

)

select * from ios
union all
select * from android
