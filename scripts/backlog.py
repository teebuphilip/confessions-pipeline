#!/usr/bin/env python3
"""
confessions-pipeline: backlog.py
Manage the arc backlog — add ideas, list status, mark as published

Usage:
  python scripts/backlog.py add --type event --idea "stayed in wrong job for 8 years because pension"
  python scripts/backlog.py add --type seed --idea "there is a difference between being broke and being poor"
  python scripts/backlog.py list
  python scripts/backlog.py generate --id <idea_id>
  python scripts/backlog.py status --id <idea_id> --set published
"""

import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path

BACKLOG_FILE = Path("backlog.json")

def load_backlog() -> list:
    if BACKLOG_FILE.exists():
        return json.loads(BACKLOG_FILE.read_text())
    return []

def save_backlog(backlog: list):
    BACKLOG_FILE.write_text(json.dumps(backlog, indent=2))

def make_id(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:8]

def add_idea(idea_type: str, idea_text: str):
    backlog = load_backlog()
    idea_id = make_id(idea_text)
    
    # check duplicate
    if any(i["id"] == idea_id for i in backlog):
        print(f"[skip] Already in backlog: {idea_id}")
        return
    
    entry = {
        "id": idea_id,
        "type": idea_type,  # event | seed
        "idea": idea_text,
        "status": "queued",  # queued | generating | drafted | scheduled | published
        "arc_slug": None,
        "added": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    
    backlog.append(entry)
    save_backlog(backlog)
    print(f"[added] {idea_id} — {idea_type.upper()}: {idea_text[:80]}...")

def list_backlog(status_filter: str = None):
    backlog = load_backlog()
    
    if not backlog:
        print("[empty] No ideas in backlog yet.")
        return
    
    statuses = {
        "queued": [],
        "drafted": [],
        "scheduled": [],
        "published": []
    }
    
    for item in backlog:
        s = item.get("status", "queued")
        if s not in statuses:
            statuses[s] = []
        statuses[s].append(item)
    
    for status, items in statuses.items():
        if status_filter and status != status_filter:
            continue
        if not items:
            continue
        print(f"\n[{status.upper()}] — {len(items)} ideas")
        for item in items:
            print(f"  {item['id']} | {item['type'].upper():6} | {item['idea'][:70]}")

def set_status(idea_id: str, new_status: str, arc_slug: str = None):
    backlog = load_backlog()
    for item in backlog:
        if item["id"] == idea_id:
            item["status"] = new_status
            item["updated"] = datetime.now().isoformat()
            if arc_slug:
                item["arc_slug"] = arc_slug
            save_backlog(backlog)
            print(f"[updated] {idea_id} → {new_status}")
            return
    print(f"[error] ID not found: {idea_id}")

def generate_from_backlog(idea_id: str):
    backlog = load_backlog()
    item = next((i for i in backlog if i["id"] == idea_id), None)
    
    if not item:
        print(f"[error] ID not found: {idea_id}")
        return
    
    flag = "--event" if item["type"] == "event" else "--seed"
    cmd = f'python scripts/generate_arc.py {flag} "{item["idea"]}"'
    
    print(f"[generate] Running: {cmd}")
    set_status(idea_id, "generating")
    
    import subprocess
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        set_status(idea_id, "drafted")
    else:
        set_status(idea_id, "queued")
        print("[error] Generation failed, reset to queued")

def main():
    parser = argparse.ArgumentParser(description="Manage the Confessions of a Loser arc backlog")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # add
    add_parser = subparsers.add_parser("add", help="Add an idea to the backlog")
    add_parser.add_argument("--type", choices=["event", "seed"], required=True)
    add_parser.add_argument("--idea", type=str, required=True)
    
    # list
    list_parser = subparsers.add_parser("list", help="List backlog")
    list_parser.add_argument("--status", type=str, help="Filter by status")
    
    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate arc from backlog item")
    gen_parser.add_argument("--id", type=str, required=True)
    
    # status
    status_parser = subparsers.add_parser("status", help="Update item status")
    status_parser.add_argument("--id", type=str, required=True)
    status_parser.add_argument("--set", type=str, required=True)
    status_parser.add_argument("--arc-slug", type=str)
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_idea(args.type, args.idea)
    elif args.command == "list":
        list_backlog(args.status)
    elif args.command == "generate":
        generate_from_backlog(args.id)
    elif args.command == "status":
        set_status(args.id, args.set, getattr(args, 'arc_slug', None))

if __name__ == "__main__":
    main()
