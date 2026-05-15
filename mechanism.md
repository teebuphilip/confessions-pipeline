# Distribution Mechanism

## The Goal

**Primary:** Cross-promotion and traffic generation to other properties (CodezMart, Stockarithm, CourtDominion, WintaPlayer, Predeve).

**Secondary:** Direct monetization via Substack paid tier, PDFs, and eventually a book.

## The Channels

| Channel | Purpose | Frequency | Content Type |
|---------|---------|-----------|--------------|
| **Substack** | Home base, monetization | Daily when posting | Full 600+ word articles |
| **Substack Notes** | Discovery, engagement | 2x per post day | Short teasers + questions |
| **X/Twitter** | Provocative hooks | 1x per post | 280-char gut punches |
| **Reddit** | Targeted communities | 1x per post | Subreddit-specific posts |
| **Reddit AITA** | Viral potential | 1x per arc | Current conflict format |
| **Medium** | Funnel to Substack | 1x per arc (weekly) | 500-800 word teasers |

## Why Each Channel

### Substack (Home Base)

- **Why:** Owns the audience. Email list. Paid subscriptions.
- **Format:** 7-post arcs. Posts 1-3 free, posts 4-7 paid.
- **Goal:** Convert readers to paid subscribers.

### Substack Notes

- **Why:** Substack's algorithm rewards Notes engagement. Discovery mechanism.
- **Format:** Two notes per article:
  - **Morning (Note 1):** Teaser that drives to the article
  - **Afternoon (Note 2):** Question/confession that sparks replies
- **Goal:** Get replies. Algorithm loves replies.

### X/Twitter

- **Why:** Massive reach. Provocative content spreads.
- **Format:** 280 characters max. Gut punch. No hashtags. Ends with "— Lou"
- **Goal:** Stop the scroll. Make people click through to Substack.

**Good X post:**
> "I cried on a bathroom floor at 47 because I was too scared to leave at 28. The math finally worked. — Lou"

**Bad X post:**
> "I stayed in a bad marriage for 20 years. Here's what I learned."

### Reddit (Targeted)

- **Why:** Hyper-targeted communities. People actively seeking this content.
- **Format:** Each post targets one subreddit. Respects subreddit rules.
- **Goal:** Drive traffic from relevant communities.

**Common targets:**
- r/relationships
- r/selfimprovement
- r/LifeAdvice
- r/offmychest
- r/TrueOffMyChest

### Reddit AITA

- **Why:** Viral potential. AITA posts get massive engagement.
- **Format:** Current conflict, not historical reflection. Must follow strict rules.
- **Goal:** Debate = engagement = visibility.

**AITA Rules (or post gets removed):**
1. Must be asking for judgment on a SPECIFIC CONFLICT with a SPECIFIC PERSON
2. Must be CURRENT, not historical reflection
3. Must include "Why I might be the asshole:" section
4. Verdict must be genuinely debatable
5. End with "AITA for [action] against [person]?"

**Good AITA:**
> "My sister called me last week to tell me I ruined our family. I told her the truth about why I stayed. AITA for finally telling her?"

**Bad AITA (will be removed):**
> "I stayed in a bad marriage for 20 years" (reflection, not conflict)

### Medium

- **Why:** Different audience. SEO benefits. Funnel to Substack.
- **Format:** 500-800 word teaser. Hook, setup, turn, cliffhanger, CTA.
- **Goal:** Get readers invested, then send them to Substack for the full story.

**Key rules:**
- Same Lou Zerr byline (brand consistency)
- Does NOT give away the ending
- Does NOT include the lessons
- Ends with clear CTA to Substack
- Set canonical link to Substack (SEO)

## The Daily Workflow

**Morning (9am):**
1. Publish Substack article
2. Post to X
3. Post to target subreddit
4. Post Substack Note 1 (teaser)

**Afternoon (3pm):**
5. Post Substack Note 2 (engagement)

**Weekly (when arc completes):**
6. Post Medium article

## The Content-Dispatcher Integration

All content outputs to `marketing/content/` in dispatcher-compatible format:

```
marketing/content/2026-05-17-lou-burning-bridges-1/
  meta.json       # Channel status tracking
  x.md            # X post content
  substack.md     # Full article
  substack_note.md # Morning note
  reddit_*.md     # Reddit post
  medium.md       # Medium teaser (Post 1 only)

marketing/content/2026-05-17-lou-burning-bridges-1-pm/
  meta.json
  substack_note.md # Afternoon note
```

The dispatcher reads `meta.json`, posts to each channel, and writes back `posted_at` and `post_id`.

## The Funnel

```
X (hook) ─────────────────┐
Reddit (targeted) ────────┼──→ Substack (home) ──→ Paid subscription
Medium (teaser) ──────────┤
Substack Notes (discovery)┘
```

Everything drives to Substack. Substack converts to paid. Paid subscribers see posts 4-7. Footer CTAs drive to other properties.

## Cost Per Arc

- **Generation:** ~$0.40 (claude-opus-4-7 + verification)
- **Per year:** ~$21 at 1 arc/week
- **ROI target:** One paid subscriber ($5/month) covers 3 months of generation costs
