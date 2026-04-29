# confessions-pipeline

**The Reluctant Adult: Confessions From A Loser**
*by Lou Zerr*

Content pipeline for `confessionsofaloser.substack.com`

---

## How it works

Two intake pipes. Same output. 7 posts per arc.

**Pipeline 1 — Life Event**
You remember something that happened. You dump it in. Claude extracts the failure arc and writes the week.

**Pipeline 2 — Paragraph Seed**
You write a raw thought or observation. Claude mines it for the failure arc and writes the week.

**Output:** 7 post drafts — Posts 1-3 FREE, Posts 4-7 PAID — with a publish schedule.

---

## Setup

```bash
git clone git@github.com:yourusername/confessions-pipeline.git
cd confessions-pipeline
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
```

Add to GitHub Secrets: `ANTHROPIC_API_KEY`

---

## Usage

### Generate an arc directly

**From a life event:**
```bash
python scripts/generate_arc.py \
  --event "Family pressured me into a marriage of convenience. Stayed 20+ years because of inertia and money. Never stay because of money."
```

**From a paragraph seed:**
```bash
python scripts/generate_arc.py \
  --seed "There is a difference between being broke and being poor. Broke is temporary. Poor is a mindset. I have been both and confused them for most of my life."
```

**From a text file (for longer dumps):**
```bash
python scripts/generate_arc.py --event-file my_story.txt
python scripts/generate_arc.py --seed-file my_thought.txt
```

### Manage the backlog

**Add ideas as they come to you:**
```bash
# life event
python scripts/backlog.py add \
  --type event \
  --idea "stayed in wrong job for 8 years because i was afraid to lose the pension"

# paragraph seed  
python scripts/backlog.py add \
  --type seed \
  --idea "nobody tells you that avoiding conflict is itself a choice with consequences"
```

**List what's in the backlog:**
```bash
python scripts/backlog.py list
python scripts/backlog.py list --status queued
```

**Generate from a backlog item:**
```bash
python scripts/backlog.py generate --id a3f2b1c4
```

**Mark as published:**
```bash
python scripts/backlog.py status --id a3f2b1c4 --set published
```

---

## Output structure

```
output/
  drafts/
    convenience-marriage/
      arc.json              # full arc metadata
      schedule.json         # publish dates for all 7 posts
      post_01_free_*.md     # free post 1
      post_02_free_*.md     # free post 2
      post_03_free_*.md     # free post 3
      post_04_paid_*.md     # paid post 4
      post_05_paid_*.md     # paid post 5
      post_06_paid_*.md     # paid post 6 — What I Should Have Done
      post_07_paid_*.md     # paid post 7 — The Tail (gut punch)
```

---

## GitHub Actions

**Manual trigger:** Go to Actions → Generate Weekly Arc → Run workflow
- Paste your event or seed directly in the UI
- Or provide a backlog ID

**Scheduled:** Every Monday 9am ET — auto-picks next queued backlog item

---

## Backlog

`backlog.json` — tracked in git. Add ideas whenever they hit you.

Statuses: `queued` → `generating` → `drafted` → `scheduled` → `published`

---

## The voice

Lou Zerr. 55. Nine hundred and forty three mistakes. Still going.

*"I am 55 years old and pretty much I have made every mistake in the book. I don't know why I am not in a gutter face down in the mud, but who knows — maybe one day. Listen to me to avoid being like me."*
