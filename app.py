import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from modules import recorder
from datetime import datetime
import json
import requests
import toml
import collections # Counter 사용을 위해 import (필요 없으면 제거 가능)

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here_for_security' # 실제 배포 시에는 더 복잡한 키 사용 권장

CONFIG_FILE = 'config.toml' # config.toml 파일 경로

# ───────────────────────────────────────────────────
# 메인 페이지 (index.html)
# ───────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ───────────────────────────────────────────────────
# 세션 설정 페이지 (session.html)
# ───────────────────────────────────────────────────
@app.route('/session')
def session_setup():
    # Flask 세션에 저장된 마지막 입력 값을 가져와 폼에 채웁니다.
    # 사용자가 새로운 세션을 시작할 때 깨끗한 폼을 보기 위함이므로,
    # task, goal, task_category는 초기에는 빈 값으로 전달합니다.
    last_bgm = session.get('last_bgm', 'off') # 배경음악은 마지막 설정값 유지
    
    initial_task = ''
    initial_goal = ''
    initial_task_category = ''

    return render_template(
        'session.html',
        bgm=last_bgm,
        task=initial_task,
        goal=initial_goal,
        task_category=initial_task_category
    )

# ───────────────────────────────────────────────────
# 세션 시작 처리 (타이머 페이지로 이동)
# ───────────────────────────────────────────────────
@app.route('/start', methods=['POST'])
def start_session():
    data = request.form.to_dict()

    # 폼에서 넘어온 데이터 타입 변환 및 기본값 설정
    data['workMinutes']   = int(data.get('workMinutes', 25))
    data['breakMinutes']  = int(data.get('breakMinutes', 5))
    data['repeatCount']   = int(data.get('repeatCount', 1))
    data['focusUnits']    = 1 # session.html에서 hidden input으로 고정
    
    data['task']          = data.get('task', '').strip()
    data['goal']          = "" # session.html에서 제거되었으므로 빈 문자열로 고정
    data['task_category'] = data.get('task_category', '미분류').strip()
    data['bgm']           = data.get('bgm', 'off')

    # 현재 포모도로 세션 정보를 Flask session에 저장 (feedback 페이지로 전달 위함)
    session['current_pomodoro_data'] = {
        'task': data['task'],
        'goal': data['goal'],
        'workMinutes': data['workMinutes'],
        'breakMinutes': data['breakMinutes'],
        'repeatCount': data['repeatCount'],
        'focusUnits': data['focusUnits'],
        'task_category': data['task_category']
    }
    
    # 마지막 설정값 기억 (다음 session_setup 페이지에서 폼을 채우는 데 사용 - 비록 현재는 사용하지 않지만, 향후 확장성 위해 유지)
    session['last_bgm'] = data['bgm']
    session['last_task'] = data['task']
    session['last_goal'] = data['goal']
    session['last_task_category'] = data['task_category']

    # task가 비어있지 않을 때만 세션 시작 기록을 record.txt에 저장
    if data['task']:
        recorder.save_task(data)
    else:
        print("작업 목표가 비어있어 세션 시작 기록을 저장하지 않습니다.")

    return render_template('timer.html', session=session['current_pomodoro_data'])

# ───────────────────────────────────────────────────
# 피드백 페이지 (feedback.html)
# ───────────────────────────────────────────────────
@app.route('/feedback')
def feedback_page():
    # 현재 진행 중인 포모도로 세션 데이터를 Flask session에서 가져옵니다.
    p = session.get('current_pomodoro_data', {})
    
    # 데이터가 없을 경우를 대비한 기본값 설정
    if not p:
        print("경고: 피드백 페이지를 위한 current_pomodoro_data가 세션에 없습니다.")
        p = {
            'task': '정보 없음',
            'goal': '정보 없음',
            'workMinutes': 25,
            'breakMinutes': 5,
            'repeatCount': 1,
            'focusUnits': 1,
            'task_category': '미분류'
        }

    return render_template(
        'feedback.html',
        task=p.get('task'),
        goal=p.get('goal'),
        workMinutes=p.get('workMinutes'),
        breakMinutes=p.get('breakMinutes'),
        repeatCount=p.get('repeatCount'),
        task_category=p.get('task_category')
    )

# ───────────────────────────────────────────────────
# 피드백 제출 처리
# ───────────────────────────────────────────────────
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.form.to_dict()
    
    # '이 통계를 남기지 않겠습니다.' 체크박스가 체크되어 있지 않을 때만 피드백을 저장
    if 'saveStats' not in data:
        task_category_from_form = data.get('task_category', '미분류')
        recorder.save_feedback(data, task_category_from_form)

    session.pop('current_pomodoro_data', None) # 사용한 세션 데이터 정리
    return redirect(url_for('index'))

# ───────────────────────────────────────────────────
# 통계 페이지 (stats.html)
# ───────────────────────────────────────────────────
@app.route('/stats')
def stats():
    all_records  = recorder.get_all_records() # 모든 기록 가져오기
    stats_data   = recorder.calculate_stats(all_records) # 통계 계산
    user_type, user_desc = recorder.classify_user_type(all_records) # 사용자 유형 분류
    
    # 통계 데이터를 Jinja2 템플릿으로 전달하기 위해 정렬 및 기본값 처리
    sorted_daily_summary = dict(sorted(stats_data.get("daily_summary", {}).items()))
    sorted_weekly_growth = dict(sorted(stats_data.get("weekly_growth", {}).items()))

    # Chart.js에 사용될 수 있는 추가 통계 데이터 (stats.html에서 사용하지 않을 경우 제거 가능)
    daily_focus_chart_data = stats_data.get("daily_focus", {})
    task_types_chart_data = stats_data.get("task_types", {})
    pomodoro_settings_chart_data = stats_data.get("pomodoro_settings", {})


    return render_template(
        "stats.html",
        daily_summary_data=sorted_daily_summary,
        weekly_growth_data=sorted_weekly_growth,
        user_type=user_type,
        user_desc=user_desc,
        daily_focus_chart_data=daily_focus_chart_data,
        task_types_chart_data=task_types_chart_data,
        pomodoro_settings_chart_data=pomodoro_settings_chart_data
    )

# ───────────────────────────────────────────────────
# OpenAI API를 통한 포모도로 설정 제안 엔드포인트
# ───────────────────────────────────────────────────
@app.route('/api/suggest_pomodoro', methods=['GET'])
def suggest_pomodoro():
    category = request.args.get('category', '미분류')
    task_keyword = request.args.get('task', '').strip()

    # 1차 입력 유효성 검사: 짧거나 의미 없는 패턴 (OpenAI API 호출 전)
    is_meaningful_task = True
    if len(task_keyword) < 2: # 최소 길이 검사
        is_meaningful_task = False
    elif not any(char.isalpha() or ('\uAC00' <= char <= '\uD7A3') for char in task_keyword): # 한글/알파벳 여부
        is_meaningful_task = False
    else:
        # 5글자 이상일 때 반복되는 문자 패턴 검사 (예: "ㄱㄱㄱㄱㄱ", "aaaaa")
        if len(task_keyword) >= 5:
            char_counts = collections.Counter(task_keyword)
            # 가장 많이 등장하는 문자가 전체 길이의 80% 이상을 차지하면 의미 없는 반복으로 간주
            if char_counts.most_common(1) and char_counts.most_common(1)[0][1] / len(task_keyword) >= 0.8:
                is_meaningful_task = False
            # 유니크한 문자가 1개 이하인 경우 (예: "aaa", "...")
            elif len(char_counts) <= 1:
                is_meaningful_task = False

    if not is_meaningful_task:
        return jsonify({
            "suggestions": recorder.get_default_settings(),
            "status": "invalid_input",
            "reason": "부정확 목표 입력으로 인해 가장 보편적인 포모도로 시간을 제안합니다."
        }), 200 # HTTP 200 OK와 함께 특정 상태 반환

    # OpenAI API 키 로드 (config.toml에서)
    openai_api_key = None
    try:
        config = toml.load(CONFIG_FILE)
        openai_api_key = config.get('openai', {}).get('api_key')
    except FileNotFoundError:
        print(f"오류: {CONFIG_FILE} 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류: {CONFIG_FILE} 파일 로딩 중 문제가 발생했습니다: {e}")

    if not openai_api_key:
        print("오류: config.toml에서 OpenAI API 키를 찾을 수 없거나 파일이 없습니다.")
        return jsonify({
            "suggestions": recorder.get_default_settings(),
            "status": "api_key_missing",
            "reason": f"OpenAI API 키가 {CONFIG_FILE}에 설정되지 않았습니다. 서버 콘솔을 확인해주세요."
        }), 500 # HTTP 500 Internal Server Error

    all_records_list = recorder.get_all_records() # 모든 기록 가져오기
    
    # 'feedback' 타입의 기록만 필터링하여 사용자 기록 수 확인
    feedback_records = [r for r in all_records_list if r.get('record_type') == 'feedback']
    num_user_records = len(feedback_records)

    records_json_lines = "\n".join([json.dumps(r, ensure_ascii=False) for r in feedback_records]) # 프롬프트에 사용할 JSON Lines

    prompt_content = f"""
    당신은 뽀모도로 세션 설정 전문가입니다. 사용자에게 최적의 뽀모도로 설정을 제안해주세요.
    
    현재 사용자가 시작하려는 세션의 정보는 다음과 같습니다:
    - 카테고리: {category}
    - 작업 목표: {task_keyword}

    다음은 과거 뽀모도로 세션 기록입니다. 각 라인은 하나의 JSON 객체입니다.
    'record_type: "feedback"'인 기록에는 다음 점수 필드가 포함되어 있습니다 (점수는 1~5점, 5점이 가장 높음):
    - 'progress_score': 작업 진행 상태 점수 (5:계획대로 모두 완료, 2:아직 시작 단계)
    - 'goal_achieve_score': 목표 달성도 점수 (5:완전히 달성, 2:아쉽지만 달성 아직)
    - 'time_eval_score': 시간 사용 평가 점수 (5:매우 효율적, 1:매우 비효율적)
    - 'focus_score': 집중도 평가 점수 (5:아주 만족스럽게 집중, 2:집중하기 조금 어려움)

    이 점수 필드들을 참고하여 (특히 'focus_score'와 'goal_achieve_score'가 높은) 유사한 카테고리나 작업 목표를 가진 세션을 분석하여 제안을 생성해주세요.
    
    **응답 JSON의 'reason' 필드에 대한 엄격한 지침:**
    1.  **성공적으로 관련 기록을 분석하여 구체적인 설정 제안을 하는 경우:** 'reason' 필드에는 오직 "과거 사용 데이터 분석을 기반으로 위와 같은 셋팅을 제안합니다!"라는 문구만 작성해주세요. (다른 구체적인 과거 세션 정보나 카테고리/작업 언급은 절대 금지)
    2.  **총 사용자 기록('feedback' 타입)이 5개 이하인 경우:** 'reason' 필드에는 오직 "사용자 기록이 부족해 가장 보편적인 포모도로 시간을 제안합니다"라는 문구만 작성해주세요. 이 경우 제안하는 설정은 일반적인 권장 설정(집중 25분, 휴식 5분, 반복 1회, 예상 뽀모도로 1회)이어야 합니다. (이 로직은 Flask 서버에서 먼저 처리되지만, OpenAI에게도 이 상태를 인지하도록 안내)
    3.  **위 두 가지 경우에 해당하지 않으면서, 현재 카테고리/작업 목표와 관련성이 높은 과거 기록을 찾기 어려운 경우:** 'reason' 필드에는 오직 "관련 기록 부족으로 일반적인 설정을 제안합니다."라는 문구만 작성해주세요. 이 경우 제안하는 설정은 일반적인 권장 설정입니다.
    
    제안에는 'workMinutes' (집중 시간, 분 단위), 'breakMinutes' (휴식 시간, 분 단위), 'repeatCount' (반복 횟수), 'focusUnits' (예상 뽀모도로 단위, 횟수)가 포함되어야 합니다.
    응답은 반드시 JSON 형식으로만 해주세요. 
    
    JSON 형식:
    {{
        "workMinutes": [분],
        "breakMinutes": [분],
        "repeatCount": [회],
        "focusUnits": [회],
        "reason": "[위 지침에 따른 이유]"
    }}

    과거 기록:
    {records_json_lines}
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
        "model": "gpt-3.5-turbo", # 또는 "gpt-4", "gpt-4o" 등 사용 가능한 모델
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that suggests Pomodoro settings based on past user data."},
            {"role": "user", "content": prompt_content}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "response_format": {"type": "json_object"}
    }

    try:
        # 사용자 기록이 5개 이하일 경우 강제로 "기록 부족" 메시지를 반환
        if num_user_records <= 5:
            suggested_data = recorder.get_default_settings()
            suggested_data["reason"] = "사용자 기록이 부족해 가장 보편적인 포모도로 시간을 제안합니다"
            status = "openai_fallback_low_records" 
        else: # 사용자 기록이 5개 초과일 때만 OpenAI 호출
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생

            openai_response_data = response.json()
            
            if openai_response_data and openai_response_data.get('choices'):
                message_content = openai_response_data['choices'][0]['message']['content'].strip()
                
                try:
                    suggested_data = json.loads(message_content)
                    # OpenAI가 제공한 reason을 직접 사용하며, 필수 필드 존재 여부 확인
                    if all(key in suggested_data for key in ["workMinutes", "breakMinutes", "repeatCount", "focusUnits", "reason"]):
                        status = "openai_success"
                    else:
                        suggested_data = recorder.get_default_settings()
                        suggested_data["reason"] = "OpenAI 응답 형식이 예상과 달라 일반적인 설정을 제안합니다. (필수 필드 누락)"
                        status = "openai_fallback"

                except json.JSONDecodeError:
                    print(f"오류: OpenAI가 유효한 JSON을 반환하지 않았습니다: {message_content}")
                    suggested_data = recorder.get_default_settings()
                    suggested_data["reason"] = "OpenAI 응답 파싱 중 오류가 발생하여 일반적인 설정을 제안합니다."
                    status = "openai_fallback"
            else:
                suggested_data = recorder.get_default_settings()
                suggested_data["reason"] = "OpenAI 응답이 비어있습니다. 일반적인 설정을 제안합니다. (API 문제일 수 있습니다.)"
                status = "openai_fallback"

    except requests.exceptions.RequestException as e:
        print(f"오류: OpenAI API 호출 중 네트워크 오류 발생: {e}")
        suggested_data = recorder.get_default_settings()
        suggested_data["reason"] = f"OpenAI API 호출 중 네트워크 오류가 발생하여 일반적인 설정을 제안합니다. (오류: {e})"
        status = "openai_api_error"
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        suggested_data = recorder.get_default_settings()
        suggested_data["reason"] = f"예상치 못한 오류가 발생하여 일반적인 설정을 제안합니다. (오류: {e})"
        status = "openai_error"

    # 제안 값이 HTML의 옵션 범위 내에 있는지 다시 한번 확인
    if suggested_data['workMinutes'] not in range(5, 60, 5): suggested_data['workMinutes'] = 25
    if suggested_data['breakMinutes'] not in range(1, 11): suggested_data['breakMinutes'] = 5
    if suggested_data['repeatCount'] not in range(1, 6): suggested_data['repeatCount'] = 1
    if suggested_data['focusUnits'] not in range(1, 11): suggested_data['focusUnits'] = 1

    return jsonify({"suggestions": suggested_data, "status": status, "reason": suggested_data["reason"]})


# ───────────────────────────────────────────────────
# 오류 페이지
# ───────────────────────────────────────────────────
@app.route('/error')
def error_page():
    message = request.args.get('message', '알 수 없는 오류가 발생했습니다.')
    return render_template('error.html', message=message)


if __name__ == '__main__':
    app.run(debug=True)

