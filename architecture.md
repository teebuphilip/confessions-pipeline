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
│       └── <arc-slug>/      # Generated arc output
│           ├── arc.json
│           ├── verifications.json
│           ├── schedule.json
│           ├── post_01_free_*.rtf
│           ├── post_01_free_*.md
│           ├── ... (posts 2-7)
│           ├── substack_notes.md
│           ├── aita_post.md
│           ├── medium_teaser.md
│           └── subreddits.json
├── louzerr.header.txt       # Header template
├── louzerr.footer.txt       # Footer with CTA
├── state.json               # Mistake counter + arc history
└── CLAUDE_SESSION_HANDOFF.md
```

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
| `medium_teaser` | 100-150 word teaser with CTA to Substack |

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

**Morning:**
1. Publish article to Substack
2. Post X (provocative tweet)
3. Post to target subreddit
4. Post Note 1 (teaser — drives to article)

**Afternoon:**
5. Post Note 2 (engagement — sparks conversation)

### Schedule
- 7 posts per arc
- ~2 posts per week (every 3 days)
- ~3 weeks per arc

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

## Cost Estimate

- **Per arc:** ~$0.40 (claude-opus-4-7 generation + sonnet verification)
- **Per year:** ~$21 at 1 arc/week
- **Ideas generation:** ~$0.02 per batch of 10

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
