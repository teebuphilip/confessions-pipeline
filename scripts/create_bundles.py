#!/usr/bin/env python3
"""
create_bundles.py — package arc posts into dispatcher-ready bundles.

Usage:
    python scripts/create_bundles.py \
        --arc four-hundred-dollars-vegas-lazy \
        --slug lou-vegas-lazy \
        --start 2026-08-22

The script:
- reads post_01..07 from output/drafts/<arc>/
- creates marketing/content/{date}-{slug}-{N}/ for each post
- writes substack.md, meta.json, and stub files for the full content shape
  (substack_note_morning.md, substack_note_afternoon.md,
   substack_note_evening.md, medium.md, bluesky.md, x.md, x_queue.json)
- leaves title blank in meta.json — fill before pushing

Bundle shape follows CONTENT_CONTRACT.md.
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from typing import Optional


POST_TYPES = {1: "free", 2: "free", 3: "free", 4: "free", 5: "free", 6: "free", 7: "free"}

NOTE_MORNING_STUB = """\
# Morning Note — {date}

Dropped a new one today.

{{substack_url}}

{teaser}

— Lou
"""

NOTE_AFTERNOON_STUB = """\
# Afternoon Note — {date}

{question}

— Lou
"""

NOTE_EVENING_STUB = """\
# Evening Note — {date}

[Provocative gambling / prediction markets question tied to today's arc theme]

— Lou
"""

BLUESKY_STUB = """\
# Bluesky — {date}

[Under 200 chars. Native. Links to article if needed: {{substack_url}}]

— Lou
"""

X_STUB = """\
# X Posts — {date}

[6-8 posts. First 1-2 may carry {{substack_url}}. Each under 200 chars. Stagger through the day.]

1. Hook
2. Story beat
3. Data / line movement
4. Hot take
5. Question
6. Observation
"""

X_QUEUE_STUB = {
    "date": "",
    "slug": "",
    "posts": []
}

MEDIUM_STUB = """\
# Medium Export — {date}

[500-800 word teaser. Substack CTA at end: {{substack_url}}]
"""


def find_post_file(arc_dir: str, post_num: int, arc_slug: str) -> Optional[str]:
    pattern = re.compile(
        rf"post_{post_num:02d}_(free|paid)_.*\.md$"
    )
    for fname in os.listdir(arc_dir):
        if pattern.match(fname) and fname.endswith(".md"):
            return os.path.join(arc_dir, fname)
    return None


def extract_frontmatter(content: str) -> dict:
    meta = {}
    if not content.startswith("---"):
        return meta
    end = content.find("---", 3)
    if end == -1:
        return meta
    block = content[3:end].strip()
    for line in block.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta


def make_meta(bundle_path: str, slug_base: str, post_num: int,
              arc_slug: str, scheduled_date: str, post_type: str,
              teaser: str) -> dict:
    post_slug = f"{slug_base}-{post_num:02d}"
    post_id = f"{scheduled_date}-{post_slug}"
    return {
        "bundle_path": bundle_path,
        "post_id": post_id,
        "product": "confessionsofaloser",
        "slug": post_slug,
        "title": "",
        "status": "ready",
        "scheduled_date": scheduled_date,
        "scheduled_time": "07:00",
        "timezone": "America/New_York",
        "arc": arc_slug,
        "post_number": post_num,
        "post_type": post_type,
        "teaser": teaser,
        "substack_tags": [],
        "channels": {
            "substack": "ready",
            "substack_note": {
                "base": "substack_note.md",
                "files": [
                    "substack_note_morning.md",
                    "substack_note_afternoon.md",
                    "substack_note_evening.md"
                ],
                "items": [
                    {"slot": "morning", "file": "substack_note_morning.md", "status": "ready"},
                    {"slot": "afternoon", "file": "substack_note_afternoon.md", "status": "ready"},
                    {"slot": "evening", "file": "substack_note_evening.md", "status": "ready"}
                ]
            },
            "substack_notes": {
                "items": [
                    {"slot": "morning", "file": "substack_note_morning.md", "status": "ready"},
                    {"slot": "afternoon", "file": "substack_note_afternoon.md", "status": "ready"},
                    {"slot": "evening", "file": "substack_note_evening.md", "status": "ready"}
                ]
            },
            "medium": "ready" if post_num == 1 else "skip",
            "bluesky": "stub",
            "x": "stub"
        }
    }


def write_bundle(bundle_dir: str, post_content: str, meta: dict,
                 post_num: int, scheduled_date: str, teaser: str):
    os.makedirs(bundle_dir, exist_ok=True)

    with open(os.path.join(bundle_dir, "substack.md"), "w") as f:
        f.write(post_content)

    with open(os.path.join(bundle_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    morning_q = f"[Question drawn from today's article — what does this post make you think about?]"
    afternoon_q = f"[Question directly from the core tension in today's article]"

    note_morning = NOTE_MORNING_STUB.format(date=scheduled_date, teaser=teaser)
    note_afternoon = NOTE_AFTERNOON_STUB.format(date=scheduled_date, question=afternoon_q)
    note_evening = NOTE_EVENING_STUB.format(date=scheduled_date)

    base_note = note_morning

    for fname, content in [
        ("substack_note.md", base_note),
        ("substack_note_morning.md", note_morning),
        ("substack_note_afternoon.md", note_afternoon),
        ("substack_note_evening.md", note_evening),
        ("bluesky.md", BLUESKY_STUB.format(date=scheduled_date)),
        ("x.md", X_STUB.format(date=scheduled_date)),
    ]:
        with open(os.path.join(bundle_dir, fname), "w") as f:
            f.write(content)

    x_queue = dict(X_QUEUE_STUB)
    x_queue["date"] = scheduled_date
    x_queue["slug"] = meta["slug"]
    with open(os.path.join(bundle_dir, "x_queue.json"), "w") as f:
        json.dump(x_queue, f, indent=2)

    if post_num == 1:
        with open(os.path.join(bundle_dir, "medium.md"), "w") as f:
            f.write(MEDIUM_STUB.format(date=scheduled_date))


def main():
    parser = argparse.ArgumentParser(description="Create dispatcher bundles from arc posts.")
    parser.add_argument("--arc", required=True, help="Arc folder name under output/drafts/")
    parser.add_argument("--slug", required=True, help="Short slug, e.g. lou-vegas-lazy")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD for post 1")
    args = parser.parse_args()

    arc_dir = os.path.join("output", "drafts", args.arc)
    if not os.path.isdir(arc_dir):
        raise SystemExit(f"Arc folder not found: {arc_dir}")

    start_date = datetime.strptime(args.start, "%Y-%m-%d")

    print(f"\nArc:   {args.arc}")
    print(f"Slug:  {args.slug}")
    print(f"Start: {args.start}")
    print()

    for post_num in range(1, 8):
        post_date = start_date + timedelta(days=post_num - 1)
        date_str = post_date.strftime("%Y-%m-%d")
        post_type = POST_TYPES[post_num]

        post_file = find_post_file(arc_dir, post_num, args.arc)
        if not post_file:
            print(f"  [skip] post {post_num:02d} — no file found in {arc_dir}")
            continue

        with open(post_file) as f:
            post_content = f.read()

        fm = extract_frontmatter(post_content)
        teaser = fm.get("teaser", "")

        bundle_name = f"{date_str}-{args.slug}-{post_num:02d}"
        bundle_dir = os.path.join("marketing", "content", bundle_name)
        bundle_path = f"marketing/content/{bundle_name}"

        meta = make_meta(
            bundle_path=bundle_path,
            slug_base=args.slug,
            post_num=post_num,
            arc_slug=args.arc,
            scheduled_date=date_str,
            post_type=post_type,
            teaser=teaser,
        )

        write_bundle(bundle_dir, post_content, meta, post_num, date_str, teaser)
        print(f"  [ok]   {bundle_name}  ({post_type})")

    print(f"\nDone. Fill in titles in each meta.json before pushing.\n")


if __name__ == "__main__":
    main()
