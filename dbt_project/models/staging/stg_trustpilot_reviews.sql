-- stg_trustpilot_reviews.sql
-- Source: raw.trustpilot_reviews, loaded via a scheduled scrape/API pull of
-- trustpilot.com/review/whoop.com (~200+ pages / ~4,000-5,000+ reviews as of
-- Aug 2026 per manual audit -- see sourced research doc).

select
    review_id,
    cast(published_at as timestamp)  as submitted_at,
    stars                              as star_rating,
    trim(review_title)                 as review_title,
    trim(review_body)                  as review_body,
    'trustpilot'                       as platform,
    reviewer_country
from {{ source('raw', 'trustpilot_reviews') }}
