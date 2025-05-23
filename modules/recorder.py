import os
import chardet
from typing import List, Dict

RECORD_FILE = "record.txt"

def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        return chardet.detect(f.read())['encoding']

def load_records() -> List[Dict]:
    records = []
    if not os.path.exists(RECORD_FILE):
        print("[DEBUG] record.txt does not exist.")
        return records

    encoding = detect_encoding(RECORD_FILE)
    print(f"[DEBUG] Detected encoding: {encoding}")

    with open(RECORD_FILE, encoding=encoding) as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"[DEBUG] Read {len(lines)} lines from file.")

    record = {}
    for line in lines:
        print(f"[DEBUG] Processing line: {line}")
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
    print(f"[DEBUG] Parsed {len(records)} records.")
    return records
