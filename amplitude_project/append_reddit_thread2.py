#!/usr/bin/env python3
"""One-off: append a curated subset (~29 of ~100 real comments) from the
second real Reddit thread -- former WHOOP CPO Ben Foster's public defense of
the 5.0 upgrade policy and the reaction to it. Not exhaustive by design: this
thread alone has ~100 comments, and processing every one would blow past the
100-150 credible-sample target already reached with the first 124 reviews.
This selects for distinct signal (band/accessory incompatibility, HR-accuracy
stagnation, regulatory mentions) rather than volume for its own sake."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "real_reviews_collected.json"
THREAD_URL = "https://www.reddit.com/r/whoop/comments/1kkfg8a/thoughts_on_50_upgrade_from_ben_foster_former/"

# (author, date, title_or_None, text, categories, has_churn_language, score)
NEW = [
    ("Temporary_Debt8132", "2025-05-14", "Thoughts on 5.0 Upgrade from Ben Foster, former Chief Product Officer at Whoop",
     "I am the former CPO at Whoop (2020-2022)... If you were intending to pay for your Whoop subscription indefinitely and you continue to, then you will literally pay $0 more... The only people for whom it matters are those who had an intention of canceling their subscription, anyway.",
     ["subscription"], False, 1900),
    ("sontino", "2025-05-14", None, "Can you please explain why they also feel the need to marginally change the dimensions so that bands and accessories need to be re-purchased? I assume this is also a core tenet of profitability… planned obsolescence to drive new sales.",
     ["band_durability", "hardware"], False, None),
    ("lobster_roulette", "2025-05-14", None, "This is my number 1 issue. Beyond everything else, the form factor isn't changing enough to warrant throwing away all old straps and having to buy new ones. This is the part that feels scummiest to me.",
     ["band_durability"], False, None),
    ("GumbysGumbo", "2025-05-14", None, "Not only do they monopolize the hardware and the subscription, but this company is sitting on the health data of MILLIONS of people to train their bespoke model. But they are pinching every penny along the way.",
     ["subscription"], False, None),
    ("-Istvan-5-", "2025-05-15", None, "Silence on this question is deafening. This is my reason for never renewing. Between my wife and I, we have invested in numerous bands, bras, clothing etc... Now? They are all just useless.",
     ["subscription", "band_durability"], True, None),
    ("ClimateFew2414", "2025-05-15", None, "The decision to require a re-up even if you had more than 12 months was made and they only backpedaled after backlash. That doesn't convey that they care about us users... now people don't want to renew because they feel betrayed.",
     ["subscription"], False, None),
    ("ElegantGrand8", "2025-05-15", None, "If I have been paying for whoop 4.0 since 2022 at US$30 a month, then I've paid approximately $830 USD. If this doesn't demonstrate user commitment then whoop is really out of touch with the loyal consumers it had.",
     ["subscription"], False, None),
    ("SFGetWeird", "2025-05-15", None, "I've been a member since Nov 2021 and paid wayyyy more than what my current whoop hardware is worth. With THE next upgrade, I'm out based on how they handled this. Insane move by them, probably the end of the company.",
     ["subscription"], True, None),
    ("smokeshowbaby", "2025-05-16", None, "WHOOP charges each user $200-300 per year even in years where they don't receive a device. For longtime customers, that means they've received something like $800-1000 since the last upgrade. That's 2x more than an Apple Watch.",
     ["subscription"], False, None),
    ("willowgoose", "2025-05-16", None, "A degraded app experience that feels deliberately exclusionary: sections of the app are now blurred out unless you're using the newest hardware... WHOOP's decision to make previous bands incompatible with newer models has left many users with sometimes dozens of now-useless bands.",
     ["subscription", "app_experience", "band_durability"], False, None),
    ("MaTr82", "2025-05-16", None, "No-one should feel a lifelong commitment to a company. In 2 years of being a member, I've seen little innovation from Whoop. A company should earn my extended subscription, not make me extend in hope of some improvements coming.",
     ["subscription"], False, None),
    ("vargus21", "2025-05-16", None, "I ended my Whoop subscription 6 months ago so I don't have any anger towards the current decisions the company has made, I just like to keep up on what they are doing after having spent 5 years as a subscriber.",
     ["subscription"], True, None),
    ("Top_Anywhere_7861", "2025-05-17", None, "I bought the MG, yet if I'm unhappy and send it back I can get the 5.0 but I won't get my money back. How messed up is that? I haven't used the device for the time but I'm forced to pay for it as soon as it's added to my account.",
     ["subscription", "hardware"], False, None),
    ("olemiss36", "2025-05-17", None, "People expected whoop to honor the terms that existed when they signed up and not do a rug pull... what they did was a slap in the face to loyal customers.",
     ["subscription"], False, None),
    ("JWNSM", "2025-05-17", None, "For those considering cancelling, just a friendly reminder: the Whoop T&Cs allows you to cancel and receive the pro-rated amount of your subscription back any time there is a material change (as there was with this launch) by emailing Whoop support within 30 days of the change.",
     ["subscription"], True, None),
    ("indianwin2001", "2025-05-17", None, "The Quantified Scientist put out a preliminary review today and said he sees NO difference in HR accuracy from the 4.0 to the MG. In 4 years, no improvement in this? I wear whoop 4.0 and a Garmin Epix Pro and the HR accuracy is VERY different during training.",
     ["hr_accuracy"], False, None),
    ("00DEADBEEF", "2025-05-18", None, "Whoop Peak is virtually the same as Whoop 4.0, they've just added Healthspan and Pace of Aging which are purely software features. Whoop One takes away Stress Monitor and Health Monitor which 4.0 members currently have.",
     ["subscription"], False, None),
    ("Potwell", "2025-05-18", None, "WHOOP's website promised free next-gen upgrades after six months when I bought my 4.0, a key reason I chose WHOOP. The new 12-month commitment or $49 fee for 5.0 contradicts this, feeling like a bait-and-switch. Unless they do or offer a refund, I'll cancel and switch devices.",
     ["subscription"], True, None),
    ("matebookxproi716512", "2025-05-18", None, "I am asked to just add another 260€ onto my new 11 Month and 23 day subscription or shell out 70€ for no tangible benefit... I even received an email promising me eligibility for a free upgrade due to my 12 month remaining subscription, only for that to get revoked a day later.",
     ["subscription"], False, None),
    ("dwb1310", "2025-05-19", None, "I now have no idea WHAT Whoop is even selling. Hardware? A service? Or just whatever drives the most short-term cash and year end profitability? I'll be watching closely... But until I do, I won't spend a penny.",
     ["subscription"], False, None),
    ("lilbikkie", "2025-05-19", None, "I have put a lot more money into my whoop subscription ($1,100 AUD over 25 months) and didn't reap the benefits of any tech updates throughout that time... (except AI, strength trainer that never worked and inaccurate steps).",
     ["subscription", "app_experience", "strain_undercounting"], False, None),
    ("elkishdude", "2025-05-19", None, "The promise was broken and here's what you get from me: nothing. I'm not going to upgrade. I will keep the device I have and I'm sorry, the product doesn't deserve more money for me despite the benefits because the promise was broken.",
     ["subscription"], False, None),
    ("TechLover94", "2025-05-20", None, "I had 17 months remaining on my subscription and was prompted to re-up again. I've consistently been a member for 6 years... To not be shipped the device on launch day almost by default just felt like I've been cheering the company along all this time... and got nothing but an ask for more money.",
     ["subscription"], False, None),
    ("danlam", "2025-05-20", None, "In the past two years, we got a ChatGPT wrapper, a strength trainer feature that feels unfinished, and a step counter beta that is highly inaccurate... I will no longer be renewing.",
     ["subscription", "app_experience", "strain_undercounting"], True, None),
    ("DrVurt", "2025-05-21", None, "The simple fact is that most people won't leave... The danger for whoop is someone with better regard and care for their customers comes and steals the niche market away. I have zero brand loyalty and will be waiting for a better option to come along.",
     ["subscription"], False, None),
    ("Grauax", "2025-05-21", None, "Now they have created a new tier of devices that forces you to pay an amount yearly for which you can buy lifelong devices that offer the same capabilities or better... ECG was offered by Samsung for instance close to 6 years ago already.",
     ["subscription", "bpi_fda"], False, None),
    ("Tminus35", "2025-05-22", None, "I wanted to extend my membership 24 months. Here is the response I received via email: 'Please know that only new members can select a 24-month membership when joining. However, if you're upgrading to WHOOP 5.0 or WHOOP MG, the 24-month option will not be available.' Loyalty is dead at Whoop and profits are the number one goal.",
     ["subscription"], False, None),
    ("BigMetal1", "2025-05-22", None, "Going to see how well they fare in Australia with the ACCC looking into them. The amount of coping around their blatant lies to get people to sign up is sickening.",
     ["subscription"], False, None),
]


def main():
    payload = json.loads(DATA_FILE.read_text())
    existing = payload["reviews"]
    start_num = len(existing) + 1
    for i, (author, date, title, text, categories, churn, score) in enumerate(NEW):
        rid = f"real_{start_num + i:03d}"
        entry = {
            "id": rid, "platform": "Reddit", "author": author or "[deleted]",
            "date": date, "title": title, "text": text, "categories": categories,
            "has_churn_language": churn, "star_rating": None, "helpful_count": score,
            "source_thread": THREAD_URL,
        }
        existing.append(entry)

    payload["_meta"]["sources"].append(
        f"{THREAD_URL} (former WHOOP CPO Ben Foster's public defense of the 5.0 upgrade policy + "
        "reaction; user-collected. Only a curated 28-comment subset of this ~100-comment thread was "
        "processed, selected for distinct signal rather than exhaustively, since the sample was "
        "already at the credible 100-150 target before this thread.)"
    )

    DATA_FILE.write_text(json.dumps(payload, indent=2))
    print(f"Appended {len(NEW)} entries. Total reviews now: {len(existing)}")


if __name__ == "__main__":
    main()
