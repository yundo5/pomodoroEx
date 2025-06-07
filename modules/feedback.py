# modules/feedback.py
import os
import re

RECORD_FILE = "record.txt"

# 평가 항목별 점수 매핑
score_map = {
    "작업진행": {
        "완료": 5,
        "거의": 4,
        "절반": 3,
        "미진행": 2
    },
    "목표달성": {
        "완전히": 5,
        "많이": 4,
        "어느 정도": 3,
        "아직": 2
    },
    "시간사용": {
        "안에": 5,
        "조금": 4,
        "훨씬": 2,
        "빠르게": 5
    },
    "집중도": {
        "아주": 5,
        "대체로": 4,
        "보통": 3,
        "조금": 2
    }
}

def generate_stats():
    """record.txt를 읽고 평균 점수를 계산하여 반환"""
    if not os.path.exists(RECORD_FILE):
        return {"labels": [], "values": []}

    # 초기 카운트 및 점수 누적
    categories = ["작업진행", "목표달성", "시간사용", "집중도"]
    total_scores = {cat: 0 for cat in categories}
    counts = {cat: 0 for cat in categories}

    with open(RECORD_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        for cat in categories:
            if line.startswith(cat):
                for key, score in score_map[cat].items():
                    if key in line:
                        total_scores[cat] += score
                        counts[cat] += 1
                        break

    # 평균 계산
    avg_scores = []
    for cat in categories:
        if counts[cat] > 0:
            avg = round(total_scores[cat] / counts[cat], 2)
        else:
            avg = 0
        avg_scores.append(avg)

    return {
        "labels": categories,
        "values": avg_scores
    }
