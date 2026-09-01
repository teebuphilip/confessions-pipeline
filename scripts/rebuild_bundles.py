import os
import json
import re
from datetime import date, timedelta
from pathlib import Path

BASE = Path("/Users/teebuphilip/Documents/work/confessionsofaloser")
DRAFTS = BASE / "output" / "drafts"
CONTENT = BASE / "marketing" / "content"

ARCS = [
    ("four-hundred-dollars-vegas-lazy", "vegas-lazy", date(2026, 9, 2)),
    ("600-line-move-i-didnt-see",       "line-move",  date(2026, 9, 9)),
    ("soft-open-made-me-look-stupid",   "soft-open",  date(2026, 9, 16)),
    ("hedge-that-ate-itself",           "hedge",      date(2026, 9, 23)),
    ("the-revenge-bet",                 "revenge-bet",date(2026, 9, 30)),
    ("the-300-dollar-vibe-check",       "vibe-check", date(2026, 10, 7)),
    ("the-guessing-years",              "guessing-years", date(2026, 10, 14)),
]

MISTAKE_MAP = {
    "four-hundred-dollars-vegas-lazy": 3,
    "600-line-move-i-didnt-see":       4,
    "soft-open-made-me-look-stupid":   5,
    "hedge-that-ate-itself":           6,
    "the-revenge-bet":                 7,
    "the-300-dollar-vibe-check":       8,
    "the-guessing-years":              9,
}

ARC_TAGS = {
    "four-hundred-dollars-vegas-lazy": ["sports betting","gambling","money mistakes","confessions","Gen X","personal finance","regret"],
    "600-line-move-i-didnt-see":       ["line movement","sports betting","sharp money","gambling","confessions","predeve"],
    "soft-open-made-me-look-stupid":   ["sports betting","gambling","soft lines","confessions","Gen X","predeve"],
    "hedge-that-ate-itself":           ["hedging","sports betting","gambling math","confessions","predeve"],
    "the-revenge-bet":                 ["revenge betting","gambling","tilt","confessions","Gen X","predeve"],
    "the-300-dollar-vibe-check":       ["vibes","sports betting","gambling","confessions","prediction markets","predeve"],
    "the-guessing-years":              ["gambling","confessions","Gen X","prediction markets","predeve","betting systems"],
}

def parse_frontmatter(content):
    fm = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            block = content[3:end].strip()
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
    return fm

def find_post_file(arc_dir, post_num):
    patterns = [
        f"post_{post_num:02d}_free_*.md",
        f"post_{post_num:02d}_paid_*.md",
    ]
    for pat in patterns:
        matches = [
            f for f in arc_dir.glob(pat)
            if "_reddit_" not in f.name and not f.name.endswith("_x.md")
        ]
        if matches:
            return matches[0]
    return None

def get_teaser(fm, body):
    if "teaser" in fm:
        return fm["teaser"]
    lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("*") and not l.startswith("---")]
    for line in lines:
        if len(line) > 40:
            return line[:120].rstrip() + ("..." if len(line) > 120 else "")
    return ""

def make_morning_note(title, teaser, post_num, arc_title, mistake_num):
    return f"New post from Lou Zerr — mistake #{mistake_num} of 943, part {post_num} of 7.\n\n\"{teaser}\"\n\n{title}\n\n{{{{substack_url}}}}"

def make_afternoon_note(fm, body):
    lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("*") and not l.startswith("---") and not l.startswith("—")]
    question = ""
    for line in lines[2:]:
        if "?" in line and len(line) > 30:
            question = line
            break
    if not question:
        for line in lines[3:8]:
            if len(line) > 60:
                question = line
                break
    if not question:
        question = lines[3] if len(lines) > 3 else lines[0]
    return f"{question}\n\n{{{{substack_url}}}}"

def make_evening_note(arc_slug, post_num):
    provocations = {
        "vegas-lazy": [
            "Vegas sets lines to balance action, not to be right. How many bettors know the difference?",
            "The opening line is a guess. The closing line is a consensus. Which one are you actually betting against?",
            "If you checked one extra venue before every bet, what would that change?",
            "Sharp money moves lines. Public money moves nothing. Which side have you been on?",
            "Kalshi and FanDuel price the same game differently every week. Are you watching both?",
            "The line moved 2.5 points and nobody told you. That's not bad luck. That's information you didn't buy.",
            "What's the last bet you made in under 30 seconds? How did it go?",
        ],
        "line-move": [
            "A line that moves 3 points before kickoff is telling you something. Are you listening or ignoring?",
            "Sharp money doesn't announce itself. It just moves the number. What moved this week?",
            "If the line moves against your bet, do you chase or sit? Most people chase. Most people lose.",
            "The prediction markets saw something the sportsbooks missed. Did you check both?",
            "Line movement is public information. Most bettors treat it like noise. Are you one of them?",
            "What's the biggest line move you ever missed — and what did it cost you?",
            "Early money vs. late money. Which side are you usually on? Which side wins more?",
        ],
        "soft-open": [
            "The opening line is bait. The closing line is the truth. Which one did you bet?",
            "Soft opens exist so books can find out what sharp money thinks. You're the experiment.",
            "If you always bet early, you're helping the book set the real line. Know that?",
            "The market corrects itself by game time. Where do you sit in that correction?",
            "Prediction markets open before sportsbooks sharpen. Are you using that window?",
            "What's the dumbest 'early bird' bet you ever placed? What happened by kickoff?",
            "Vegas tests the opening. The market gives the answer. Are you reading the answer?",
        ],
        "hedge": [
            "A hedge that guarantees a loss is not a hedge. It's a fee for feeling safe.",
            "Math doesn't care about your feelings. Have you ever run the numbers before hedging?",
            "Sportsbooks love hedgers. Hedgers pay twice. Are you hedging or just paying double vig?",
            "When is hedging smart and when is it just panic? Most people can't tell the difference.",
            "If you've never lost money on a winning bet, you've never hedged badly. Has that happened to you?",
            "Prediction markets let you hedge across venues. Does that change the math?",
            "The hedge that ate itself — have you been there? What did it cost?",
        ],
        "revenge-bet": [
            "The revenge bet feels logical in the moment. It never is. Ever placed one?",
            "Tilt is real. It makes you bet faster, bigger, and stupider. What's your tell?",
            "If you lost $300 and immediately bet $400 to get it back, you didn't lose $300. You lost $700.",
            "How many of your losses came after a loss? That's the real number you should track.",
            "Prediction markets don't care that you're angry. They just take your money faster.",
            "The best bet after a bad beat is no bet. How many times have you proven that wrong?",
            "Revenge betting is just gambling with extra steps. What finally made you stop?",
        ],
        "vibe-check": [
            "Vibes are not an edge. What does your actual win rate say?",
            "A 'sharp' tip without data is just someone else's vibe. How much have you paid for those?",
            "If you can't explain why you took a line, you don't have a reason — you have a feeling.",
            "Kalshi and Polymarket disagree with sportsbooks every week. That gap is data. Are you reading it?",
            "The best bettors track everything. The worst bettors track nothing. Where are you?",
            "What's the most expensive vibe you ever trusted? What did it teach you?",
            "Measured edges beat hot takes every time. Do you have a measured edge?",
        ],
        "guessing-years": [
            "How many years did you guess before you started tracking? What did the guessing cost?",
            "The difference between a losing bettor and a winning bettor is a spreadsheet. Agree?",
            "PredEve tracks cross-venue discrepancies so you don't have to guess. What would you do with that data?",
            "If you tracked every bet for 90 days, what would the honest number say about your edge?",
            "Most bettors know their biggest wins. Almost none know their actual ROI. Do you?",
            "The guessing years end when you start writing things down. Have yours ended?",
            "What's the one number about your betting history you're afraid to calculate?",
        ],
    }
    slug_key = {
        "vegas-lazy": "vegas-lazy",
        "line-move": "line-move",
        "soft-open": "soft-open",
        "hedge": "hedge",
        "revenge-bet": "revenge-bet",
        "vibe-check": "vibe-check",
        "guessing-years": "guessing-years",
    }
    key = arc_slug
    provs = provocations.get(key, ["What did this loss actually cost you? {{substack_url}}"])
    return provs[(post_num - 1) % len(provs)] + "\n\n{{substack_url}}"

def make_bluesky(title, teaser, slug, post_num):
    short = teaser[:100] if len(teaser) > 100 else teaser
    text = f"Lou Zerr, mistake #{post_num}. {short} {{{{substack_url}}}}"
    if len(text) > 200:
        text = f"Lou Zerr. {short[:80]}... {{{{substack_url}}}}"
    return text

def make_medium(title, teaser, arc_title, mistake_num, post_num, body):
    lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("*") and not l.startswith("---") and not l.startswith("—")]
    excerpt = ""
    for line in lines[:10]:
        if len(line) > 80:
            excerpt = line
            break
    if not excerpt and lines:
        excerpt = lines[0]

    return f"""Lou Zerr has made 943 serious mistakes in his life. He's documenting every one of them.

This is mistake #{mistake_num} of 943, part {post_num} of 7: {arc_title}.

{title}

{teaser}

{excerpt}

This is the kind of story Lou writes every week at Confessions of a Loser — specific, honest, and darker than it sounds. No self-help framework. No clean endings. Just the actual thing that happened, and what it still costs.

Read the full post on Substack: {{{{substack_url}}}}"""

def make_meta(bundle_date, slug, arc_folder, post_num, title, teaser, arc_title, mistake_num, substack_tags, morning_note, afternoon_note, evening_note, bluesky_text):
    post_id = f"{bundle_date}-{slug}"
    return {
        "bundle_path": f"marketing/content/{post_id}",
        "post_id": post_id,
        "product": "confessionsofaloser",
        "slug": slug,
        "title": title,
        "teaser": teaser,
        "arc": arc_title,
        "mistake_number": mistake_num,
        "post_number": post_num,
        "scheduled_date": str(bundle_date),
        "scheduled_time": "02:00",
        "timezone": "America/New_York",
        "status": "ready",
        "main_article_file": "substack.md",
        "primary_channel": "substack",
        "substack_tags": substack_tags,
        "channels": {
            "substack": {
                "file": "substack.md",
                "link_policy": "site_cta",
                "role": "primary_source_article",
                "status": "ready"
            },
            "substack_note": {
                "file": "substack_note.md",
                "files": [
                    "substack_note.md",
                    "substack_note_morning.md",
                    "substack_note_afternoon.md",
                    "substack_note_evening.md"
                ],
                "items": [
                    {"slot": "morning",   "file": "substack_note_morning.md",   "link_policy": "hook", "status": "ready"},
                    {"slot": "afternoon", "file": "substack_note_afternoon.md", "link_policy": "hook", "status": "ready"},
                    {"slot": "evening",   "file": "substack_note_evening.md",   "link_policy": "hook", "status": "ready"},
                ],
                "link_policy": "hook",
                "status": "ready"
            },
            "substack_note_morning": {
                "family": "substack_note",
                "file": "substack_note_morning.md",
                "link_policy": "hook",
                "slot": "morning",
                "status": "ready"
            },
            "substack_note_afternoon": {
                "family": "substack_note",
                "file": "substack_note_afternoon.md",
                "link_policy": "hook",
                "slot": "afternoon",
                "status": "ready"
            },
            "substack_note_evening": {
                "family": "substack_note",
                "file": "substack_note_evening.md",
                "link_policy": "hook",
                "slot": "evening",
                "status": "ready"
            },
            "substack_notes": {
                "files": [
                    "substack_note_morning.md",
                    "substack_note_afternoon.md",
                    "substack_note_evening.md"
                ],
                "items": [
                    {"slot": "morning",   "file": "substack_note_morning.md",   "link_policy": "hook", "status": "ready"},
                    {"slot": "afternoon", "file": "substack_note_afternoon.md", "link_policy": "hook", "status": "ready"},
                    {"slot": "evening",   "file": "substack_note_evening.md",   "link_policy": "hook", "status": "ready"},
                ],
                "link_policy": "hook",
                "role": "slot_aware_note_selector",
                "status": "ready"
            },
            "medium": {
                "file": "medium.md",
                "link_policy": "canonical_article",
                "role": "secondary_long_form_export",
                "status": "ready"
            },
            "bluesky": {
                "file": "bluesky.md",
                "link_policy": "optional_link",
                "max_chars": 200,
                "status": "ready"
            }
        },
        "hook_qa": {
            "substack_note": {
                "candidates": [
                    morning_note,
                    afternoon_note,
                    f"Lou Zerr, mistake #{mistake_num}, part {post_num} of 7. {{{{substack_url}}}}"
                ],
                "selected": morning_note
            },
            "bluesky": {
                "candidates": [bluesky_text],
                "selected": bluesky_text
            }
        },
        "narrative": {
            "arc": arc_title,
            "mistake": f"#{mistake_num} of 943",
            "post": f"{post_num} of 7",
            "teaser": teaser
        }
    }

def build_all():
    built = 0
    for arc_folder, arc_slug, arc_start in ARCS:
        arc_dir = DRAFTS / arc_folder
        mistake_num = MISTAKE_MAP[arc_folder]
        tags = ARC_TAGS[arc_folder]

        for post_num in range(1, 8):
            bundle_date = arc_start + timedelta(days=post_num - 1)
            slug = f"lou-{arc_slug}-{post_num}"
            dir_name = f"{bundle_date}-{slug}"
            bundle_dir = CONTENT / dir_name
            bundle_dir.mkdir(parents=True, exist_ok=True)

            src_file = find_post_file(arc_dir, post_num)
            if not src_file:
                print(f"MISSING: {arc_folder} post {post_num}")
                continue

            raw = src_file.read_text()
            fm = parse_frontmatter(raw)

            title = fm.get("title", f"Part {post_num}")
            arc_title = fm.get("arc", arc_folder.replace("-", " ").title())
            teaser = get_teaser(fm, raw)

            # Strip frontmatter from body for substack.md
            body = raw
            if raw.startswith("---"):
                end = raw.find("---", 3)
                if end != -1:
                    body = raw[end+3:].strip()

            morning = make_morning_note(title, teaser, post_num, arc_title, mistake_num)
            afternoon = make_afternoon_note(fm, body)
            evening = make_evening_note(arc_slug, post_num)
            bluesky = make_bluesky(title, teaser, arc_slug, mistake_num)
            medium = make_medium(title, teaser, arc_title, mistake_num, post_num, body)
            meta = make_meta(bundle_date, slug, arc_folder, post_num, title, teaser, arc_title, mistake_num, tags, morning, afternoon, evening, bluesky)

            (bundle_dir / "substack.md").write_text(raw)
            (bundle_dir / "substack_note.md").write_text(morning)
            (bundle_dir / "substack_note_morning.md").write_text(morning)
            (bundle_dir / "substack_note_afternoon.md").write_text(afternoon)
            (bundle_dir / "substack_note_evening.md").write_text(evening)
            (bundle_dir / "medium.md").write_text(medium)
            (bundle_dir / "bluesky.md").write_text(bluesky)
            (bundle_dir / "meta.json").write_text(json.dumps(meta, indent=2))

            print(f"Built: {dir_name}")
            built += 1

    print(f"\nTotal bundles built: {built}")

if __name__ == "__main__":
    build_all()
