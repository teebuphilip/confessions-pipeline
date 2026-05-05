#!/usr/bin/env python3
"""
confessions-pipeline: generate_arc.py
Lou Zerr / The Reluctant Adult: Confessions From A Loser

Pipeline:
1. Generate 7-post arc with anti-AI rules
2. Per-post passes: AI detection, readability, coherence
3. AITA pass: conflict, self-reflection, debatable verdict
4. Arc-level readability pass
5. Output: RTF (Substack-ready), Medium teasers, X posts, AITA

Two intake modes:
  --event   : "I did X, stayed for Y, it cost me Z" — life memory trigger
  --seed    : raw paragraph dump — thought/observation trigger
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

# File paths
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
HEADER_FILE = ROOT_DIR / "louzerr.header.txt"
FOOTER_FILE = ROOT_DIR / "louzerr.footer.txt"
STATE_FILE = ROOT_DIR / "state.json"

# Load header/footer templates
def load_template(filepath: Path) -> str:
    if filepath.exists():
        return filepath.read_text().strip()
    return ""

HEADER_TEMPLATE = load_template(HEADER_FILE)
FOOTER_TEMPLATE = load_template(FOOTER_FILE)

# =============================================================================
# PROMPTS
# =============================================================================

SYSTEM_PROMPT = """You are the ghostwriter for Lou Zerr, author of "The Reluctant Adult: Confessions From A Loser."

Lou is a 55-year-old man who has made approximately nine hundred and forty three mistakes in his life — personal, professional, financial, social. He is still alive, barely functional, and considers this a miracle. He writes so others can avoid being like him.

AI generates fictional but emotionally true details — no real names, no real places, no identifying information.

Lou's voice:
- Dry, self-aware, darkly funny without trying to be
- Never preachy. Never a framework. Never "5 lessons I learned"
- Talks like a guy telling a story at a bar at 11pm, not a LinkedIn influencer
- Short punchy sentences mixed with longer ones that unravel slowly
- Self-deprecating but not self-pitying — there's a difference
- The humor comes from brutal honesty, not jokes
- Signs off every post as "— Lou"

CRITICAL: AVOID AI-SOUNDING LANGUAGE
Your writing must NOT sound like AI. Avoid these tells at all costs:

1. BANNED PHRASES — never use:
   - "dive into", "delve", "unpack", "shed light", "navigate", "landscape"
   - "it's important to note/remember", "certainly", "based on the information"
   - "journey", "resonate", "empower", "at the end of the day", "in today's world"
   - "everyone wants to", "it goes without saying", "without further ado"
   - "have you ever wondered", "now this might make you wonder"
   - "you have the power to", "it's okay to", "remember that"
   - "Ah, yes", "however, for most people", "if you have ever wondered"

2. AVOID constant parallelism — "It's not about X, it's about Y" is AI cancer. Never use this structure.

3. AVOID hedging — cut words like "typically", "more often than not", "might be", "may", "perhaps"

4. MIX sentence length — short punchy. Then longer. Then short again. Like this.

5. MIX voice — 1st, 2nd, 3rd person as natural in storytelling

6. BE SPECIFIC — names, numbers, sensory details. Generic = AI.

7. NO CLEAN ENDINGS — real life doesn't wrap up neatly

8. NO LISTS unless absolutely necessary — diving into bullet points is an AI tell

9. DON'T TELL how to feel — MAKE them feel it through specific scenes

10. OCCASIONAL IMPERFECTION is human — too clean is suspicious

11. NO COLONS IN TITLES — except for Post 6 "What I Should Have Done:" and Post 7 "The Tail:"

12. AVOID blogging clichés — these are AI cancer

Return ONLY valid JSON. No preamble. No markdown fences."""

ARC_PROMPT = """Given this failure input from Lou:

INPUT TYPE: {input_type}
INPUT: {user_input}

Generate a full 7-post arc.

POST STRUCTURE:
Posts 1-3 are FREE. Posts 4-7 are PAID.
Each post must be:
- Minimum 600 words. Do not summarize. Live inside the moment.
- Written in first person, past tense
- One specific scene per post — not a summary of events
- Emotionally honest, never melodramatic
- End with a one-line tease for the next post

Post 1: The setup. The moment it started.
Post 2: The first year. When he already knew.
Post 3: The middle. How he rationalized staying.
Post 4: The bottom. One specific terrible moment.
Post 5: The crawl out. Every coward move included.
Post 6: The playbook. Concrete rules. No metaphors. Title starts with "What I Should Have Done:"
Post 7: The tail. What it still costs him today. Title starts with "The Tail:"

PER POST METADATA:

TAGS (5-8 Substack tags):
Specific, searchable, relevant to that post's content.

TEASER (one sentence, 15 words max):
The most uncomfortable truth from that post. Punchy. No fluff. Works as a standalone hook.

X POST (max 280 characters):
Must be PROVOCATIVE — stop the scroll, spark interest, make people react.
Rules:
- Hook in the first 5 words — must stop the scroll
- Emotional gut punch in the middle
- Conversational, blunt, slightly unhinged
- No hashtags
- End with "— Lou"
- Must feel like a real person tweeting at 2am, not a content calendar
- BAD: "I stayed in a bad marriage for 20 years. Here's what I learned."
- GOOD: "I cried on a bathroom floor at 47 because I was too scared to leave at 28. The math finally worked. — Lou"
- BETTER: "My wife told me she loved me every day for 20 years. I believed her for maybe 3 of them. — Lou"

SUBREDDIT (one per post):
The single best subreddit for that specific post's content. Include:
- Subreddit name
- Why it fits this post specifically
- Suggested post title for that subreddit
- Any subreddit-specific rules to be aware of

SUBSTACK NOTES (2 per post):
Substack Notes are short-form posts for discovery. Generate 2 Notes per article:

NOTE_1_TEASER (morning post, drives to article):
- 1-3 sentences max
- Tease the story, create curiosity
- Can reference "full story drops today" or link context
- Personal, Lou's voice, not salesy
- Example: "Fail #2: I spent 5 years trying to impress a man who never noticed. Tomorrow I tell you about the job I took to make my father proud. Spoiler: he still doesn't know what I do for a living. — Lou"

NOTE_2_ENGAGEMENT (afternoon post, sparks conversation):
- Question or confession that invites replies
- Does NOT need to link to article
- Goal: get people talking, algorithm rewards replies
- Personal, relatable, slightly vulnerable
- Example: "What's the longest you've stayed somewhere you knew you should leave? I have a number. It's embarrassing. — Lou"

ARC-LEVEL OUTPUTS:

ARC_SUBREDDITS (5 subreddits):
The 5 best subreddits for the overall arc theme. Include subreddit name, why it fits, and which post works best there.

AITA_POST:
Adapt the core story into a full AITA-format Reddit post. 300-400 words. First person.

CRITICAL AITA RULES (post gets removed if you violate these):
- Must be asking for JUDGMENT on a SPECIFIC CONFLICT with a SPECIFIC PERSON
- Must be a conflict Lou is CURRENTLY dealing with or CONSIDERING dealing with
- NOT feelings, NOT life regrets, NOT relationship advice, NOT a rant
- The arc is history. The AITA is the PRESENT-DAY CONFLICT that history created.
- Must include "Why I might be the asshole:" section — acknowledge the other side, make verdict debatable
- End with: "AITA for [specific action] against [specific person]?"

AITA STRUCTURE:
[Story - the current conflict, 300-400 words]

Why I might be the asshole: [Lou acknowledges the other person's perspective, why his action could be seen as wrong]

AITA for [specific action] against [specific person]?

GOOD AITA EXAMPLES:
- "My sister called me last week to tell me I ruined our family. I told her the truth about why I stayed. AITA for finally telling her?"
- "AITA for telling my aunt at her 70th birthday that her crying 30 years ago ruined my life?"

BAD AITA (will get removed):
- "I stayed in a bad marriage for 20 years" (reflection, not current conflict)

MEDIUM_ARTICLE:
A full Medium article (500-800 words) that:
- Uses the Lou Zerr byline and voice
- Hooks with the most compelling moment from the arc
- Tells enough of the story to create investment, but stops before the payoff
- Leaves readers NEEDING to know what happened
- Ends with clear CTA: "Read the full 7-part story on my Substack"
- Does NOT give away the ending or the lessons
- Feels like a standalone piece that happens to have more

Structure:
1. Hook (the gut punch moment)
2. Setup (how Lou got there)
3. The turn (when things went wrong)
4. The cliffhanger (stop before resolution)
5. CTA to Substack

DO NOT include the actual Substack URL - we'll add that in post-processing.

ARC_SUMMARY (2-3 sentences):
What this arc is about. Used for product descriptions.

Return this exact JSON structure:

{{
  "arc_title": "short title for this failure arc",
  "arc_slug": "kebab-case-slug",
  "arc_summary": "2-3 sentence summary of the arc",
  "failure_type": "personal|professional|financial|social|relationship",
  "emotional_core": "one sentence — what this is really about underneath",
  "gut_punch": "the single most painful truth in this arc",
  "medium_article": "500-800 word Medium article with hook, setup, turn, cliffhanger, CTA",
  "arc_subreddits": [
    {{
      "subreddit": "r/subreddit_name",
      "why_it_fits": "explanation",
      "best_post": 1
    }}
  ],
  "aita_post": "full AITA post text with Why I might be the asshole section",
  "posts": [
    {{
      "number": 1,
      "tier": "free",
      "title": "post title",
      "hook": "first line — must make them keep reading",
      "body": "full post body in Lou's voice, 600+ words",
      "tease": "one line tease for next post",
      "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
      "teaser": "15-word punchy uncomfortable truth",
      "x_post": "280 char max PROVOCATIVE X post ending with — Lou",
      "subreddit": {{
        "name": "r/subreddit_name",
        "why_it_fits": "explanation",
        "suggested_title": "title for this subreddit",
        "rules_to_know": "relevant rules"
      }},
      "note_1_teaser": "1-3 sentence teaser for morning, drives to article",
      "note_2_engagement": "question or confession for afternoon, sparks replies"
    }}
  ]
}}
"""

# =============================================================================
# VERIFICATION PROMPTS
# =============================================================================

AI_DETECTION_PROMPT = """You are a ruthless editor. Your only job is to detect and destroy AI-generated language.

Read the following post and flag every sentence that sounds like it was written by an AI, a content marketer, or a LinkedIn thought leader.

FLAG anything that:
- Uses journey, navigate, resonate, empower, dive in, delve, unpack, shed light, it's okay to, at the end of the day, in today's world, or any similar corporate filler
- Summarizes instead of showing a specific moment
- Tells the reader how to feel instead of making them feel it
- Uses passive voice to avoid accountability
- Sounds like advice from someone who has never failed
- Uses metaphors that are generic — "life is a journey", "turn the page", "close that chapter"
- Has more than one exclamation point
- Starts a sentence with "Remember" or "Know that" or "It's important to"
- Wraps up too neatly — real life doesn't have clean endings
- Could have been written by anyone — if it has no specific detail it's AI
- Uses "It's not about X, it's about Y" parallelism
- Uses hedging words: typically, might be, perhaps, more often than not

For every flagged sentence, provide:
- The original sentence
- Why it's AI
- A rewritten version in Lou Zerr's voice

Lou Zerr's voice: 55yo, made every mistake, darkly funny, specific scenes, never inspirational, uncomfortable honesty, 2am insomnia energy.

VERDICT (pick one):
- SOUNDS_HUMAN — post it as-is
- NEEDS_WORK — fixable, here are the specific rewrites
- AI_SLOP — too far gone, needs full rewrite

POST TO VERIFY:
{post_content}

Return JSON:
{{
  "verdict": "SOUNDS_HUMAN|NEEDS_WORK|AI_SLOP",
  "flags": [
    {{
      "original": "flagged sentence",
      "reason": "why it's AI",
      "rewrite": "fixed version"
    }}
  ],
  "rewritten_body": "full rewritten body if NEEDS_WORK or AI_SLOP, otherwise null"
}}
"""

READABILITY_PROMPT = """You are an editor checking this post for readability.

Check for:
- Awkward sentences that don't flow when read aloud
- Sentences that are too long or convoluted
- Unclear pronoun references
- Jarring transitions between paragraphs
- Repetitive sentence structures
- Words or phrases that feel forced

POST TO CHECK:
{post_content}

Return JSON:
{{
  "readable": true|false,
  "issues": [
    {{
      "sentence": "the problematic sentence",
      "issue": "what's wrong",
      "fix": "suggested fix"
    }}
  ],
  "rewritten_body": "full rewritten body if not readable, otherwise null"
}}
"""

COHERENCE_PROMPT = """You are an editor checking this post for internal coherence.

Check for:
- Details that contradict each other
- Timeline inconsistencies
- Facts that don't make sense together
- Character actions that don't match their described personality
- Logical gaps in the narrative

POST TO CHECK:
{post_content}

Return JSON:
{{
  "coherent": true|false,
  "issues": [
    {{
      "problem": "description of the inconsistency",
      "fix": "how to resolve it"
    }}
  ],
  "rewritten_body": "full rewritten body if not coherent, otherwise null"
}}
"""

AITA_VERIFICATION_PROMPT = """You are verifying an AITA post follows Reddit rules.

RULES:
1. Must ask for judgment on a SPECIFIC CONFLICT with a SPECIFIC PERSON
2. Must be a CURRENT conflict, not historical reflection
3. Must NOT be: feelings, life regrets, relationship advice, rants
4. Must include "Why I might be the asshole:" section
5. Verdict must be genuinely debatable (not obvious NTA or YTA)
6. Must end with "AITA for [action] against [person]?"

AITA POST:
{aita_post}

Return JSON:
{{
  "valid": true|false,
  "issues": [
    "list of rule violations"
  ],
  "has_current_conflict": true|false,
  "has_specific_person": true|false,
  "has_self_reflection": true|false,
  "verdict_debatable": true|false,
  "rewritten_aita": "rewritten AITA post if invalid, otherwise null"
}}
"""

ARC_READABILITY_PROMPT = """You are checking the narrative flow across all 7 posts in this arc.

Check for:
- Emotional arc builds properly from Post 1 to Post 7
- No jarring transitions between posts
- Details stay consistent across posts
- Callbacks work (things set up early pay off later)
- Post 7 lands the gut punch set up in Post 1
- Each post tease properly leads to the next post
- Voice stays consistent throughout

ARC POSTS:
{arc_posts}

Return JSON:
{{
  "flows_well": true|false,
  "issues": [
    {{
      "posts": [1, 2],
      "problem": "description of the flow issue",
      "fix": "how to resolve"
    }}
  ],
  "consistency_issues": [
    {{
      "detail": "the inconsistent detail",
      "appears_in": [1, 4],
      "contradiction": "how it contradicts"
    }}
  ]
}}
"""

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"next_mistake_number": 1, "arcs_generated": []}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_and_increment_mistake_number() -> int:
    state = load_state()
    num = state["next_mistake_number"]
    state["next_mistake_number"] = num + 1
    save_state(state)
    return num

def record_arc(mistake_number: int, arc: dict):
    state = load_state()
    state["arcs_generated"].append({
        "mistake_number": mistake_number,
        "arc_title": arc["arc_title"],
        "arc_slug": arc["arc_slug"],
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "generated"
    })
    save_state(state)

# =============================================================================
# GENERATION
# =============================================================================

def call_claude(system: str, prompt: str, model: str = "claude-opus-4-7", max_tokens: int = 16000) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    # strip markdown fences
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return raw

def generate_arc(input_type: str, user_input: str) -> dict:
    prompt = ARC_PROMPT.format(input_type=input_type, user_input=user_input)
    print(f"[generate] Creating 7-post arc from {input_type}...")
    raw = call_claude(SYSTEM_PROMPT, prompt)
    return json.loads(raw)

# =============================================================================
# VERIFICATION PASSES
# =============================================================================

def verify_ai_detection(post: dict) -> dict:
    """Check post for AI-sounding language."""
    content = f"TITLE: {post['title']}\n\nHOOK: {post['hook']}\n\nBODY:\n{post['body']}\n\nTEASE: {post['tease']}"
    prompt = AI_DETECTION_PROMPT.format(post_content=content)
    raw = call_claude("You are a ruthless AI detection editor.", prompt, model="claude-sonnet-4-20250514", max_tokens=4000)
    return json.loads(raw)

def verify_readability(post: dict) -> dict:
    """Check post for readability issues."""
    content = f"TITLE: {post['title']}\n\nHOOK: {post['hook']}\n\nBODY:\n{post['body']}\n\nTEASE: {post['tease']}"
    prompt = READABILITY_PROMPT.format(post_content=content)
    raw = call_claude("You are a readability editor.", prompt, model="claude-sonnet-4-20250514", max_tokens=4000)
    return json.loads(raw)

def verify_coherence(post: dict) -> dict:
    """Check post for internal coherence."""
    content = f"TITLE: {post['title']}\n\nHOOK: {post['hook']}\n\nBODY:\n{post['body']}\n\nTEASE: {post['tease']}"
    prompt = COHERENCE_PROMPT.format(post_content=content)
    raw = call_claude("You are a coherence editor.", prompt, model="claude-sonnet-4-20250514", max_tokens=4000)
    return json.loads(raw)

def verify_aita(aita_post: str) -> dict:
    """Verify AITA post follows Reddit rules."""
    prompt = AITA_VERIFICATION_PROMPT.format(aita_post=aita_post)
    raw = call_claude("You are an AITA post validator.", prompt, model="claude-sonnet-4-20250514", max_tokens=4000)
    return json.loads(raw)

def verify_arc_flow(posts: list) -> dict:
    """Check narrative flow across all 7 posts."""
    arc_posts = ""
    for p in posts:
        arc_posts += f"\n--- POST {p['number']} ({p['tier'].upper()}) ---\n"
        arc_posts += f"TITLE: {p['title']}\n"
        arc_posts += f"HOOK: {p['hook']}\n"
        arc_posts += f"BODY: {p['body'][:500]}...\n"  # truncate for token savings
        arc_posts += f"TEASE: {p['tease']}\n"

    prompt = ARC_READABILITY_PROMPT.format(arc_posts=arc_posts)
    raw = call_claude("You are an arc flow editor.", prompt, model="claude-sonnet-4-20250514", max_tokens=4000)
    return json.loads(raw)

def apply_fixes(post: dict, ai_result: dict, read_result: dict, cohere_result: dict) -> dict:
    """Apply fixes from verification passes to a post."""
    # Priority: coherence > readability > AI detection
    if cohere_result.get("rewritten_body"):
        post["body"] = cohere_result["rewritten_body"]
    elif read_result.get("rewritten_body"):
        post["body"] = read_result["rewritten_body"]
    elif ai_result.get("rewritten_body"):
        post["body"] = ai_result["rewritten_body"]
    return post

# =============================================================================
# RTF OUTPUT
# =============================================================================

def text_to_rtf(text: str) -> str:
    """Convert plain text to RTF format."""
    # Escape special RTF characters
    text = text.replace('\\', '\\\\')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')

    # Convert markdown-style formatting
    # Bold: **text** -> \b text\b0
    text = re.sub(r'\*\*(.+?)\*\*', r'\\b \1\\b0 ', text)
    # Italic: *text* -> \i text\i0
    text = re.sub(r'\*(.+?)\*', r'\\i \1\\i0 ', text)

    # Convert newlines to RTF paragraph breaks
    text = text.replace('\n\n', '\\par\\par\n')
    text = text.replace('\n', '\\par\n')

    # Convert em dashes
    text = text.replace('—', '\\emdash ')

    # Convert arrow
    text = text.replace('→', '-> ')

    return text

def generate_rtf(post: dict, mistake_number: int, header: str, footer: str) -> str:
    """Generate RTF content for a post."""
    # Fill in header template
    filled_header = header.format(
        mistake_number=mistake_number,
        post_number=post['number']
    )

    # Build content
    content = f"""{filled_header}

{post['title']}

{post['hook']}

{post['body']}

{post['tease']}

— Lou

---

{footer}
"""

    rtf_body = text_to_rtf(content)

    # Wrap in RTF document structure
    rtf = r"""{\rtf1\ansi\deff0
{\fonttbl{\f0 Georgia;}{\f1 Arial;}}
{\colortbl;\red0\green0\blue0;}
\f0\fs24
""" + rtf_body + r"""
}"""

    return rtf

# =============================================================================
# SAVE OUTPUTS
# =============================================================================

def save_arc(arc: dict, output_dir: Path, mistake_number: int, verifications: dict):
    slug = arc["arc_slug"]
    arc_dir = output_dir / slug
    arc_dir.mkdir(parents=True, exist_ok=True)

    # Save full arc JSON
    with open(arc_dir / "arc.json", "w") as f:
        json.dump(arc, f, indent=2)

    # Save verifications
    with open(arc_dir / "verifications.json", "w") as f:
        json.dump(verifications, f, indent=2)

    # Generate publish schedule
    base_date = datetime.now() + timedelta(days=3)
    schedule = []

    for i, post in enumerate(arc["posts"]):
        publish_date = base_date + timedelta(days=i * 3)
        post_num = post['number']
        tier = post['tier']
        base_name = f"post_{post_num:02d}_{tier}_{slug}"

        # =================================================================
        # 1. RTF file (Substack article - paste ready)
        # =================================================================
        rtf_filename = f"{base_name}.rtf"
        rtf_content = generate_rtf(post, mistake_number, HEADER_TEMPLATE, FOOTER_TEMPLATE)
        with open(arc_dir / rtf_filename, "w") as f:
            f.write(rtf_content)

        # =================================================================
        # 2. MD file (reference with all assets)
        # =================================================================
        md_filename = f"{base_name}.md"
        tags_str = ', '.join(post.get('tags', []))
        subreddit = post.get('subreddit', {})

        md_content = f"""---
arc: {arc['arc_title']}
mistake: {mistake_number} of 943
post: {post_num} of 7
tier: {tier.upper()}
title: {post['title']}
scheduled: {publish_date.strftime('%Y-%m-%d')}
author: Lou Zerr
tags: {tags_str}
teaser: {post.get('teaser', '')}
---

# {post['title']}

*{HEADER_TEMPLATE.format(mistake_number=mistake_number, post_number=post_num)}*

{post['hook']}

{post['body']}

*{post['tease']}*

— Lou

---

{FOOTER_TEMPLATE}
"""
        with open(arc_dir / md_filename, "w") as f:
            f.write(md_content)

        # =================================================================
        # 3. X Post file (standalone, copy-paste to X)
        # =================================================================
        x_filename = f"{base_name}_x.md"
        x_content = f"""# X Post for: {post['title']}

Post this to X/Twitter.

---

{post.get('x_post', 'N/A')}
"""
        with open(arc_dir / x_filename, "w") as f:
            f.write(x_content)

        # =================================================================
        # 4. Reddit file (standalone, includes subreddit in filename)
        # =================================================================
        subreddit_name = subreddit.get('name', 'r/unknown').replace('r/', '').replace('/', '_')
        reddit_filename = f"{base_name}_reddit_{subreddit_name}.md"
        reddit_content = f"""# Reddit Post for: {post['title']}

**Subreddit:** {subreddit.get('name', 'N/A')}
**Suggested Title:** {subreddit.get('suggested_title', 'N/A')}
**Rules to know:** {subreddit.get('rules_to_know', 'N/A')}

---

## Post Content

{subreddit.get('suggested_title', post['title'])}

{post['hook']}

{post['body'][:1500]}...

[Read the full story on my Substack]

— Lou
"""
        with open(arc_dir / reddit_filename, "w") as f:
            f.write(reddit_content)

        # =================================================================
        # 5. Substack Note 1 (Morning - Teaser)
        # =================================================================
        note1_filename = f"substack_notes_post_{post_num:02d}_1.md"
        note1_content = f"""# Substack Note 1 (Morning - Teaser)

**Post:** {post['title']}
**When:** Morning (with article, X, Reddit)
**Purpose:** Drive to article

---

{post.get('note_1_teaser', 'N/A')}
"""
        with open(arc_dir / note1_filename, "w") as f:
            f.write(note1_content)

        # =================================================================
        # 6. Substack Note 2 (Afternoon - Engagement)
        # =================================================================
        note2_filename = f"substack_notes_post_{post_num:02d}_2.md"
        note2_content = f"""# Substack Note 2 (Afternoon - Engagement)

**Post:** {post['title']}
**When:** Afternoon
**Purpose:** Spark conversation (no link needed)

---

{post.get('note_2_engagement', 'N/A')}
"""
        with open(arc_dir / note2_filename, "w") as f:
            f.write(note2_content)

        # =================================================================
        # Schedule entry
        # =================================================================
        schedule.append({
            "post": post_num,
            "tier": tier,
            "title": post['title'],
            "publish_date": publish_date.strftime('%Y-%m-%d'),
            "files": {
                "article_rtf": rtf_filename,
                "article_md": md_filename,
                "x_post": x_filename,
                "reddit": reddit_filename,
                "note_1": note1_filename,
                "note_2": note2_filename
            },
            "tags": post.get('tags', []),
            "subreddit": subreddit.get('name', '')
        })

        print(f"  [post {post_num}] {tier.upper()} — {post['title']} (6 files)")

    # Save schedule
    with open(arc_dir / "schedule.json", "w") as f:
        json.dump(schedule, f, indent=2)

    # Save AITA post
    aita_post = arc.get('aita_post', '')
    if aita_post:
        with open(arc_dir / "aita_post.md", "w") as f:
            f.write(f"# AITA Post for: {arc['arc_title']}\n\n{aita_post}")

    # Save Medium article (one per arc, weekly post)
    medium_article = arc.get('medium_article', arc.get('medium_teaser', ''))
    if medium_article:
        medium_content = f"""# {arc['arc_title']}

*I've made 943 serious mistakes in my life. I'm documenting every one of them so you don't have to make the same ones. My name is Lou Zerr. This is mistake #{mistake_number}.*

---

{medium_article}

---

## Read the Full Story

This is Part 1 of a 7-part series. The full arc — including the bottom, the crawl out, and what I should have done — is on my Substack.

**→ [Read the full 7-part story on Substack](https://confessionsofaloser.substack.com)**

---

*Follow me here on Medium for more confessions, or subscribe to my Substack for the complete stories.*

— Lou
"""
        with open(arc_dir / "medium_article.md", "w") as f:
            f.write(medium_content)

    # Save arc-level subreddits
    arc_subreddits = arc.get('arc_subreddits', [])
    if arc_subreddits:
        with open(arc_dir / "subreddits.json", "w") as f:
            json.dump(arc_subreddits, f, indent=2)

    # Print summary
    total_files = 7 * 6 + 3  # 6 per post + arc.json + aita + medium_teaser
    print(f"\n[done] Arc saved to: {arc_dir}")
    print(f"[files] {total_files} files generated (6 per post + arc files)")
    print(f"[arc] {arc['arc_title']}")
    print(f"[mistake] #{mistake_number} of 943")
    print(f"[core] {arc['emotional_core']}")
    print(f"[gut punch] {arc['gut_punch']}")

    return arc_dir

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline(input_type: str, user_input: str, output_dir: Path, skip_verify: bool = False):
    """Run the full generation and verification pipeline."""

    # Get mistake number
    mistake_number = get_and_increment_mistake_number()
    print(f"[pipeline] Generating Mistake #{mistake_number}")

    # Step 1: Generate arc
    arc = generate_arc(input_type, user_input)

    verifications = {
        "posts": [],
        "aita": None,
        "arc_flow": None
    }

    if not skip_verify:
        # Step 2: Per-post verification passes
        print("\n[verify] Running per-post verification passes...")
        for post in arc["posts"]:
            print(f"  [post {post['number']}] Checking...")

            # AI detection
            ai_result = verify_ai_detection(post)
            verdict = ai_result.get("verdict", "UNKNOWN")
            print(f"    AI: {verdict}")

            # Readability
            read_result = verify_readability(post)
            readable = "OK" if read_result.get("readable", True) else "ISSUES"
            print(f"    Readability: {readable}")

            # Coherence
            cohere_result = verify_coherence(post)
            coherent = "OK" if cohere_result.get("coherent", True) else "ISSUES"
            print(f"    Coherence: {coherent}")

            # Apply fixes if needed
            if verdict != "SOUNDS_HUMAN" or not read_result.get("readable", True) or not cohere_result.get("coherent", True):
                post = apply_fixes(post, ai_result, read_result, cohere_result)
                print(f"    [fixed] Applied rewrites")

            verifications["posts"].append({
                "post_number": post['number'],
                "ai_detection": ai_result,
                "readability": read_result,
                "coherence": cohere_result
            })

        # Step 3: AITA verification
        print("\n[verify] Checking AITA post...")
        aita_result = verify_aita(arc.get("aita_post", ""))
        verifications["aita"] = aita_result
        if not aita_result.get("valid", False):
            print(f"  AITA: INVALID — {aita_result.get('issues', [])}")
            if aita_result.get("rewritten_aita"):
                arc["aita_post"] = aita_result["rewritten_aita"]
                print(f"  [fixed] Applied AITA rewrite")
        else:
            print(f"  AITA: VALID")

        # Step 4: Arc-level readability
        print("\n[verify] Checking arc flow...")
        arc_result = verify_arc_flow(arc["posts"])
        verifications["arc_flow"] = arc_result
        if arc_result.get("flows_well", True):
            print(f"  Arc flow: OK")
        else:
            print(f"  Arc flow: ISSUES — {len(arc_result.get('issues', []))} problems found")

    # Step 5: Save outputs
    print("\n[save] Writing output files...")
    arc_dir = save_arc(arc, output_dir, mistake_number, verifications)

    # Record in state
    record_arc(mistake_number, arc)

    # Print schedule
    print(f"\n[schedule]")
    schedule = json.load(open(arc_dir / "schedule.json"))
    for s in schedule:
        print(f"  {s['publish_date']} — [{s['tier'].upper()}] {s['title']}")

    return arc_dir

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate a 7-post arc for Confessions of a Loser")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--event", type=str, help="Life event: describe what happened, why you stayed, what it cost")
    group.add_argument("--seed", type=str, help="Raw paragraph seed: a thought or observation to mine")
    group.add_argument("--event-file", type=str, help="Path to a .txt file with your life event")
    group.add_argument("--seed-file", type=str, help="Path to a .txt file with your paragraph seed")

    parser.add_argument("--output", type=str, default="output/drafts", help="Output directory")
    parser.add_argument("--skip-verify", action="store_true", help="Skip verification passes (faster, riskier)")

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

    run_pipeline(input_type, user_input, output_dir, skip_verify=args.skip_verify)

if __name__ == "__main__":
    main()
