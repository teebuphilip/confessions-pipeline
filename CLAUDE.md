# CLAUDE.md — Confessions of a Loser Pipeline

## What this repo is

Content generation pipeline for **The Reluctant Adult: Confessions From A Loser** by Lou Zerr, published at `confessionsofaloser.substack.com`.

Two intake modes → 7-post arc (posts 1-3 free, 4-7 paid) → markdown + RTF drafts + dispatcher-ready bundles.

---

## Environment setup

```bash
source ~/venvs/cd39/bin/activate
set -a && source .env && set +a
```

`.env` contains `ANTHROPIC_API_KEY`. Never commit it.

---

## Key commands

### Generate an arc

```bash
# From a paragraph seed (most common)
python scripts/generate_arc.py --seed "your story or thought here"

# From a life event description
python scripts/generate_arc.py --event "I did X, stayed for Y, it cost me Z"

# From a text file
python scripts/generate_arc.py --seed-file story.txt

# Skip verification passes (faster, riskier)
python scripts/generate_arc.py --seed "..." --skip-verify
```

### Package manually-written arc posts into dispatcher bundles

Use the prompt in `BUNDLE_PROMPT.md`. Fill in arc name, folder, start date, and short slug.

### Other scripts

```bash
python scripts/generate_ideas.py           # generate 10 arc ideas
python scripts/generate_ideas.py --count 5 --decade 40s
python scripts/generate_loser_notes.py --arc output/drafts/<arc-slug>
python scripts/generate_loser_notes.py --compile   # build THE_LOSERS_PLAYBOOK.md
```

---

## Output structure

### Draft files (per arc)

```
output/drafts/<arc-slug>/
  arc.json                          # full arc metadata
  verifications.json                # AI/readability/coherence check results
  schedule.json                     # publish dates for all 7 posts
  aita_post.md                      # Reddit AITA post
  medium_article.md                 # Medium teaser (arc-level, weekly)
  subreddits.json                   # best subreddits for the arc
  ai_costs.csv                      # per-arc API cost log

  post_01_free_<slug>.rtf           # Substack paste-ready
  post_01_free_<slug>.md            # reference + all promo assets
  post_01_free_<slug>_x.md          # X/Twitter post
  post_01_free_<slug>_reddit_<sub>.md  # Reddit post (one per subreddit)
  substack_notes_post_01_1.md       # morning Substack Note
  substack_notes_post_01_2.md       # afternoon Substack Note
  # ... repeat for posts 2-7
```

### Dispatcher bundles (automated posting)

```
marketing/content/
  {YYYY-MM-DD}-lou-{slug}-{N}/      # morning: article + X + Reddit + Note 1
    meta.json
    substack.md
    x.md
    substack_note.md
    reddit_<sub>.md
    medium.md                       # Post 1 only

  {YYYY-MM-DD}-lou-{slug}-{N}-pm/   # afternoon: Note 2 only
    meta.json
    substack_note.md
```

---

## State and tracking

- `state.json` — tracks mistake counter (`next_mistake_number`) and all arcs generated
- `output/ai_costs_all.csv` — cumulative API cost log across all runs
- Current next mistake number: **10**

---

## Arc schedule (current)

| Arc folder | Short slug | Dates | Mistake # |
|---|---|---|---|
| four-hundred-dollars-vegas-lazy | lou-vegas-lazy | Aug 19–25 | #3 |
| 600-line-move-i-didnt-see | lou-line-move | Aug 26–Sep 1 | #4 |
| soft-open-made-me-look-stupid | lou-soft-open | Sep 2–8 | #5 |
| hedge-that-ate-itself | lou-hedge | Sep 9–15 | #6 |
| the-revenge-bet | lou-revenge-bet | Sep 16–22 | #7 |
| the-300-dollar-vibe-check | lou-vibe-check | Sep 23–29 | #8 |
| the-guessing-years | lou-guessing-years | Sep 30–Oct 6 | #9 |

**Next available start date: Tuesday Oct 7, 2026**

---

## Lou Zerr's voice (never break these)

Lou is 55. 943 mistakes. Still going. Writes so others don't repeat his failures.

**Do:**
- Short punchy sentences mixed with longer ones that unravel slowly
- Specific names, numbers, sensory details
- Dry, self-aware, darkly funny without trying to be funny
- First-person, past tense
- Signs off every post as `— Lou`
- No clean endings — real life doesn't wrap neatly

**Never:**
- "dive into", "delve", "unpack", "shed light", "navigate", "landscape"
- "journey", "resonate", "empower", "at the end of the day"
- "it's important to note/remember", "certainly"
- "It's not about X, it's about Y" (parallelism = AI cancer)
- Bullet point lists (AI tell)
- Preachy tone, self-help frameworks, "5 lessons I learned"

---

## Post structure

| Post | Tier | Content |
|---|---|---|
| 1 | FREE | The setup. The moment it started. |
| 2 | FREE | The first year. When he already knew. |
| 3 | FREE | The middle. How he rationalized staying. |
| 4 | PAID | The bottom. One specific terrible moment. |
| 5 | PAID | The crawl out. Every coward move included. |
| 6 | PAID | `What I Should Have Done:` — concrete rules, no metaphors. |
| 7 | PAID | `The Tail:` — what it still costs him today. |

Minimum 600 words per post. One specific scene per post. Not a summary.

---

## Distribution channels

| Channel | Timing | Content |
|---|---|---|
| Substack | 9am | Full article |
| X/Twitter | 9am | 280-char gut punch, ends `— Lou` |
| Reddit | 9am | Subreddit-specific post |
| Substack Note 1 | 9am (with article) | Teaser, drives to article |
| Substack Note 2 | 3pm | Question/confession, sparks replies |
| Medium | Weekly (arc complete) | 500-800 word teaser with Substack CTA |

---

## Models and cost

- **Generation:** `claude-opus-4-7` (~$0.40/arc)
- **Verification:** `claude-sonnet-4-20250514`
- **Per year:** ~$21 at 1 arc/week

---

## Reddit config

`reddit_targets.json` controls subreddit mode:
- `"mode": "ai"` — AI picks 3 best subreddits per post based on content
- `"mode": "fixed"` — same subreddits every post (set in `"subreddits"` list)

---

## Header/footer templates

- `louzerr.header.txt` — uses `{mistake_number}` and `{post_number}` placeholders
- `louzerr.footer.txt` — CTA for predeve.com + startup idea validator

---

## What NOT to commit

- `.env`
- `backlog.json` (if it exists)
- Any file with real API keys or credentials

`.gitignore` handles most of this, but double-check before committing.
