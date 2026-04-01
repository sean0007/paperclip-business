#!/usr/bin/env python3
"""
Finance Metrics Agent — paperclip-business
==========================================

Purpose: Update KPI scoreboard, classify signals, track revenue.
This script is the entry point for the Finance Metrics Paperclip agent.

Usage:
  python3 scripts/finance_metrics_agent.py

Adapter config:
  Command: /opt/homebrew/bin/python3
  Args: scripts/finance_metrics_agent.py
"""

import json
import os
import subprocess
import sqlite3
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path("/Users/aihelper/paperclip-business")
TRADING_DB = Path("/Users/aihelper/openclaw-memory/trading.db")
SCOREBOARD = WORKSPACE / "KPI_SCOREBOARD.md"
EXPERIMENTS = WORKSPACE / "ACTIVE_EXPERIMENTS.md"

def get_trading_desk_stats():
    """Read P&L from trading desk."""
    try:
        conn = sqlite3.connect(str(TRADING_DB))
        cur = conn.cursor()
        
        # Today's stats
        today = date.today().isoformat()
        cur.execute("""
            SELECT capital, daily_pnl, trades_count 
            FROM daily_stats WHERE date = ?
            ORDER BY date DESC LIMIT 1
        """, (today,))
        row = cur.fetchone()
        
        # Total all-time
        cur.execute("SELECT SUM(pnl), COUNT(*) FROM trades")
        total = cur.fetchone()
        
        # Win rate
        cur.execute("SELECT COUNT(*) FROM trades WHERE pnl > 0")
        wins = cur.fetchone()[0] or 0
        total_trades = total[1] or 0
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        conn.close()
        return {
            "capital": row[0] if row else 10000,
            "daily_pnl": row[1] if row else 0,
            "today_trades": row[2] if row else 0,
            "total_pnl": total[0] or 0,
            "total_trades": total_trades,
            "win_rate": win_rate
        }
    except Exception as e:
        return {"error": str(e)}


def read_experiments():
    """Read active experiments."""
    if not EXPERIMENTS.exists():
        return []
    try:
        content = EXPERIMENTS.read_text()
        # Parse markdown table
        experiments = []
        lines = content.split("\n")
        for line in lines:
            if line.startswith("|") and "Experiment" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 4:
                    experiments.append({
                        "name": parts[0],
                        "channel": parts[1],
                        "status": parts[2],
                        "signals": parts[3],
                        "revenue": parts[4] if len(parts) > 4 else "$0"
                    })
        return experiments
    except Exception as e:
        return []


def classify_signal_strength(experiments):
    """Count signals by strength."""
    weak = medium = strong = 0
    for exp in experiments:
        sig = exp.get("signals", "0").upper()
        if "STRONG" in sig or "★★★" in sig:
            strong += 1
        elif "MEDIUM" in sig or "★★" in sig:
            medium += 1
        elif "WEAK" in sig or "★" in sig or sig not in ["$0", "0", "NONE"]:
            weak += 1
    return {"weak": weak, "medium": medium, "strong": strong}


def update_scoreboard(trading_stats, experiments, signal_counts):
    """Update KPI scoreboard file."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Read existing scoreboard
    if SCOREBOARD.exists():
        content = SCOREBOARD.read_text()
    else:
        content = "# KPI SCOREBOARD — paperclip-business\n\n"
    
    # Find the trading desk section or add it
    trading_section = f"""
## Trading Desk (seans Trading Desk Co.)
- Updated: {today}
- Capital: ${trading_stats.get('capital', 10000):,.2f}
- Total P&L: ${trading_stats.get('total_pnl', 0):.2f}
- Total Trades: {trading_stats.get('total_trades', 0)}
- Win Rate: {trading_stats.get('win_rate', 0):.1f}%
- Daily P&L: ${trading_stats.get('daily_pnl', 0):.2f}
"""
    
    # Update or add section
    if "## Trading Desk" in content:
        # Replace existing trading desk section
        start = content.find("## Trading Desk")
        end = content.find("\n## ", start + 1)
        if end == -1:
            content = content[:start] + trading_section
        else:
            content = content[:start] + trading_section + content[end:]
    else:
        content += trading_section
    
    # Add experiment summary
    exp_summary = f"""
## Active Experiments Summary
- Updated: {today}
- Total Active: {len(experiments)}
- Strong Signals (7d): {signal_counts['strong']}
- Medium Signals (7d): {signal_counts['medium']}
- Weak Signals (7d): {signal_counts['weak']}
"""
    
    if "## Active Experiments Summary" in content:
        start = content.find("## Active Experiments Summary")
        end = content.find("\n## ", start + 1)
        if end == -1:
            content = content[:start] + exp_summary
        else:
            content = content[:start] + exp_summary + content[end:]
    else:
        content += exp_summary
    
    SCOREBOARD.write_text(content)
    return True


def run():
    print(f"[FinanceMetrics] {datetime.now().isoformat()} — Running")
    
    # Get trading desk data
    trading = get_trading_desk_stats()
    if "error" in trading:
        print(f"[FinanceMetrics] Error reading trading DB: {trading['error']}")
    else:
        print(f"[FinanceMetrics] Trading: Capital=${trading.get('capital', 0):,.2f}, "
              f"P&L=${trading.get('total_pnl', 0):.2f}, "
              f"Trades={trading.get('total_trades', 0)}, "
              f"WinRate={trading.get('win_rate', 0):.1f}%")
    
    # Get experiments
    experiments = read_experiments()
    print(f"[FinanceMetrics] {len(experiments)} experiments read")
    
    # Classify signals
    signals = classify_signal_strength(experiments)
    print(f"[FinanceMetrics] Signals: weak={signals['weak']}, "
          f"medium={signals['medium']}, strong={signals['strong']}")
    
    # Update scoreboard
    update_scoreboard(trading, experiments, signals)
    print(f"[FinanceMetrics] Scoreboard updated: {SCOREBOARD}")
    
    print("[FinanceMetrics] NO_REPLY — done")


if __name__ == "__main__":
    run()
