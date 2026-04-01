#!/usr/bin/env python3
"""
Product Builder Agent — paperclip-business
==========================================

Purpose: Landing pages, sales copy, digital assets, offer pages.
This script is the entry point for the Product Builder Paperclip agent.

Usage:
  python3 scripts/product_builder_agent.py

Adapter config:
  Command: /opt/homebrew/bin/python3
  Args: scripts/product_builder_agent.py
"""

import json
import os
import subprocess
import sqlite3
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path("/Users/aihelper/paperclip-business")
QUEUE_FILE = WORKSPACE / ".product_builder_queue.json"
AFFILIATE_REPO = Path("/Users/aihelper/paperclip-affiliate")

def get_dispatch_tasks():
    """Check for dispatched tasks from CEO."""
    if not QUEUE_FILE.exists():
        return []
    try:
        content = QUEUE_FILE.read_text()
        tasks = json.loads(content)
        return tasks if isinstance(tasks, list) else []
    except Exception:
        return []


def mark_task_done(task_id):
    """Mark a task as completed."""
    tasks = get_dispatch_tasks()
    tasks = [t for t in tasks if t.get("id") != task_id]
    if tasks:
        QUEUE_FILE.write_text(json.dumps(tasks, indent=2))
    elif QUEUE_FILE.exists():
        QUEUE_FILE.unlink()


def check_affiliate_site():
    """Check the current affiliate site status."""
    if not AFFILIATE_REPO.exists():
        print("[ProductBuilder] Affiliate repo not found at ~/paperclip-affiliate")
        return
    
    try:
        pages_dir = AFFILIATE_REPO / "pages"
        if pages_dir.exists():
            pages = list(pages_dir.glob("*.html"))
            print(f"[ProductBuilder] Affiliate site: {len(pages)} pages found")
            for page in pages[:5]:
                print(f"  - {page.name}")
        else:
            print("[ProductBuilder] No pages/ directory in affiliate repo")
    except Exception as e:
        print(f"[ProductBuilder] Error checking affiliate site: {e}")


def run():
    print(f"[ProductBuilder] {datetime.now().isoformat()} — Running heartbeat")
    
    # Check for dispatched tasks from CEO
    tasks = get_dispatch_tasks()
    if tasks:
        print(f"[ProductBuilder] Found {len(tasks)} dispatched tasks:")
        for task in tasks[:3]:
            print(f"  - [{task.get('type', 'unknown')}] {task.get('description', 'no desc')}")
            mark_task_done(task.get("id"))
    else:
        # Run default site check
        print("[ProductBuilder] No pending tasks — checking affiliate site status")
        check_affiliate_site()
    
    print("[ProductBuilder] NO_REPLY — done")


if __name__ == "__main__":
    run()
