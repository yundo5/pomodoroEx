import os
from typing import List, Dict

RECORD_FILE = "record.txt"

def load_records() -> List[Dict]:
    records = []
    if not os.path.exists(RECORD_FILE):
        return records

    with open(RECORD_FILE, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    record = {}
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            record = {"timestamp": line[1:-1]}
        elif line.startswith("Focus Level"):
            record["focus"] = line.split(": ", 1)[1]
        elif line.startswith("Work Flow"):
            record["flow"] = line.split(": ", 1)[1]
        elif line.startswith("Task Type"):
            record["task"] = line.split(": ", 1)[1]
        elif line.startswith("Focus Duration Feedback"):
            record["focus_feedback"] = line.split(": ", 1)[1]
        elif line.startswith("Break Duration Feedback"):
            record["break_feedback"] = line.split(": ", 1)[1]
        elif line.startswith("-") and record:
            records.append(record)
            record = {}
    return records
