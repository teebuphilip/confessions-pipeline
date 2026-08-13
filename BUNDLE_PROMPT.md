# Reusable Bundle Creation Prompt

Use this prompt when you have manually written arc posts and need to package them into the content pusher format.

---

## The Prompt

I have a new arc of posts for the Confessions of a Loser Substack. The arc is called **[ARC NAME]** and the posts are saved in:

```
output/drafts/[arc-folder-name]/
  post_01_free_[arc-folder-name].md
  post_02_free_[arc-folder-name].md
  post_03_free_[arc-folder-name].md
  post_04_paid_[arc-folder-name].md
  post_05_paid_[arc-folder-name].md
  post_06_paid_[arc-folder-name].md
  post_07_paid_[arc-folder-name].md
```

I want to schedule these 7 posts starting on **[START DATE, e.g. Tuesday Oct 7, 2026]**, one post per day for 7 consecutive days.

Please:
1. Create 7 dated bundle folders under `marketing/content/` following this naming pattern: `{YYYY-MM-DD}-lou-{short-slug}-{01..07}/`
2. Copy each post file into its bundle as `substack.md`
3. Write a `meta.json` in each bundle with `status: ready`, the correct `scheduled_date`, `scheduled_time: 07:00`, `timezone: America/New_York`, `product: confessionsofaloser`, and `channels: { substack: ready }`
4. Leave `title` blank — I will fill that in before pushing
5. Do not touch any other files

The short slug for this arc is: **[e.g. lou-new-arc-name]**

---

## Notes

- Posts 01-03 are free. Posts 04-07 are paid.
- Start date should always be a Tuesday unless there is a specific reason not to.
- The `title` field in `meta.json` is intentionally left blank — fill it in manually before the pusher runs.
- After creating the bundles, commit with message: `content: schedule [arc name] arc, [start date] - [end date]`
- Check that no `.env` file gets committed.

---

## Arc Folder Reference

Existing arcs and their slugs:

| Arc folder | Short slug | Dates |
|---|---|---|
| four-hundred-dollars-vegas-lazy | lou-vegas-lazy | Aug 19 - Aug 25 |
| 600-line-move-i-didnt-see | lou-line-move | Aug 26 - Sep 1 |
| soft-open-made-me-look-stupid | lou-soft-open | Sep 2 - Sep 8 |
| hedge-that-ate-itself | lou-hedge | Sep 9 - Sep 15 |
| the-revenge-bet | lou-revenge-bet | Sep 16 - Sep 22 |
| the-300-dollar-vibe-check | lou-vibe-check | Sep 23 - Sep 29 |
| the-guessing-years | lou-guessing-years | Sep 30 - Oct 6 |

Next available start date: **Tuesday Oct 7, 2026**
