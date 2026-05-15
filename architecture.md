# Confessions of a Loser — Pipeline Architecture

## Overview

This is a content generation pipeline for **The Reluctant Adult: Confessions From A Loser** by Lou Zerr, a 55-year-old man documenting his 943 life mistakes.

**Primary Goal:** Cross-promotion and traffic generation to other properties (CodezMart, Stockarithm, CourtDominion, WintaPlayer, Predeve).

**Secondary Goal:** Direct monetization via Substack paid tier, brochures, PDFs.

## Pipeline Flow

```
INPUT (seed/event)
    ↓
GENERATE (7-post arc + metadata)
    ↓
VERIFY (per-post passes)
    ├── AI Detection
    ├── Readability
    └── Coherence
    ↓
VERIFY (AITA pass)
    ├── Conflict check
    ├── Self-reflection section
    └── Debatable verdict
    ↓
VERIFY (Arc-level pass)
    └── Narrative flow across all 7 posts
    ↓
OUTPUT
    ├── RTF files (Substack paste-ready)
    ├── Markdown files (reference + promo assets)
    ├── Substack Notes (2 per post)
    ├── X posts (provocative)
    ├── Reddit targets (per-post + arc-level)
    ├── AITA post
    └── Medium teaser
```

## File Structure

```
confessionsofaloser/
├── scripts/
│   ├── generate_arc.py      # Main pipeline script
│   └── generate_ideas.py    # Idea generator utility
├── ideas/
│   └── seed_ideas.json      # Backlog of arc ideas
├── output/
│   └── drafts/
│       └── <arc-slug>/      # Generated arc output (see below)
├── louzerr.header.txt       # Header template
├── louzerr.footer.txt       # Footer with CTA
├── state.json               # Mistake counter + arc history
└── CLAUDE_SESSION_HANDOFF.md
```

## Output Files (Loser-Proof Structure)

**One file = one action. No hunting, no mistakes.**

Example with slug `burning_bridges`, post 1, subreddit `r/relationships`:

```
output/drafts/burning_bridges/

# Arc-level files
arc.json                                    # Full arc data
verifications.json                          # Verification results
schedule.json                               # Publish dates + file map
aita_post.md                                # Reddit AITA post
medium_teaser.md                            # Medium teaser with CTA
subreddits.json                             # Arc-level subreddit targets

# Per-post files (6 files per post × 7 posts = 42 files)

## Post 1 example:
post_01_free_burning_bridges.rtf            # → Substack (paste)
post_01_free_burning_bridges.md             # → Reference
post_01_free_burning_bridges_x.md           # → X/Twitter (paste)
post_01_free_burning_bridges_reddit_relationships.md  # → Reddit (paste)
substack_notes_post_01_1.md                 # → Notes (morning)
substack_notes_post_01_2.md                 # → Notes (afternoon)

## Post 2 example:
post_02_free_burning_bridges.rtf
post_02_free_burning_bridges.md
post_02_free_burning_bridges_x.md
post_02_free_burning_bridges_reddit_selfimprovement.md
substack_notes_post_02_1.md
substack_notes_post_02_2.md

# ... posts 3-7 follow same pattern
```

**Total per arc: ~48 files** (42 per-post + 6 arc-level)

## Dispatcher-Compatible Output

In addition to the loser-proof structure above, the pipeline also outputs content in `content-dispatcher` format for automated posting.

### Folder Structure

```
marketing/content/

# Morning folders (article + X + Reddit + Note 1)
2026-05-17-lou-burning-bridges-1/
  meta.json
  x.md
  substack.md
  substack_note.md
  reddit_relationships.md
  medium.md              # Only in Post 1 folder

# Afternoon folders (Note 2 only)
2026-05-17-lou-burning-bridges-1-pm/
  meta.json
  substack_note.md

# Repeat for posts 2-7...
```

### meta.json Structure

```json
{
  "post_id": "2026-05-17-lou-burning-bridges-1",
  "product": "confessions-of-a-loser",
  "scheduled_date": "2026-05-17",
  "scheduled_time": "09:00",
  "timezone": "America/New_York",
  "status": "ready",
  "arc": "The Bridge I Burned",
  "mistake_number": 2,
  "post_number": 1,
  "tier": "free",
  "channels": {
    "x": { "status": "ready", "posted_at": null, "post_id": null },
    "substack": { "status": "ready", "posted_at": null, "post_id": null },
    "substack_note": { "status": "ready", "posted_at": null, "post_id": null },
    "medium": { "status": "ready", "posted_at": null, "post_id": null },
    "reddit": {
      "status": "ready",
      "subreddits": [
        { "name": "relationships", "file": "reddit_relationships.md", "status": "ready" }
      ]
    }
  }
}
```

### File Contents

| File | Content |
|------|---------|
| `x.md` | Just the tweet text (no headers) |
| `substack.md` | Full article with header/footer |
| `substack_note.md` | Note text only |
| `reddit_<sub>.md` | Reddit post with title |
| `medium.md` | Full Medium article (Post 1 only) |

### Schedule Pattern

- **Morning (09:00):** Article + X + Reddit + Note 1 + Medium (Post 1 only)
- **Afternoon (15:00):** Note 2

**Total per arc:** 14 content folders (7 morning + 7 afternoon)

## Input Modes

### 1. Life Event (`--event`)
Direct description: "I did X, stayed for Y, it cost me Z"

```bash
python scripts/generate_arc.py --event "I stayed at a job for 8 years because I was afraid to fail at something new"
```

### 2. Paragraph Seed (`--seed`)
Raw paragraph dump: thought, observation, or memory to mine

```bash
python scripts/generate_arc.py --seed "Family pressured me into a marriage of convenience..."
```

### 3. File Input (`--event-file` / `--seed-file`)
Read from a text file

```bash
python scripts/generate_arc.py --seed-file story.txt
```

## Generation Details

### Model Configuration
- **Generation:** `claude-opus-4-7` (high quality, ~$0.40/arc)
- **Verification:** `claude-sonnet-4-20250514` (faster, cheaper)
- **Max tokens:** 16,000 for generation, 4,000 for verification

### Anti-AI Rules (baked into prompt)

The system prompt includes strict rules to avoid AI-sounding language:

1. **Banned phrases:** "dive into", "delve", "journey", "navigate", "it's important to", etc.
2. **No parallelism:** Avoid "It's not about X, it's about Y" structure
3. **No hedging:** Cut "typically", "might be", "perhaps"
4. **Mix sentence length:** Short. Then longer. Then short again.
5. **Be specific:** Names, numbers, sensory details
6. **No clean endings:** Real life doesn't wrap up neatly
7. **No lists:** Bullet points are an AI tell

### Post Structure

| Post | Tier | Title Pattern | Content |
|------|------|---------------|---------|
| 1 | FREE | [Punchy] | The setup. The moment it started. |
| 2 | FREE | [Punchy] | The first year. When he already knew. |
| 3 | FREE | [Punchy] | The middle. How he rationalized staying. |
| 4 | PAID | [Punchy] | The bottom. One specific terrible moment. |
| 5 | PAID | [Punchy] | The crawl out. Every coward move included. |
| 6 | PAID | What I Should Have Done: | The playbook. Concrete rules. |
| 7 | PAID | The Tail: | What it still costs him today. |

## Per-Post Output

Each post generates:

| Asset | Description | Usage |
|-------|-------------|-------|
| `title` | Punchy post title | Substack headline |
| `hook` | First line | Must make them keep reading |
| `body` | 600+ words | Full post in Lou's voice |
| `tease` | One line | Tease for next post |
| `tags` | 5-8 tags | Substack discovery |
| `teaser` | 15 words | Uncomfortable truth, standalone hook |
| `x_post` | 280 chars | Provocative, ends with "— Lou" |
| `subreddit` | Target + title | Reddit cross-post |
| `note_1_teaser` | 1-3 sentences | Morning Substack Note, drives to article |
| `note_2_engagement` | Question/confession | Afternoon Note, sparks conversation |

## Arc-Level Output

| Asset | Description |
|-------|-------------|
| `arc_summary` | 2-3 sentences for product descriptions |
| `arc_subreddits` | 5 best subreddits for the arc theme |
| `aita_post` | Reddit AITA post with current conflict + self-reflection |
| `medium_article` | 500-800 word Medium article (hook, setup, turn, cliffhanger, CTA) |

## Verification Pipeline

### Per-Post Passes

**1. AI Detection**
- Flags sentences that sound like AI/LinkedIn/content marketer
- Returns verdict: `SOUNDS_HUMAN` | `NEEDS_WORK` | `AI_SLOP`
- Auto-rewrites flagged content

**2. Readability**
- Checks for awkward sentences, unclear pronouns, jarring transitions
- Returns: `readable: true/false`
- Provides fixes for issues

**3. Coherence**
- Checks for contradictions, timeline issues, logical gaps
- Returns: `coherent: true/false`
- Provides fixes for inconsistencies

### AITA Pass

Verifies Reddit compliance:
- Has specific conflict with specific person
- Is current, not historical reflection
- Includes "Why I might be the asshole:" section
- Verdict is genuinely debatable
- Ends with proper AITA question

### Arc-Level Pass

Checks narrative flow:
- Emotional arc builds Post 1 → Post 7
- Details consistent across posts
- Callbacks work (setup → payoff)
- Post 7 lands the gut punch from Post 1
- Voice stays consistent

## State Management

`state.json` tracks:
```json
{
  "next_mistake_number": 2,
  "arcs_generated": [
    {
      "mistake_number": 1,
      "arc_title": "The Twenty-Year Favor",
      "arc_slug": "twenty-year-favor",
      "generated_date": "2026-04-30",
      "status": "posting"
    }
  ]
}
```

## Publishing Cadence

### Per Post (daily when publishing)

**Morning workflow (example: Post 1 of burning_bridges):**
```
1. Open post_01_free_burning_bridges.rtf     → Paste to Substack → Publish
2. Open post_01_free_burning_bridges_x.md    → Copy → Paste to X
3. Open post_01_free_burning_bridges_reddit_relationships.md → Copy → Paste to r/relationships
4. Open substack_notes_post_01_1.md          → Copy → Paste to Substack Notes
```

**Afternoon workflow:**
```
5. Open substack_notes_post_01_2.md          → Copy → Paste to Substack Notes
```

**One file = one destination. Loser-proof.**

### Weekly Medium Post (one per arc)

When arc completes, post `medium_article.md` to Medium:
- Same Lou Zerr pseudonym as Substack
- 500-800 word teaser with cliffhanger
- CTA links to full Substack story
- Set canonical link to Substack to avoid duplicate content penalties

### Schedule
- 7 posts per arc
- ~2 posts per week (every 3 days)
- ~3 weeks per arc
- 1 Medium article when arc completes

## Header/Footer Templates

### Header (`louzerr.header.txt`)
```
I've made 943 serious mistakes in my life. I'm documenting every one of them so you don't have to make the same ones. My name is Lou Zerr. Here's another {mistake_number} of 943 (part {post_number} of 7).
```

### Footer (`louzerr.footer.txt`)
```
I spent 25 years building the wrong things. So I built a system that tells you if your startup idea is already dead before you waste 6 months on it. $97, 48 hours, you get back everything — brief, pricing, name, SEO, marketing copy, GTM plan.

→ Find out if your idea is already dead: https://buy.stripe.com/fZu4gy2Na4zU2kM3Od87K00
```

## Loser Notes Generator

Generate PDF-ready summaries from completed arcs:

```bash
# Generate Loser Notes from one arc
python scripts/generate_loser_notes.py --arc output/drafts/twenty-year-favor

# Print to screen
python scripts/generate_loser_notes.py --arc output/drafts/twenty-year-favor --stdout

# Compile all notes into one book
python scripts/generate_loser_notes.py --compile
```

**Output per arc:**
- `loser_notes_<slug>.json` — structured data
- `loser_notes_<slug>.md` — formatted markdown

**Book compilation:**
- `THE_LOSERS_PLAYBOOK.md` — all arcs combined
- ~2 pages per arc × 75 arcs = 150-page book
- Sell on Gumroad, Amazon KDP, etc.

---

## Ideas Generator

Generate more arc ideas:

```bash
# Generate 10 new ideas
python scripts/generate_ideas.py

# Generate 5 ideas focused on 40s
python scripts/generate_ideas.py --count 5 --decade 40s

# Preview without saving
python scripts/generate_ideas.py --dry-run
```

Ideas organized by decade:
- **20s:** The Setup Years
- **30s:** The Rationalization Years
- **40s:** The Damage Years
- **50s:** The Reckoning Years

## Cost Tracking

All scripts track API costs automatically:

| File | Contains |
|------|----------|
| `output/<arc-slug>/ai_costs.csv` | Costs for that arc run |
| `output/ai_costs_all.csv` | All costs across all runs |

Each CSV includes: timestamp, model, purpose, input_tokens, output_tokens, cost_usd

### Model Pricing (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| claude-opus-4-7 | $15.00 | $75.00 |
| claude-sonnet-4-20250514 | $3.00 | $15.00 |

### Cost Estimates

- **Per arc:** ~$0.40 (claude-opus-4-7 generation + sonnet verification)
- **Per year:** ~$21 at 1 arc/week
- **Ideas generation:** ~$0.02 per batch of 10
- **Loser Notes:** ~$0.01 per arc

## CLI Reference

```bash
# Generate arc from seed
python scripts/generate_arc.py --seed "your story here"

# Generate arc from file
python scripts/generate_arc.py --seed-file story.txt

# Skip verification (faster, riskier)
python scripts/generate_arc.py --seed "..." --skip-verify

# Generate more ideas
python scripts/generate_ideas.py --count 10
```

## Lou Zerr's Voice

- 55 years old, nine hundred and forty three mistakes
- Dry, self-aware, darkly funny without trying
- Never preachy, never a framework, never "5 lessons I learned"
- Short punchy sentences mixed with longer ones that unravel slowly
- Humor from brutal honesty, not jokes
- Signs off every post as "— Lou"
- The cautionary tale, not the guru
