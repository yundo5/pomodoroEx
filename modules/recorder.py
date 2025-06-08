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
    # 피드백 저장 시, 해당 피드백이 어떤 세션에 대한 것인지 연결하기 위해
    # 가장 최근의 작업 시간 기록과 연결할 수 있도록 구분자를 추가하거나,
    # feedback 페이지에서 세션 정보를 숨겨서 받아오는 방식 고려
    # 여기서는 간단히 구분자 추가
    with open(RECORD_FILE, 'a', encoding='utf-8') as f:
        f.write(f"작업진행: {progress}\n")
        f.write(f"목표달성: {goal_achieve}\n")
        f.write(f"시간사용: {time_eval}\n")
        f.write(f"집중도: {focus}\n")
        if comment:
            f.write(f"기타의견: {comment}\n")
        f.write("-" * 30 + "\n") # 각 세션의 끝을 알리는 구분자 def get_all_sessions_data():
    
def get_all_sessions_data(): # 이 함수가 있는지 확인하고 없으면 추가
    """record.txt 파일에서 모든 세션 데이터와 피드백을 파싱하여 반환"""
    sessions = []
    current_session = {}
    # record.txt 파일이 존재하지 않을 경우를 대비하여 예외 처리
    if not os.path.exists(RECORD_FILE):
        return sessions # 파일이 없으면 빈 리스트 반환

    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('[') and ']' in line: # 새 세션 시작
            if current_session: # 이전 세션이 있으면 추가
                sessions.append(current_session)
            current_session = {}
            current_session['timestamp'] = line.strip('[]')
        elif line.startswith('작업: '):
            current_session['task'] = line.replace('작업: ', '')
        elif line.startswith('목표: '):
            current_session['goal'] = line.replace('목표: ', '')
        elif line.startswith('예상 시간: '):
            # "5분 1분 1회" 형식 파싱
            time_parts_str = line.replace('예상 시간: ', '')
            try:
                parts = time_parts_str.split('분 ')
                current_session['work_minutes'] = parts[0]
                current_session['break_minutes'] = parts[1].split(' ')[0]
                current_session['repeat_count'] = parts[1].split(' ')[1].replace('회', '')
            except IndexError:
                print(f"경고: 예상 시간 형식 오류 - {time_parts_str}")
                current_session['work_minutes'] = '?'
                current_session['break_minutes'] = '?'
                current_session['repeat_count'] = '?'
        elif line.startswith('작업진행: '):
            current_session['progress'] = line.replace('작업진행: ', '')
        elif line.startswith('목표달성: '):
            current_session['goal_achieve'] = line.replace('목표달성: ', '')
        elif line.startswith('시간사용: '):
            current_session['time_eval'] = line.replace('시간사용: ', '')
        elif line.startswith('집중도: '):
            current_session['focus'] = line.replace('집중도: ', '')
        elif line.startswith('기타의견: '):
            current_session['comment'] = line.replace('기타의견: ', '')
        elif line.startswith('-' * 30): # 세션 구분자
            if current_session:
                sessions.append(current_session)
            current_session = {} # 다음 세션을 위해 초기화

    if current_session: # 파일의 마지막 세션 추가
        sessions.append(current_session)
    return sessions

def calculate_stats(sessions): # 이 함수가 있는지 확인하고 없으면 추가
    """파싱된 세션 데이터를 기반으로 통계 계산"""
    daily_focus = {}
    task_types = {}
    pomodoro_settings = {}

    for session in sessions:
        try:
            # 날짜별 집중도
            date_str = session['timestamp'].split(' ')[0]
            focus_level = session.get('focus', '평가 없음')

            if date_str not in daily_focus:
                daily_focus[date_str] = {'매우 집중': 0, '잘 집중': 0, '보통': 0, '집중 어려움': 0, '평가 없음': 0}
            daily_focus[date_str][focus_level] += 1

            # 작업 유형 (사용 목적)
            task = session.get('task', '미지정')
            task_types[task] = task_types.get(task, 0) + 1

            # 포모도로 세팅
            # get()으로 안전하게 접근하고, 누락될 경우 기본값 설정
            work_m = session.get('work_minutes', '?')
            break_m = session.get('break_minutes', '?')
            repeat_c = session.get('repeat_count', '?')
            setting_key = f"{work_m}분 {break_m}분 {repeat_c}회"
            pomodoro_settings[setting_key] = pomodoro_settings.get(setting_key, 0) + 1
        except KeyError as e:
            print(f"세션 데이터 처리 중 키 오류 발생: {e} in session: {session}")
            continue
        except Exception as e:
            print(f"세션 데이터 처리 중 알 수 없는 오류 발생: {e} in session: {session}")
            continue

    return {
        "daily_focus": daily_focus,
        "task_types": task_types,
        "pomodoro_settings": pomodoro_settings
    }