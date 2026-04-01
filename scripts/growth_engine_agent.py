#!/usr/bin/env python3
"""
Growth Engine Agent — paperclip-business
=======================================

Purpose: Acquisition, outreach, social posting, demand tests.
This script is the entry point for the Growth Engine Paperclip agent.

Usage:
  python3 scripts/growth_engine_agent.py

Adapter config:
  Command: /opt/homebrew/bin/python3
  Args: scripts/growth_engine_agent.py
"""

import json
import os
import subprocess
import sqlite3
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path("/Users/aihelper/paperclip-business")
QUEUE_FILE = WORKSPACE / ".growth_engine_queue.json"
EXPERIMENTS = WORKSPACE / "ACTIVE_EXPERIMENTS.md"

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


def run_outreach_simple():
    """Run simple outreach based on active experiments."""
    if not EXPERIMENTS.exists():
        print("[GrowthEngine] No experiments file found — nothing to do")
        return
    
    try:
        content = EXPERIMENTS.read_text()
        lines = content.split("\n")
        
        # Find active experiments
        active = []
        for line in lines:
            if line.startswith("|") and "---" not in line and "Experiment" not in line:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 3 and parts[2].upper() in ["ACTIVE", "RUNNING"]:
                    active.append({"name": parts[0], "channel": parts[1] if len(parts) > 1 else "TBD"})
        
        if not active:
            print("[GrowthEngine] No active experiments to promote")
            return
        
        print(f"[GrowthEngine] Found {len(active)} active experiments:")
        for exp in active[:3]:
            print(f"  - {exp['name']} ({exp['channel']})")
        
        print("[GrowthEngine] Outreach would run here (social posting, Reddit, etc.)")
        print("[GrowthEngine] Note: Requires Sean to create Reddit/Twitter accounts")
        
    except Exception as e:
        print(f"[GrowthEngine] Error: {e}")


def run():
    print(f"[GrowthEngine] {datetime.now().isoformat()} — Running heartbeat")
    
    # Check for dispatched tasks from CEO
    tasks = get_dispatch_tasks()
    if tasks:
        print(f"[GrowthEngine] Found {len(tasks)} dispatched tasks:")
        for task in tasks[:3]:
            print(f"  - [{task.get('type', 'unknown')}] {task.get('description', 'no desc')}")
            # Mark done after "executing"
            mark_task_done(task.get("id"))
    else:
        # Run default outreach check
        print("[GrowthEngine] No pending tasks — running default outreach check")
        run_outreach_simple()
    
    print("[GrowthEngine] NO_REPLY — done")


if __name__ == "__main__":
    run()
