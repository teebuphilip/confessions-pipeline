# Confessions Pipeline — TLDR

## What It Does

Generates 7-post story arcs from life mistakes. Outputs everything needed to publish and promote.

## Quick Start

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/generate_arc.py --seed "your story here"
```

## Pipeline

```
seed → generate 7 posts → verify (AI/readability/coherence) → output files
```

## Output Per Arc

| File | What |
|------|------|
| `post_*.rtf` | Substack paste-ready |
| `post_*.md` | Reference + promo assets |
| `substack_notes.md` | All 14 Notes (2 per post) |
| `aita_post.md` | Reddit AITA |
| `medium_teaser.md` | Medium hook |
| `subreddits.json` | Reddit targets |
| `schedule.json` | Publish dates + all content |

## Per Post Assets

- **X post:** Provocative, 280 chars, ends "— Lou"
- **Note 1:** Morning teaser, drives to article
- **Note 2:** Afternoon engagement, sparks replies
- **Subreddit:** Target + suggested title
- **Tags:** 5-8 Substack tags

## Daily Publish Flow

**Morning:** Article + X + Reddit + Note 1
**Afternoon:** Note 2

## Cost

~$0.40/arc. ~$21/year at 1 arc/week.

## Files

```
scripts/generate_arc.py    # main pipeline
scripts/generate_ideas.py  # idea generator
ideas/seed_ideas.json      # backlog (15 ideas)
louzerr.header.txt         # header template
louzerr.footer.txt         # footer CTA
state.json                 # mistake counter
```

## More Ideas

```bash
python scripts/generate_ideas.py          # 10 new ideas
python scripts/generate_ideas.py --dry-run # preview only
```
