# Confessions Pipeline — Claude Session Handoff
Last updated: 2026-04-30

## What this is

Content pipeline for **The Reluctant Adult: Confessions From A Loser** by Lou Zerr, published at confessionsofaloser.substack.com.

Repo: https://github.com/teebuphilip/confessions-pipeline

Two intake modes → 7-post arc (posts 1-3 free, 4-7 paid), output as markdown drafts.

## Current state

- Repo is live and pushed to GitHub
- `ANTHROPIC_API_KEY` secret is set in GitHub repo secrets
- GitHub Actions workflow scheduled: Monday 9am ET (auto-picks next queued backlog item)
- Model: `claude-opus-4-7`
- Post length: 500-700 words per post
- Arc 1 has NOT been generated yet — needs `ANTHROPIC_API_KEY` set locally to run

## What has NOT been done yet

- Arc 1 not generated (local API key not set during session)
- Backlog not seeded
- No posts published to Substack yet

## File layout

```
scripts/generate_arc.py     # main arc generator — --event or --seed
scripts/backlog.py          # idea queue manager
.github/workflows/generate_arc.yml   # Monday auto-run + manual trigger
output/drafts/<arc-slug>/   # generated post files (gitignored, stays local)
backlog.json                # idea queue (gitignored)
```

## Lou's voice

Lou Zerr. 55. Nine hundred and forty three mistakes. Still going.

- Dry, self-aware, darkly funny without trying
- Never preachy. Never a framework. Never "5 lessons I learned"
- Short punchy sentences mixed with longer ones that unravel slowly
- Humor from brutal honesty, not jokes
- Signs off every post as "— Lou"
- "nine hundred and forty three others" — written out long form, not 943

## Arc 1 seed (ready to run)

```bash
python scripts/generate_arc.py --seed "Family pressured me into a marriage of convenience. I was not ready to get married, and maybe I would never have been ready. Maybe my personality needed someone more compliant (I doubt that would ever describe any woman at any time now!). I have stayed forever and it proved fruitless until 3 years ago. I stayed because of inertia and money. Never stay because of money. If something doesn't feel right, you have to move on. And never stay because of money."
```

Post 1 was already validated in an earlier GUI session — voice confirmed correct.

## To run locally

```bash
cd ~/Documents/work/confessionsofaloser
source ~/venvs/cd39/bin/activate
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/generate_arc.py --seed "..."
```

## Cost

~$0.40 per arc on claude-opus-4-7. ~$21/year at 1 arc/week.

## Next things to do

1. Set local API key and generate Arc 1
2. Review the 7 posts, publish Post 1 to Substack
3. Seed the backlog with more story ideas
4. Set up Substack free/paid split matching post tiers
