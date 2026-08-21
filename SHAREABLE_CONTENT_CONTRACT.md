# Shareable Content Contract

## Purpose

This is the short version of the content operating model for reuse in other repos.

The current content system is:

- Substack for the canonical long-form article
- Substack notes for the morning, afternoon, and evening slots
- Medium for the compatibility long-form export when scheduled
- Bluesky for an optional mirrored short-form package when scheduled

X can be held back for a run that only needs the long-form and note lanes.

## Daily Output

Each day, the repo should try to produce:

- 1 canonical Substack article
- 3 Substack note slots: morning, afternoon, evening
- 1 Medium export when scheduled
- 1 Bluesky variant when the schedule asks for it
- 1 short internal summary
- 1 list of weak or rejected angles

Reruns may temporarily hold X and `x_queue.json` while still producing `substack.md`, the Substack note family, `medium.md`, and `bluesky.md`. In that mode, Substack is still the primary article lane.

## Substack

Substack is the canonical long-form home.

It should:

- stand alone
- explain the premise clearly
- show the evidence or reasoning
- state the takeaway plainly
- avoid invented claims

It is the source of truth for the daily article URL. All other channels may start with a placeholder link token and get rewritten later by the URL-update job.
The bundle metadata should also include `substack_tags` so the publisher can apply the same tag list downstream.
For the Substack note family, the reusable contract is `meta.json.channels.substack_notes.items`. Each item should include `slot`, `file`, and `status`. Keep `meta.json.channels.substack_note` as the compatibility alias with the base note, the full file list, and the same `items` payload.

## X

X is the short-form distribution layer.

It should:

- feel like 6 to 8 distinct posts, not one long post
- include a hook, story, product/problem, data, opinion, question, or observation
- allow a link only in the first one or two posts if it adds value
- keep each post under 200 characters
- stay specific and defensible
- use `{{substack_url}}` as the temporary link token before the later rewrite job runs

## Bluesky

Bluesky follows the same short-form rule set as X.

It should:

- stay under 200 characters
- remain native and specific
- use `{{substack_url}}` as the temporary link token when a link is included
- avoid link spam or duplicated wording from X

Dispatch shape:

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
```

- `substack.md` is the canonical long-form article
- `substack_note.md` is the base Substack Note
- `substack_note_morning.md`, `substack_note_afternoon.md`, and `substack_note_evening.md` are the staggered note files
- `medium.md` is the compatibility export when scheduled
- `bluesky.md` is the optional human review file for the mirrored short post
- `x.md` is the human review file when X is enabled
- `x_queue.json` is the machine dispatch queue when X is enabled
- `meta.json.channels.substack_notes.items` is the slot-aware dispatch list
- `meta.json.channels.substack_note` remains the compatibility alias
- every queued X item should carry its own `publish_at`
- downstream pusher code should only release items whose `publish_at` is due
- a later rewrite job should replace `{{substack_url}}` with the published Substack URL from the dated handoff record after the article goes live
- `state/publish-handoff/YYYY-MM-DD/stockarithm.json` in `founder-revenue-os` is the reusable handoff record for later jobs
- `meta.json.substack_tags` is the canonical tag list for the Substack article

## Rejection Rules

The automation should reject content that is:

- vague
- repetitive
- generic
- too salesy
- too dependent on missing context
- based on weak or unverified facts
- forced only to hit a quota

## Operating Shape

```text
1 core idea
-> 1 Medium article
-> 6 to 8 X posts
-> reject weak angles
-> publish only the strong cuts
```

## Rule Of Thumb

Consistency matters, but sharpness matters more.

If the material is weak, the output should be thinner or absent, not padded.
