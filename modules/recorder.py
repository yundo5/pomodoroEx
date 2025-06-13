import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter

RECORD_FILE = "record.txt"

# ──────────────────────────────────────────
# 세션 시작 시 기록
# ──────────────────────────────────────────
def save_task(data):
    """사용자가 세션 시작 전에 입력한 작업 정보를 저장"""
    task           = data.get('task', '').strip()
    goal           = data.get('goal', '').strip()
    work           = data.get('workMinutes', '')
    rest           = data.get('breakMinutes', '')
    repeat         = data.get('repeatCount', '')
    focus_units    = data.get('focusUnits', '')
    task_category  = data.get('task_category', '미분류')
    timestamp      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(RECORD_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"카테고리: {task_category}\n")
        f.write(f"작업: {task}\n")
        f.write(f"목표: {goal}\n")
        f.write(f"세션 설정: {work}분 {rest}분 {repeat}회 (예상 뽀모도로: {focus_units}회)\n")

# ──────────────────────────────────────────
# 세션 종료 후 피드백 기록
# ──────────────────────────────────────────
def save_feedback(data):
    """세션 종료 후 사용자 자기평가 내용을 저장"""
    progress   = data.get("progress", "")
    goal_state = data.get("goal_achieve", "")
    time_eval  = data.get("time_eval", "")
    focus      = data.get("focus", "")
    comment    = data.get("comment", "").strip()

    # hidden 필드(세션 정보)
    original_task         = data.get('task', '')
    original_goal         = data.get('goal', '')
    original_workMinutes  = data.get('workMinutes', '')
    original_breakMinutes = data.get('breakMinutes', '')
    original_repeatCount  = data.get('repeatCount', '')
    task_category         = data.get('task_category', '미분류')

    with open(RECORD_FILE, 'a', encoding='utf-8') as f:
        f.write(f"카테고리: {task_category}\n")
        f.write(f"작업: {original_task}\n")
        f.write(f"목표: {original_goal}\n")
        f.write(f"세션 설정: {original_workMinutes}분 {original_breakMinutes}분 {original_repeatCount}회\n")
        f.write(f"작업진행: {progress}\n")
        f.write(f"목표달성: {goal_state}\n")
        f.write(f"시간사용: {time_eval}\n")
        f.write(f"집중도: {focus}\n")
        if comment:
            f.write(f"기타의견: {comment}\n")
        f.write("-" * 30 + "\n")

# ──────────────────────────────────────────
# 기록 파일 파싱
# ──────────────────────────────────────────
def get_all_sessions_data():
    """record.txt 파일에서 모든 세션 데이터를 리스트 딕셔너리 형태로 반환"""
    sessions, current = [], {}

    if not os.path.exists(RECORD_FILE):
        return sessions

    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in map(str.strip, lines):
        if not line:
            continue

        # 세션 헤더
        if line.startswith('[') and ']' in line:
            if current:
                sessions.append(current)
            current = {'timestamp': line.strip('[]')}
            continue

        # 필드별 파싱
        if line.startswith('카테고리: '):
            current['task_category'] = line.replace('카테고리: ', '')
        elif line.startswith('작업: '):
            current['task'] = line.replace('작업: ', '')
        elif line.startswith('목표: '):
            current['goal'] = line.replace('목표: ', '')
        elif line.startswith('세션 설정: '):
            setting = line.replace('세션 설정: ', '')
            try:
                parts = setting.split('분 ')
                current['work_minutes']  = int(parts[0])
                current['break_minutes'] = int(parts[1].split(' ')[0])
                current['repeat_count']  = int(parts[1].split(' ')[1].replace('회', ''))
                if '(예상 뽀모도로: ' in setting:
                    current['focus_units'] = int(
                        setting.split('(예상 뽀모도로: ')[1].replace('회)', '')
                    )
            except Exception:
                current['work_minutes'] = current['break_minutes'] = current['repeat_count'] = '?'
        elif line.startswith('작업진행: '):
            current['progress'] = line.replace('작업진행: ', '')
        elif line.startswith('목표달성: '):
            current['goal_achieve'] = line.replace('목표달성: ', '')
        elif line.startswith('시간사용: '):
            current['time_eval'] = line.replace('시간사용: ', '')
        elif line.startswith('집중도: '):
            current['focus'] = line.replace('집중도: ', '')
        elif line.startswith('기타의견: '):
            current['comment'] = line.replace('기타의견: ', '')
        elif line.startswith('-' * 30):
            if current:
                sessions.append(current)
                current = {}

    if current:
        sessions.append(current)
    return sessions

# ──────────────────────────────────────────
# 통계 계산
# ──────────────────────────────────────────
def calculate_stats(sessions):
    """세션 데이터를 기반으로 각종 통계 계산"""
    # 매핑 테이블
    focus_map = {"매우 집중": 5, "잘 집중": 4, "보통": 3, "집중 어려움": 2, "평가 없음": 1}

    daily_focus, task_types, pomodoro_settings = {}, {}, {}
    daily_summary, hourly_focus, weekday_focus = {}, {}, {}
    category_stats = {
        k: {"sessions": 0, "achieved": 0, "total_focus": 0, "count": 0}
        for k in ["공부/이해", "생산/작성", "읽기/자료 습득", "정리/관리", "기획/설계", "미분류"]
    }

    # 주간 성장 통계
    weekly_growth = defaultdict(lambda: {"focus_sum": 0, "focus_cnt": 0,
                                         "goal_total": 0, "goal_hit": 0})

    # 시간·요일 초기화
    for h in range(24):
        hourly_focus[h] = {**{k: 0 for k in focus_map}, "count": 0}
    for d in range(7):
        weekday_focus[d] = {**{k: 0 for k in focus_map}, "count": 0}

    for s in sessions:
        try:
            dt = datetime.strptime(s['timestamp'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        date_str = dt.strftime("%Y-%m-%d")
        y_week   = dt.strftime("%Y-%W")   # 주차
        hour     = dt.hour
        weekday  = dt.weekday()

        focus_str   = s.get('focus', '평가 없음')
        focus_score = focus_map.get(focus_str, 1)
        goal_ok     = (s.get('goal_achieve') == '달성')

        # ── 날짜별 집중도
        daily_focus.setdefault(date_str, {k: 0 for k in focus_map})
        daily_focus[date_str][focus_str] += 1

        # ── 날짜별 요약
        ds = daily_summary.setdefault(
            date_str, {"achieved": 0, "total": 0, "focus_sum": 0, "count": 0}
        )
        ds["total"]     += 1
        ds["count"]     += 1
        ds["focus_sum"] += focus_score
        if goal_ok:
            ds["achieved"] += 1

        # ── 시간대·요일 집중도
        hourly_focus[hour][focus_str] += 1
        hourly_focus[hour]["count"]   += 1
        weekday_focus[weekday][focus_str] += 1
        weekday_focus[weekday]["count"]   += 1

        # ── 작업 유형
        task = s.get('task', '미지정')
        task_types[task] = task_types.get(task, 0) + 1

        # ── 포모도로 세팅
        setting_key = f"{s.get('work_minutes', '?')}분 {s.get('break_minutes', '?')}분 {s.get('repeat_count', '?')}회"
        pomodoro_settings[setting_key] = pomodoro_settings.get(setting_key, 0) + 1

        # ── 카테고리
        cat = s.get('task_category', '미분류')
        if cat not in category_stats:
            cat = '미분류'
        cs = category_stats[cat]
        cs["sessions"]      += 1
        cs["total_focus"]   += focus_score
        cs["count"]         += 1
        if goal_ok:
            cs["achieved"] += 1

        # ── 주간 성장 데이터
        wg = weekly_growth[y_week]
        wg["focus_sum"]   += focus_score
        wg["focus_cnt"]   += 1
        wg["goal_total"]  += 1
        if goal_ok:
            wg["goal_hit"] += 1

    # ── 후처리: 평균/달성률 등 계산
    for d, v in daily_summary.items():
        v["avg_focus"] = v["focus_sum"] / v["count"] if v["count"] else 0
        v["goal_rate"] = (v["achieved"] / v["total"]) * 100 if v["total"] else 0

    for h in hourly_focus:
        if hourly_focus[h]["count"]:
            hourly_focus[h]["avg_focus"] = sum(
                focus_map[k] * hourly_focus[h][k] for k in focus_map
            ) / hourly_focus[h]["count"]
        else:
            hourly_focus[h]["avg_focus"] = 0

    for d in weekday_focus:
        if weekday_focus[d]["count"]:
            weekday_focus[d]["avg_focus"] = sum(
                focus_map[k] * weekday_focus[d][k] for k in focus_map
            ) / weekday_focus[d]["count"]
        else:
            weekday_focus[d]["avg_focus"] = 0

    for cat, v in category_stats.items():
        if v["count"]:
            v["avg_focus"] = v["total_focus"] / v["count"]
            v["goal_rate"] = (v["achieved"] / v["sessions"]) * 100 if v["sessions"] else 0
        else:
            v["avg_focus"] = v["goal_rate"] = 0

    weekly_summary = {
        wk: {
            "avg_focus": round(v["focus_sum"] / v["focus_cnt"], 2) if v["focus_cnt"] else 0,
            "goal_rate": round((v["goal_hit"] / v["goal_total"]) * 100, 2) if v["goal_total"] else 0
        }
        for wk, v in weekly_growth.items()
    }

    return {
        "daily_focus"   : daily_focus,
        "task_types"    : task_types,
        "pomodoro_settings": pomodoro_settings,
        "daily_summary" : daily_summary,
        "hourly_focus"  : hourly_focus,
        "weekday_focus" : weekday_focus,
        "category_stats": category_stats,
        "weekly_growth" : weekly_summary,      # ⭐ 성장곡선용
    }

# ──────────────────────────────────────────
# 사용자 유형 분류
# ──────────────────────────────────────────
def classify_user_type(sessions):
    """집중 시간대·길이·패턴을 바탕으로 프로필 문자열과 설명 반환"""
    if not sessions:
        return "데이터 부족", "아직 충분한 세션 정보가 없습니다."

    focus_map = {"매우 집중": 5, "잘 집중": 4, "보통": 3, "집중 어려움": 2, "평가 없음": 1}

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
            dt = datetime.strptime(s['timestamp'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        hour_counter[dt.hour] += 1
        date_set.add(dt.date())

        work_m = s.get('work_minutes', 0)
        if isinstance(work_m, int) and work_m <= 15:
            short_sessions += 1

        focus_score = focus_map.get(s.get('focus', '평가 없음'), 1)
        focus_sum  += focus_score

        if s.get('goal_achieve') == '달성':
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
