# Content Contract

## Purpose

This file defines the daily content output contract for the repo.

The system is intended to automate publishing for:

- Substack
- Substack notes
- Medium compatibility exports
- Bluesky

X is optional and may be held back for specific runs.

## Daily Output

The repo should attempt to produce one daily content package with:

- 1 canonical Substack article
- 3 Substack note slots: morning, afternoon, evening
- 1 Medium compatibility export when scheduled
- 1 Bluesky post when the schedule row asks for it
- 1 short internal summary of the angle used
- 1 list of rejected angles or weak drafts

Some reruns may deliberately hold back X and `x_queue.json` while still emitting `substack.md`, the Substack note family, `medium.md`, and `bluesky.md` from the same scheduled idea. In that mode, Substack remains the main article lane and Medium stays a compatibility export.

The Substack article is the source of truth.
Any X or Bluesky posts should be different cuts of that article, not random rewrites.

`meta.json` should carry the article tags in `substack_tags` so the publisher can reuse them when it writes the downstream handoff record.
For the Substack note family, `meta.json.channels.substack_notes.items` is the slot-aware dispatch contract. Each item should name the slot and file for the morning, afternoon, or evening note. Keep `meta.json.channels.substack_note` as the compatibility alias with the base file, the full `files` list, and the same `items` payload.

## Substack Contract

Substack is the long-form home for the idea.

The article should:

- explain the premise clearly
- show the evidence or reasoning
- state the takeaway plainly
- be self-contained
- not assume the reader knows the repo or the internal system
- avoid invented claims
- be the first thing the bundle treats as canonical

The later rewrite job should pull the published Substack URL from the dated handoff record and replace `{{substack_url}}` everywhere else in the bundle.

Substack should not be a teaser.
It should be the full argument.

If the idea is weak, do not publish a weak article just to maintain frequency.

## X Contract

X is the short-form distribution layer.

The post set should usually include:

- a hook post
- a story post
- a product/problem post
- a data post
- a hot take
- a question
- an observation
- a current/reply post if the timing is real

Rules:

- target 6 to 8 posts
- do not force 8 if the source material only supports 4 or 5 strong posts
- only the first one or two posts should carry a link, if links are used at all
- the rest should be native value, not link spam
- keep each post specific and defensible
- each post should carry its own `publish_at` timestamp in the bundle queue
- stagger the queue through the day instead of dumping all posts at once
- the machine-readable queue should be the dispatch contract, not the raw review file
- keep each post under 200 characters
- use `{{substack_url}}` as the temporary link token until the rewrite job runs

Bundle shape:

```text
marketing/content/{YYYY-MM-DD}-{slug}/
  substack.md
  substack_note.md
  substack_note_morning.md
  substack_note_afternoon.md
  substack_note_evening.md
  medium.md
  bluesky.md
  x.md
  x_queue.json
  meta.json
```

- `substack.md` is the canonical long-form article
- `substack_note.md` is the base Substack Note
- `substack_note_morning.md`, `substack_note_afternoon.md`, and `substack_note_evening.md` are the staggered note variants
- `medium.md` is the compatibility long-form export when the schedule row asks for it
- `bluesky.md` is the optional mirrored short post
- `x.md` is the human review package when X is enabled
- `x_queue.json` is the machine dispatch queue when X is enabled
- `x_queue.json` is where each item gets its `publish_at`
- `meta.json.channels.substack_notes.items` is the slot-aware selector for downstream dispatch
- downstream pusher code should publish only items whose `publish_at` is due
- a later job should replace `{{substack_url}}` with the live Substack URL after publication
- `state/publish-handoff/YYYY-MM-DD/stockarithm.json` in `founder-revenue-os` is the canonical URL handoff file for later jobs
- `meta.json.substack_tags` is the source field for the Substack tag list

## Rejection Rules

The automation should reject content that is:

- vague
- repetitive
- generic finance noise
- too salesy
- too self-congratulatory
- too dependent on missing context
- based on weak or unverified facts
- forced only to hit a quota

If the system cannot make a post strong, it should drop the post.

## Practical Standard

The daily package should follow this shape:

```text
1 core idea
-> 1 Medium article
-> 6 to 8 X posts
-> reject weak angles
-> publish only the strong cuts
```

## Operating Principle

Consistency matters, but sharpness matters more.

The system should publish enough to stay visible, but not so much that it starts manufacturing filler.
