-- stg_reddit_posts.sql
-- Source: raw.reddit_posts, loaded via Reddit's public listing API
-- (reddit.com/r/whoop/top.json, reddit.com/r/whoop/new.json) on a daily cron.
-- Reddit skews toward power users ("meticulous, has-receipts" per the sourced
-- research) so this source is kept separate from review-platform sources and
-- weighted differently downstream -- see int_review_categorized.sql.

select
    post_id,
    cast(created_at as timestamp)   as submitted_at,
    upvotes,
    num_comments,
    trim(title)                      as post_title,
    trim(selftext)                   as post_body,
    'reddit'                          as platform,
    subreddit
from {{ source('raw', 'reddit_posts') }}
where subreddit = 'whoop'
