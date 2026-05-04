#!/usr/bin/env python3
"""
generate_ideas.py — Generate more arc ideas for Lou Zerr

Usage:
  python scripts/generate_ideas.py              # generate 10 new ideas
  python scripts/generate_ideas.py --count 5   # generate 5 new ideas
  python scripts/generate_ideas.py --decade 30s # focus on 30s mistakes
"""

import argparse
import os
import json
from datetime import datetime
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
IDEAS_FILE = ROOT_DIR / "ideas" / "seed_ideas.json"

SYSTEM_PROMPT = """You are brainstorming arc ideas for Lou Zerr, a 55-year-old man documenting his 943 life mistakes.

Lou's brand:
- Raw, honest, darkly funny
- Never preachy, never inspirational
- The cautionary tale, not the guru
- Mistakes span personal, professional, financial, social, relationship domains

Each idea needs:
- A punchy title (format: "The [Thing] I [Did/Didn't Do]")
- A one-line seed that captures the core regret
- The decade it happened (20s, 30s, 40s, 50s)
- The era name for that decade

Era names:
- 20s: The Setup Years
- 30s: The Rationalization Years
- 40s: The Damage Years
- 50s: The Reckoning Years

Ideas should be:
- Universal enough to resonate but specific enough to feel real
- NOT generic self-help topics
- Things a real person would actually regret
- Dark but not traumatic (no abuse, assault, death of children)
- The kind of thing someone would admit at 2am after too much whiskey

Return ONLY valid JSON array. No preamble."""

GENERATE_PROMPT = """Generate {count} new arc ideas for Lou Zerr.

{decade_filter}

Existing ideas (don't repeat these):
{existing_titles}

Return JSON array:
[
  {{
    "decade": "30s",
    "era": "The Rationalization Years",
    "title": "The [Something] I [Did]",
    "seed": "one line describing the core regret"
  }}
]
"""


def load_ideas() -> dict:
    if IDEAS_FILE.exists():
        return json.loads(IDEAS_FILE.read_text())
    return {"generated_date": datetime.now().strftime("%Y-%m-%d"), "source": "initial", "ideas": []}


def save_ideas(data: dict):
    IDEAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    IDEAS_FILE.write_text(json.dumps(data, indent=2))


def generate_ideas(count: int = 10, decade: str = None) -> list:
    data = load_ideas()
    existing = data.get("ideas", [])
    existing_titles = [i["title"] for i in existing]

    decade_filter = ""
    if decade:
        era_map = {
            "20s": "The Setup Years",
            "30s": "The Rationalization Years",
            "40s": "The Damage Years",
            "50s": "The Reckoning Years"
        }
        era = era_map.get(decade, "")
        decade_filter = f"Focus on mistakes from the {decade} ({era})."

    prompt = GENERATE_PROMPT.format(
        count=count,
        decade_filter=decade_filter,
        existing_titles="\n".join(f"- {t}" for t in existing_titles)
    )

    print(f"[generate] Creating {count} new ideas...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    new_ideas = json.loads(raw)

    # Assign IDs and status
    next_id = max([i.get("id", 0) for i in existing], default=0) + 1
    for idea in new_ideas:
        idea["id"] = next_id
        idea["status"] = "available"
        next_id += 1

    return new_ideas


def main():
    parser = argparse.ArgumentParser(description="Generate new arc ideas for Lou Zerr")
    parser.add_argument("--count", type=int, default=10, help="Number of ideas to generate")
    parser.add_argument("--decade", type=str, choices=["20s", "30s", "40s", "50s"], help="Focus on specific decade")
    parser.add_argument("--dry-run", action="store_true", help="Print ideas without saving")

    args = parser.parse_args()

    new_ideas = generate_ideas(count=args.count, decade=args.decade)

    print(f"\n[generated] {len(new_ideas)} new ideas:\n")
    for idea in new_ideas:
        print(f"  [{idea['decade']}] {idea['title']}")
        print(f"         {idea['seed']}\n")

    if not args.dry_run:
        data = load_ideas()
        data["ideas"].extend(new_ideas)
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        save_ideas(data)
        print(f"[saved] Total ideas: {len(data['ideas'])}")
    else:
        print("[dry-run] Ideas not saved")


if __name__ == "__main__":
    main()
