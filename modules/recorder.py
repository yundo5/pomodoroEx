import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

RECORD_FILE = "record.txt"

# ──────────────────────────────────────────
# 피드백 평가 항목별 점수 매핑
# ──────────────────────────────────────────
FEEDBACK_SCORE_MAP = {
    "progress": {
        "계획대로 모두 완료했어요.": 5,
        "거의 다 했어요.": 4,
        "절반 정도 진행했어요.": 3,
        "아직 시작 단계예요. / 많이 남았어요.": 2,
        "": 1 # 평가 없음
    },
    "goal_achieve": {
        "목표를 완전히 달성했어요!": 5,
        "목표에 많이 가까워졌어요.": 4,
        "어느 정도 진척이 있었어요.": 3,
        "아쉽지만, 목표 달성은 아직이에요.": 2,
        "": 1 # 평가 없음
    },
    "time_eval": {
        "시간을 매우 잘 활용했어요.": 5,
        "대부분의 시간을 효과적으로 사용했어요.": 4,
        "시간 활용이 보통이었어요.": 3,
        "시간 낭비가 좀 있었어요.": 2,
        "": 1 # 평가 없음
    },
    "focus": {
        "아주 만족스럽게 집중했어요!": 5,
        "대체로 집중을 잘 한 편이에요.": 4,
        "보통 수준으로 집중했어요.": 3,
        "집중하기 조금 어려웠어요.": 2,
        "": 1 # 평가 없음
    }
}

# ──────────────────────────────────────────
# 세션 시작 시 기록
# ──────────────────────────────────────────
def save_task(data):
    """사용자가 세션 시작 전에 입력한 작업 정보를 JSON Line으로 저장"""
    work_minutes = int(data.get('workMinutes', 25))
    break_minutes = int(data.get('breakMinutes', 5))
    repeat_count = int(data.get('repeatCount', 1))
    focus_units = int(data.get('focusUnits', 1))

    record_data = {
        'timestamp': datetime.now().isoformat(), # ISO 8601 형식
        'record_type': 'session_start', # 레코드 유형 명시
        'task_category': data.get('task_category', '미분류').strip(),
        'task': data.get('task', '').strip(),
        'goal': data.get('goal', '').strip(), # 폼에는 없지만 데이터 구조 유지를 위해 저장
        'workMinutes': work_minutes,
        'breakMinutes': break_minutes,
        'repeatCount': repeat_count,
        'focusUnits': focus_units,
    }

    with open(RECORD_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record_data, ensure_ascii=False) + "\n")

# ──────────────────────────────────────────
# 세션 종료 후 피드백 기록
# ──────────────────────────────────────────
def save_feedback(data, task_category_from_session):
    """세션 종료 후 사용자 자기평가 내용을 JSON Line으로 저장"""
    original_work_minutes  = int(data.get('workMinutes', 25))
    original_break_minutes = int(data.get('breakMinutes', 5))
    original_repeat_count  = int(data.get('repeatCount', 1))
    original_focus_units = int(data.get('focusUnits', 1)) 

    progress_str   = data.get("progress", "").strip()
    goal_achieve_str = data.get("goal_achieve", "").strip()
    time_eval_str  = data.get("time_eval", "").strip()
    focus_str      = data.get("focus", "").strip()
    comment_str    = data.get("comment", "").strip()

    progress_score   = FEEDBACK_SCORE_MAP["progress"].get(progress_str, 1)
    goal_achieve_score = FEEDBACK_SCORE_MAP["goal_achieve"].get(goal_achieve_str, 1)
    time_eval_score  = FEEDBACK_SCORE_MAP["time_eval"].get(time_eval_str, 1)
    focus_score      = FEEDBACK_SCORE_MAP["focus"].get(focus_str, 1)

    feedback_data = {
        'timestamp': datetime.now().isoformat(),
        'record_type': 'feedback',
        'task_category': task_category_from_session,
        'task': data.get('task', '').strip(),
        'goal': data.get('goal', '').strip(),
        'workMinutes': original_work_minutes,
        'breakMinutes': original_break_minutes,
        'repeatCount': original_repeat_count,
        'focusUnits': original_focus_units,
        
        'progress': progress_str,
        'goal_achieve': goal_achieve_str,
        'time_eval': time_eval_str,
        'focus': focus_str,
        'comment': comment_str,

        'progress_score': progress_score,
        'goal_achieve_score': goal_achieve_score,
        'time_eval_score': time_eval_score,
        'focus_score': focus_score,
    }

    with open(RECORD_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(feedback_data, ensure_ascii=False) + "\n")

# ──────────────────────────────────────────
# 기록 파일 파싱
# ──────────────────────────────────────────
def get_all_records():
    """record.txt 파일에서 모든 JSON Line 레코드를 리스트 딕셔너리 형태로 반환"""
    records = []
    if not os.path.exists(RECORD_FILE):
        return records

    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    records.append(data)
                except json.JSONDecodeError as e:
                    print(f"오류: record.txt에서 JSON 라인을 파싱할 수 없습니다: {line} - 오류: {e}")
                    continue
    return records

# ──────────────────────────────────────────
# 통계 계산
# ──────────────────────────────────────────
def calculate_stats(all_records):
    """세션 데이터를 기반으로 각종 통계 계산 (feedback 레코드만 사용)"""
    daily_focus_counts = defaultdict(lambda: {k: 0 for k in FEEDBACK_SCORE_MAP["focus"].keys()})
    task_types_counts = Counter()
    pomodoro_settings_counts = Counter()
    
    daily_summary_data = defaultdict(lambda: {"achieved_count": 0, "total_count": 0, "focus_sum": 0, "goal_rate": 0, "avg_focus_score": 0})
    hourly_focus_data = defaultdict(lambda: {"focus_sum": 0, "count": 0})
    weekday_focus_data = defaultdict(lambda: {"focus_sum": 0, "count": 0})
    category_stats_data = defaultdict(lambda: {"sessions": 0, "achieved": 0, "total_focus": 0, "count": 0})
    weekly_growth_data = defaultdict(lambda: {"focus_sum": 0, "focus_cnt": 0, "goal_total": 0, "goal_hit": 0})

    for record in all_records:
        if record.get('record_type') != 'feedback':
            continue

        try:
            dt = datetime.fromisoformat(record['timestamp'])
        except ValueError:
            print(f"오류: 기록에서 잘못된 타임스탬프 형식: {record['timestamp']}")
            continue

        date_str = dt.strftime("%Y-%m-%d")
        y_week   = dt.strftime("%Y-%W")
        hour     = dt.hour
        weekday  = dt.weekday()

        focus_score = record.get('focus_score', 1) 
        focus_str = record.get('focus', '') 
        
        goal_achieve_score = record.get('goal_achieve_score', 1)
        goal_ok = (goal_achieve_score >= 4)


        # ── 날짜별 집중도 (막대 그래프용)
        daily_focus_counts[date_str][focus_str] += 1

        # ── 달력 기반 하루 요약 (daily_summary_data)
        daily_summary_data[date_str]["total_count"] += 1
        daily_summary_data[date_str]["focus_sum"]   += focus_score
        if goal_ok:
            daily_summary_data[date_str]["achieved_count"] += 1
        
        # ── 시간대별 집중도 (hourly_focus_data)
        hourly_focus_data[hour]["focus_sum"] += focus_score
        hourly_focus_data[hour]["count"] += 1

        # ── 요일별 집중도 (weekday_focus_data)
        weekday_focus_data[weekday]["focus_sum"] += focus_score
        weekday_focus_data[weekday]["count"] += 1

        # ── 작업 유형 (task_types_counts)
        task = record.get('task', '미지정')
        task_types_counts[task] += 1

        # ── 포모도로 세팅 (pomodoro_settings_counts)
        setting_key = f"{record.get('workMinutes', '?')}분 {record.get('breakMinutes', '?')}분 {record.get('repeatCount', '?')}회"
        pomodoro_settings_counts[setting_key] += 1

        # ── 카테고리 (category_stats_data)
        cat = record.get('task_category', '미분류')
        category_stats_data[cat]["sessions"] += 1
        category_stats_data[cat]["total_focus"] += focus_score
        category_stats_data[cat]["count"] += 1
        if goal_ok:
            category_stats_data[cat]["achieved"] += 1
        
        # ── 주간 성장 데이터 (weekly_growth_data)
        wg = weekly_growth_data[y_week]
        wg["focus_sum"]   += focus_score
        wg["focus_cnt"]   += 1
        wg["goal_total"]  += 1
        if goal_ok:
            wg["goal_hit"] += 1

    # ── 후처리: 평균/달성률 등 계산
    for date_str, data in daily_summary_data.items():
        if data["total_count"] > 0:
            data["avg_focus_score"] = round(data["focus_sum"] / data["total_count"], 2)
            data["goal_rate"] = round((data["achieved_count"] / data["total_count"]) * 100, 2)
        else:
            data["avg_focus_score"] = 0
            data["goal_rate"] = 0
    
    for hour, data in hourly_focus_data.items():
        if data["count"] > 0:
            data["avg_focus"] = round(data["focus_sum"] / data["count"], 2)
        else:
            data["avg_focus"] = 0

    for weekday, data in weekday_focus_data.items():
        if data["count"] > 0:
            data["avg_focus"] = round(data["focus_sum"] / data["count"], 2)
        else:
            data["avg_focus"] = 0

    for cat, data in category_stats_data.items():
        if data["count"]:
            data["avg_focus"] = round(data["total_focus"] / data["count"], 2)
            data["goal_rate"] = round((data["achieved"] / data["sessions"]) * 100, 2) if data["sessions"] else 0
        else:
            data["avg_focus"] = 0
            data["goal_rate"] = 0
    
    weekly_summary = {
        wk: {
            "avg_focus": round(v["focus_sum"] / v["focus_cnt"], 2) if v["focus_cnt"] else 0,
            "goal_rate": round((v["goal_hit"] / v["goal_total"]) * 100, 2) if v["goal_total"] else 0
        }
        for wk, v in weekly_growth_data.items()
    }

    return {
        "daily_focus"   : dict(daily_focus_counts),
        "task_types"    : dict(task_types_counts),
        "pomodoro_settings": dict(pomodoro_settings_counts),
        "daily_summary" : dict(daily_summary_data),
        "hourly_focus"  : dict(hourly_focus_data),
        "weekday_focus" : dict(weekday_focus_data),
        "category_stats": dict(category_stats_data),
        "weekly_growth" : weekly_summary,
    }

# ──────────────────────────────────────────
# 사용자 유형 분류
# ──────────────────────────────────────────
def classify_user_type(all_records):
    """집중 시간대·길이·패턴을 바탕으로 프로필 문자열과 설명 반환 (feedback 레코드만 사용)"""
    sessions = [r for r in all_records if r.get('record_type') == 'feedback']
    
    if not sessions:
        return "데이터 부족", "아직 충분한 세션 정보가 없습니다."

    hour_counter   = Counter()
    date_set       = set()
    short_sessions = 0
    total_sessions = 0
    focus_sum      = 0
    goal_hit       = 0
    goal_total     = 0

    now = datetime.now()
    recent_border = now - timedelta(days=14)

    for s in sessions:
        try:
            dt = datetime.fromisoformat(s['timestamp'])
        except ValueError:
            continue

        hour_counter[dt.hour] += 1
        date_set.add(dt.date())

        work_m = s.get('workMinutes', 0)
        if isinstance(work_m, int) and work_m <= 15:
            short_sessions += 1

        focus_score = s.get('focus_score', 1) 
        focus_sum  += focus_score

        goal_achieve_score = s.get('goal_achieve_score', 1)
        if goal_achieve_score >= 4: # 4점 이상을 달성으로 간주
            goal_hit += 1
        goal_total += 1
        total_sessions += 1

    hour_total = sum(hour_counter.values())
    if hour_total == 0:
        return "데이터 부족", "세션 수가 너무 적습니다."

    morning_ratio = sum(hour_counter[h] for h in range(6, 11)) / hour_total
    night_ratio   = sum(hour_counter[h % 24] for h in [21, 22, 23, 0, 1, 2]) / hour_total
    avg_focus     = focus_sum / total_sessions
    avg_goal      = goal_hit / goal_total if goal_total else 0
    short_ratio   = short_sessions / total_sessions
    recent_days   = len([d for d in date_set if d >= recent_border.date()])

    if morning_ratio >= 0.30 and avg_goal >= 0.70:
        return "🌞 아침형 계획가", "오전 시간대에 계획적으로 목표를 달성하는 타입입니다."
    if night_ratio >= 0.30 and avg_focus >= 4.0:
        return "🌕 야행성 집중러", "늦은 밤에 더욱 집중력이 높아지는 타입입니다."
    if short_ratio >= 0.50:
        return "⚡ 짧게 몰입형", "짧은 세션에 강한 몰입을 보여주는 타입입니다."
    if recent_days >= 8 and avg_focus >= 3.0:
        return "📅 꾸준한 실행자", "최근 2주간 거의 매일 뽀모도로를 실천한 꾸준파입니다."

    return "🌀 산발적 실험자", "아직 뚜렷한 패턴이 없어요. 다양한 루틴을 시도해 보세요!"

# ──────────────────────────────────────────
# 포모도로 설정 제안을 위한 기본값 함수
# ──────────────────────────────────────────
def get_default_settings():
    """기본 포모도로 설정값을 반환합니다."""
    return {"workMinutes": 25, "breakMinutes": 5, "repeatCount": 1, "focusUnits": 1}

# 이 함수는 OpenAI API가 대체하므로 더 이상 app.py에서 직접 호출되지 않습니다.
def suggest_pomodoro_settings(category, task_keyword, all_records):
    """
    과거 피드백 레코드를 기반으로 포모도로 설정을 제안합니다.
    (OpenAI API가 이 역할을 수행하므로 이 함수는 더 이상 사용되지 않음)
    """
    return None

# 이 함수도 OpenAI API가 대체하므로 더 이상 app.py에서 직접 호출되지 않습니다.
def get_most_common_overall_settings(all_records):
    """(더 이상 사용되지 않음)"""
    return get_default_settings()

