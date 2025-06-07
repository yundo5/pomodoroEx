# modules/recorder.py
import os
from datetime import datetime

RECORD_FILE = "record.txt"

def save_task(data):
    """사용자가 세션 시작 전에 입력한 작업 정보를 저장"""
    task = data.get('task', '').strip()
    goal = data.get('goal', '').strip()
    work = data.get('workMinutes', '')
    rest = data.get('breakMinutes', '')
    repeat = data.get('repeatCount', '')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(RECORD_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"작업: {task}\n")
        f.write(f"목표: {goal}\n")
        f.write(f"예상 시간: {work}분 {rest}분 {repeat}회\n")

def save_feedback(data):
    """세션 종료 후 사용자 자기평가 내용을 저장"""
    progress = data.get("progress", "")
    goal_achieve = data.get("goal_achieve", "")
    time_eval = data.get("time_eval", "")
    focus = data.get("focus", "")
    comment = data.get("comment", "").strip()

    with open(RECORD_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n작업진행: {progress}\n")
        f.write(f"목표달성: {goal_achieve}\n")
        f.write(f"시간사용: {time_eval}\n")
        f.write(f"집중도: {focus}\n")
        if comment:
            f.write(f"기타의견: {comment}\n")
        f.write("-" * 30 + "\n")
