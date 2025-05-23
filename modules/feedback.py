from collections import defaultdict
from typing import List, Dict

def summarize_feedback(records: List[Dict]) -> Dict:
    summary = defaultdict(lambda: {
        "focus_feedback": defaultdict(int),
        "break_feedback": defaultdict(int),
        "focus_sessions": 0
    })

    for rec in records:
        key = (rec.get("focus"), rec.get("flow"), rec.get("task"))
        summary[key]["focus_feedback"][rec.get("focus_feedback", "None")] += 1
        summary[key]["break_feedback"][rec.get("break_feedback", "None")] += 1
        summary[key]["focus_sessions"] += 1

    return summary

def calculate_total_focus_time(records: List[Dict], default_focus_minutes: int = 25) -> int:
    return len([r for r in records if "focus" in r]) * default_focus_minutes
