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

## Output Per Arc (~48 files)

**One file = one action. Loser-proof.**

Example with `burning_bridges` slug:

| File | Destination |
|------|-------------|
| `post_01_free_burning_bridges.rtf` | Substack (paste) |
| `post_01_free_burning_bridges_x.md` | X/Twitter |
| `post_01_free_burning_bridges_reddit_relationships.md` | Reddit |
| `substack_notes_post_01_1.md` | Notes (morning) |
| `substack_notes_post_01_2.md` | Notes (afternoon) |

Repeat × 7 posts = 42 files + arc files (AITA, Medium teaser, etc.)

## Daily Workflow

**Morning:**
```
1. post_01_*.rtf           → Substack
2. post_01_*_x.md          → X
3. post_01_*_reddit_*.md   → Reddit
4. substack_notes_post_01_1.md → Notes
```

**Afternoon:**
```
5. substack_notes_post_01_2.md → Notes
```

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

## Loser Notes (PDF Product)

```bash
python scripts/generate_loser_notes.py --arc output/drafts/twenty-year-favor
python scripts/generate_loser_notes.py --compile  # compile book
```

75 arcs → 150-page book → Gumroad/Amazon

---

## More Ideas

```bash
python scripts/generate_ideas.py          # 10 new ideas
python scripts/generate_ideas.py --dry-run # preview only
```
