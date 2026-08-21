# Bundle Creation

Use `scripts/create_bundles.py` to package arc posts into dispatcher-ready bundles.

## Usage

```bash
source ~/venvs/cd39/bin/activate
set -a && source .env && set +a

python scripts/create_bundles.py \
    --arc <arc-folder-name> \
    --slug <short-slug> \
    --start <YYYY-MM-DD>
```

## Example

```bash
python scripts/create_bundles.py \
    --arc four-hundred-dollars-vegas-lazy \
    --slug lou-vegas-lazy \
    --start 2026-08-22
```

## What it creates

For each of the 7 posts, one bundle folder under `marketing/content/`:

```
{YYYY-MM-DD}-{slug}-{01..07}/
  substack.md                   # copied from output/drafts/<arc>/post_NN_*
  meta.json                     # scheduled_date, status: ready, channels, etc.
  substack_note.md              # base note (compatibility alias)
  substack_note_morning.md      # drop announcement + link to article
  substack_note_afternoon.md    # question from today's article
  substack_note_evening.md      # provocative gambling/prediction markets question
  bluesky.md                    # stub — fill before pushing
  x.md                          # stub — fill before pushing
  x_queue.json                  # machine dispatch queue stub
  medium.md                     # post 1 only
```

All note stubs and x.md use `{{substack_url}}` as a link placeholder.

## After running

1. Fill in `title` in each `meta.json`
2. Fill in the note stubs and x.md with real content
3. Commit: `content: schedule [arc name] arc, [start date] - [end date]`
4. Push

## Arc schedule reference

| Arc folder | Short slug | Dates | Mistake # |
|---|---|---|---|
| four-hundred-dollars-vegas-lazy | lou-vegas-lazy | Aug 22–28 | #3 |
| 600-line-move-i-didnt-see | lou-line-move | Aug 29–Sep 4 | #4 |
| soft-open-made-me-look-stupid | lou-soft-open | Sep 5–11 | #5 |
| hedge-that-ate-itself | lou-hedge | Sep 12–18 | #6 |
| the-revenge-bet | lou-revenge-bet | Sep 19–25 | #7 |
| the-300-dollar-vibe-check | lou-vibe-check | Sep 26–Oct 2 | #8 |
| the-guessing-years | lou-guessing-years | Oct 3–9 | #9 |

**Next available start date: Saturday Oct 10, 2026**
