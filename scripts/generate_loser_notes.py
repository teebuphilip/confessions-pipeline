#!/usr/bin/env python3
"""
generate_loser_notes.py — Generate "Loser Notes" PDF-ready summary from an arc

Usage:
  python scripts/generate_loser_notes.py --arc output/drafts/twenty-year-favor
  python scripts/generate_loser_notes.py --arc output/drafts/twenty-year-favor --format md
  python scripts/generate_loser_notes.py --arc output/drafts/twenty-year-favor --format txt
  python scripts/generate_loser_notes.py --compile  # compile all arcs into one book

Output: Loser Notes summary with:
  - Arc summary
  - The mistake in one line (gut punch)
  - 10 Loser Moves (what Lou did wrong)
  - 10 Non-Loser Moves (what to do instead)
  - The Tail (what it still costs)
  - Bottom line
"""

import argparse
import os
import json
from pathlib import Path
from datetime import datetime
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
DRAFTS_DIR = ROOT_DIR / "output" / "drafts"
NOTES_DIR = ROOT_DIR / "output" / "loser_notes"

SYSTEM_PROMPT = """You are extracting actionable lessons from Lou Zerr's confessional story arcs.

Lou Zerr is a 55-year-old man documenting his 943 life mistakes. Each arc is a 7-post story about one major mistake.

Your job: Extract the lessons into a "Loser Notes" format that someone can read in 5 minutes and walk away with concrete, actionable advice.

Voice:
- Direct, no bullshit
- Self-deprecating but useful
- "Don't be me" energy
- Concrete actions, not vague inspiration

Output must follow the exact structure provided."""

EXTRACT_PROMPT = """Analyze this 7-post arc and create "Loser Notes" — a 2-page summary with actionable takeaways.

ARC TITLE: {arc_title}
EMOTIONAL CORE: {emotional_core}
GUT PUNCH: {gut_punch}

POSTS:
{posts_content}

Generate the following sections. Be SPECIFIC and CONCRETE. Pull actual quotes and details from the posts.

1. ARC_SUMMARY (2-3 sentences): What this arc is about

2. MISTAKE_ONE_LINE: The gut punch quote that captures the whole arc (use the gut_punch or find a better one from the posts)

3. LOSER_MOVES (exactly 10): What Lou did wrong. Each one:
   - Short title (3-5 words)
   - One sentence explanation with specific detail from the arc

4. NON_LOSER_MOVES (exactly 10): What to do instead. Each one:
   - Short imperative title (3-5 words)
   - One sentence of concrete, actionable advice

5. THE_TAIL (3-5 bullets): What this mistake STILL costs Lou today. Be specific.

6. BOTTOM_LINE (3-4 short lines): The final "don't do this" punch. Punchy. No fluff.

Return as JSON:
{{
  "arc_title": "",
  "arc_summary": "",
  "mistake_one_line": "",
  "loser_moves": [
    {{"title": "", "detail": ""}}
  ],
  "non_loser_moves": [
    {{"title": "", "detail": ""}}
  ],
  "the_tail": ["", "", ""],
  "bottom_line": ["", "", ""]
}}
"""


def load_arc(arc_dir: Path) -> dict:
    """Load arc.json from directory."""
    arc_file = arc_dir / "arc.json"
    if not arc_file.exists():
        raise FileNotFoundError(f"No arc.json found in {arc_dir}")
    return json.loads(arc_file.read_text())


def extract_loser_notes(arc: dict) -> dict:
    """Use AI to extract Loser Notes from arc."""

    # Build posts content
    posts_content = ""
    for post in arc["posts"]:
        posts_content += f"\n--- POST {post['number']} ({post['tier'].upper()}): {post['title']} ---\n"
        posts_content += f"Hook: {post['hook']}\n"
        posts_content += f"Body: {post['body']}\n"
        posts_content += f"Tease: {post['tease']}\n"

    prompt = EXTRACT_PROMPT.format(
        arc_title=arc.get("arc_title", "Unknown"),
        emotional_core=arc.get("emotional_core", ""),
        gut_punch=arc.get("gut_punch", ""),
        posts_content=posts_content
    )

    print(f"[extract] Generating Loser Notes for: {arc.get('arc_title', 'Unknown')}...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    if raw.endswith("```"):
        raw = raw[:-3]

    return json.loads(raw)


def format_markdown(notes: dict) -> str:
    """Format Loser Notes as markdown."""

    md = f"""# LOSER NOTES: {notes['arc_title']}

**Arc Summary:** {notes['arc_summary']}

---

## THE MISTAKE IN ONE LINE

*"{notes['mistake_one_line']}"*

---

## THE 10 LOSER MOVES (What I Did — Don't)

"""

    for i, move in enumerate(notes['loser_moves'], 1):
        md += f"**{i}. {move['title']}** {move['detail']}\n\n"

    md += """---

## THE 10 NON-LOSER MOVES (Do This Instead)

"""

    for i, move in enumerate(notes['non_loser_moves'], 1):
        md += f"**{i}. {move['title']}** {move['detail']}\n\n"

    md += """---

## THE TAIL (What It Still Costs)

"""

    for item in notes['the_tail']:
        md += f"- {item}\n\n"

    md += """---

## THE BOTTOM LINE

"""

    for line in notes['bottom_line']:
        md += f"{line}  \n"

    md += """
— Lou

---

*From "The Reluctant Adult: Confessions From A Loser" — 943 mistakes documented so you don't have to make them.*

*→ Full arc: confessionsofaloser.substack.com*
"""

    return md


def format_text(notes: dict) -> str:
    """Format Loser Notes as plain text."""

    txt = f"""================================================================================
LOSER NOTES: {notes['arc_title']}
================================================================================

Arc Summary: {notes['arc_summary']}

--------------------------------------------------------------------------------
THE MISTAKE IN ONE LINE
--------------------------------------------------------------------------------

"{notes['mistake_one_line']}"

--------------------------------------------------------------------------------
THE 10 LOSER MOVES (What I Did — Don't)
--------------------------------------------------------------------------------

"""

    for i, move in enumerate(notes['loser_moves'], 1):
        txt += f"{i}. {move['title']}\n   {move['detail']}\n\n"

    txt += """--------------------------------------------------------------------------------
THE 10 NON-LOSER MOVES (Do This Instead)
--------------------------------------------------------------------------------

"""

    for i, move in enumerate(notes['non_loser_moves'], 1):
        txt += f"{i}. {move['title']}\n   {move['detail']}\n\n"

    txt += """--------------------------------------------------------------------------------
THE TAIL (What It Still Costs)
--------------------------------------------------------------------------------

"""

    for item in notes['the_tail']:
        txt += f"* {item}\n\n"

    txt += """--------------------------------------------------------------------------------
THE BOTTOM LINE
--------------------------------------------------------------------------------

"""

    for line in notes['bottom_line']:
        txt += f"{line}\n"

    txt += """
— Lou

================================================================================
From "The Reluctant Adult: Confessions From A Loser"
943 mistakes documented so you don't have to make them.
→ Full arc: confessionsofaloser.substack.com
================================================================================
"""

    return txt


def compile_book(output_file: Path = None) -> str:
    """Compile all Loser Notes into one book."""

    if output_file is None:
        output_file = NOTES_DIR / "THE_LOSERS_PLAYBOOK.md"

    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    # Find all loser notes
    notes_files = sorted(NOTES_DIR.glob("loser_notes_*.json"))

    if not notes_files:
        print("[compile] No loser notes found. Generate some first.")
        return ""

    book = f"""# THE LOSER'S PLAYBOOK

## 943 Mistakes So You Don't Have To

**By Lou Zerr**

*I've made 943 serious mistakes in my life. I'm documenting every one of them so you don't have to make the same ones.*

---

**Published:** {datetime.now().strftime('%Y')}

**Website:** confessionsofaloser.substack.com

---

# TABLE OF CONTENTS

"""

    # Build TOC
    all_notes = []
    for i, notes_file in enumerate(notes_files, 1):
        notes = json.loads(notes_file.read_text())
        all_notes.append(notes)
        book += f"{i}. {notes['arc_title']}\n"

    book += "\n---\n\n# INTRODUCTION\n\n"
    book += """I'm Lou Zerr. I'm 55 years old. I've made approximately 943 serious mistakes in my life — personal, professional, financial, social. I am still alive, barely functional, and I consider this a miracle.

This book is not inspiration. This book is a warning.

Each chapter is one mistake. Each mistake comes with two lists: what I did (don't), and what you should do instead. I learned all of this the hard way. You don't have to.

The girl needs to eat. Don't be a loser.

— Lou

---

"""

    # Add each arc
    for i, notes in enumerate(all_notes, 1):
        book += f"# CHAPTER {i}: {notes['arc_title'].upper()}\n\n"
        book += format_markdown(notes)
        book += "\n---\n\n"

    # Write book
    output_file.write_text(book)
    print(f"[compile] Book written to: {output_file}")
    print(f"[compile] {len(all_notes)} chapters, ~{len(all_notes) * 2} pages")

    return book


def main():
    parser = argparse.ArgumentParser(description="Generate Loser Notes from an arc")
    parser.add_argument("--arc", type=str, help="Path to arc directory")
    parser.add_argument("--format", type=str, choices=["md", "txt", "json"], default="md", help="Output format")
    parser.add_argument("--compile", action="store_true", help="Compile all notes into one book")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of file")

    args = parser.parse_args()

    if args.compile:
        book = compile_book()
        if args.stdout:
            print(book)
        return

    if not args.arc:
        print("Error: --arc required (or use --compile)")
        return

    arc_dir = Path(args.arc)
    if not arc_dir.is_absolute():
        arc_dir = ROOT_DIR / arc_dir

    # Load arc
    arc = load_arc(arc_dir)

    # Extract notes
    notes = extract_loser_notes(arc)

    # Save JSON
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    slug = arc.get("arc_slug", "unknown")
    json_file = NOTES_DIR / f"loser_notes_{slug}.json"
    json_file.write_text(json.dumps(notes, indent=2))
    print(f"[saved] {json_file}")

    # Format output
    if args.format == "md":
        output = format_markdown(notes)
        ext = "md"
    elif args.format == "txt":
        output = format_text(notes)
        ext = "txt"
    else:
        output = json.dumps(notes, indent=2)
        ext = "json"

    if args.stdout:
        print(output)
    else:
        output_file = NOTES_DIR / f"loser_notes_{slug}.{ext}"
        output_file.write_text(output)
        print(f"[saved] {output_file}")


if __name__ == "__main__":
    main()
