#!/usr/bin/env python3
"""
confessions-pipeline: generate_arc.py
Lou Zerr / The Reluctant Adult: Confessions From A Loser

Two intake modes:
  --event   : "I did X, stayed for Y, it cost me Z" — life memory trigger
  --seed    : raw paragraph dump — thought/observation trigger

Output: 7 post drafts in output/drafts/<arc_slug>/
"""

import argparse
import os
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are the ghostwriter for Lou Zerr, author of "The Reluctant Adult: Confessions From A Loser."

Lou is a 55-year-old man who has made approximately nine hundred and forty three mistakes in his life — personal, professional, financial, social. He is still alive, barely functional, and considers this a miracle. He writes so others can avoid being like him.

Lou's voice:
- Dry, self-aware, darkly funny without trying to be
- Never preachy. Never a framework. Never "5 lessons I learned"
- Talks like a guy telling a story at a bar at 11pm, not a LinkedIn influencer
- Short punchy sentences mixed with longer ones that unravel slowly
- Self-deprecating but not self-pitying — there's a difference
- The humor comes from brutal honesty, not jokes
- Signs off every post as "— Lou"

Post structure rules:
- Posts 1-3 are FREE. Hook the reader, give them the setup and the disaster.
- Posts 4-7 are PAID. The real mechanics, the bottom, the crawl back, what he should have done, what it cost long term.
- Each post title should be punchy and specific — not vague
- Each post ends with a one-line tease for the next post
- Post 6 (What I Should Have Done) is the most tactical — concrete, specific, no bullshit
- Post 7 (The Tail) is the gut punch — long term cost, often unexpected

Return ONLY valid JSON. No preamble. No markdown fences."""

ARC_PROMPT = """Given this failure input from Lou:

INPUT TYPE: {input_type}
INPUT: {user_input}

Generate a full 7-post arc. Return this exact JSON structure:

{{
  "arc_title": "short title for this failure arc",
  "arc_slug": "kebab-case-slug",
  "failure_type": "personal|professional|financial|social|relationship",
  "emotional_core": "one sentence — what this is really about underneath",
  "gut_punch": "the single most painful truth in this arc",
  "posts": [
    {{
      "number": 1,
      "tier": "free",
      "title": "post title",
      "hook": "first line — must make them keep reading",
      "body": "full post body in Lou's voice, 300-500 words",
      "tease": "one line tease for next post"
    }},
    ... (all 7 posts)
  ]
}}

Posts 1-3: free tier. Posts 4-7: paid tier.
Post 6 title must start with "What I Should Have Done:"
Post 7 title must start with "The Tail:"
"""

def generate_arc(input_type: str, user_input: str) -> dict:
    prompt = ARC_PROMPT.format(input_type=input_type, user_input=user_input)
    
    print(f"[generate_arc] Generating 7-post arc from {input_type}...")
    
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = response.content[0].text.strip()
    
    # strip markdown fences if Claude adds them anyway
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    
    return json.loads(raw)

def save_arc(arc: dict, output_dir: Path):
    slug = arc["arc_slug"]
    arc_dir = output_dir / slug
    arc_dir.mkdir(parents=True, exist_ok=True)
    
    # save full arc JSON
    with open(arc_dir / "arc.json", "w") as f:
        json.dump(arc, f, indent=2)
    
    # generate publish schedule — 2 posts per week
    base_date = datetime.now() + timedelta(days=3)
    schedule = []
    post_num = 0
    
    for post in arc["posts"]:
        publish_date = base_date + timedelta(days=post_num * 3)
        post_num += 1
        
        # write individual post file
        filename = f"post_{post['number']:02d}_{post['tier']}_{slug}.md"
        filepath = arc_dir / filename
        
        content = f"""---
arc: {arc['arc_title']}
post: {post['number']} of 7
tier: {post['tier'].upper()}
title: {post['title']}
scheduled: {publish_date.strftime('%Y-%m-%d')}
author: Lou Zerr
publication: The Reluctant Adult — Confessions From A Loser
---

# {post['title']}

{post['hook']}

{post['body']}

*{post['tease']}*

— Lou
"""
        with open(filepath, "w") as f:
            f.write(content)
        
        schedule.append({
            "post": post['number'],
            "tier": post['tier'],
            "title": post['title'],
            "file": filename,
            "publish_date": publish_date.strftime('%Y-%m-%d')
        })
        
        print(f"  [post {post['number']}] {post['tier'].upper()} — {post['title']}")
    
    # save schedule
    with open(arc_dir / "schedule.json", "w") as f:
        json.dump(schedule, f, indent=2)
    
    print(f"\n[done] Arc saved to: {arc_dir}")
    print(f"[arc] {arc['arc_title']}")
    print(f"[core] {arc['emotional_core']}")
    print(f"[gut punch] {arc['gut_punch']}")
    
    return arc_dir

def main():
    parser = argparse.ArgumentParser(description="Generate a 7-post arc for Confessions of a Loser")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--event", type=str, help="Life event: describe what happened, why you stayed, what it cost")
    group.add_argument("--seed", type=str, help="Raw paragraph seed: a thought or observation to mine")
    group.add_argument("--event-file", type=str, help="Path to a .txt file with your life event")
    group.add_argument("--seed-file", type=str, help="Path to a .txt file with your paragraph seed")
    
    parser.add_argument("--output", type=str, default="output/drafts", help="Output directory")
    
    args = parser.parse_args()
    
    if args.event:
        input_type = "LIFE_EVENT"
        user_input = args.event
    elif args.seed:
        input_type = "PARAGRAPH_SEED"
        user_input = args.seed
    elif args.event_file:
        input_type = "LIFE_EVENT"
        user_input = Path(args.event_file).read_text()
    elif args.seed_file:
        input_type = "PARAGRAPH_SEED"
        user_input = Path(args.seed_file).read_text()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    arc = generate_arc(input_type, user_input)
    arc_dir = save_arc(arc, output_dir)
    
    print(f"\n[schedule]")
    schedule = json.load(open(arc_dir / "schedule.json"))
    for s in schedule:
        print(f"  {s['publish_date']} — [{s['tier'].upper()}] {s['title']}")

if __name__ == "__main__":
    main()
