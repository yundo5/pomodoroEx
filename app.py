from flask import Flask, render_template, request, redirect, url_for
from modules import recorder

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/session')
def session_setup():
    return render_template('session.html', bgm='off', task='', goal='')

@app.route('/start', methods=['POST'])
def start_session():
    data = request.form.to_dict()

    # 기본값 처리
    data['theme']        = '땅'
    data['bgm']          = data.get('bgm', 'off')
    data['workMinutes']  = int(data.get('workMinutes', 25))
    data['breakMinutes'] = int(data.get('breakMinutes', 5))
    data['repeatCount']  = int(data.get('repeatCount', 1))
    data['task']         = data.get('task', '')
    data['goal']         = data.get('goal', '')

    recorder.save_task(data)

    # timer.html 로 data(dict)를 session 키로 넘겨줌
    return render_template('timer.html', session=data)

@app.route('/feedback')
    
    # 기본 테마를 설정 (땅부터 시작)
    data['theme'] = '땅'
    
    recorder.save_task(data)  # 데이터 저장 # 세션 정보를 feedback 페이지로 전달하기 위해 session에 저장하거나,
    # 간단하게는 URL 파라미터나 숨겨진 필드로 전달할 수 있습니다.
    # 여기서는 timer.html로 전달한 후, timer.html에서 feedback으로 redirect 시킬 때
    # 이 데이터를 다시 전달하는 방식(또는 세션에 저장)을 고려해야 합니다.
    # 간단한 예시를 위해, feedback 페이지에서 session 객체를 다시 로드하는 방식이나
    # feedback 페이지 자체에서 기록된 가장 최근 세션 정보를 읽어오는 방식이 필요할 수 있습니다.
    # 현재 피드백 페이지는 session 객체를 직접 받지 않으므로, 이 부분의 로직을 수정해야 합니다.
    # 임시 방편으로, 가장 최근 기록을 feedback 페이지에서 보여준다고 가정합니다.

    return render_template('timer.html', session=data)  # timer.html로 이동 @app.route('/feedback')
def feedback_page():
    # 실제 구현에서는 현재 진행 중인 세션 정보를 가져와야 합니다.
    # 예를 들어, 세션을 시작할 때 생성된 고유 ID를 이용하거나,
    # 가장 최근에 기록된 세션 정보를 recorder 모듈에서 가져올 수 있습니다.
    # 여기서는 간단히 record.txt에서 가장 최근 세션 정보를 읽어오는 방식을 가정합니다.
    all_sessions = recorder.get_all_sessions_data()
    # 가장 최근 세션 정보를 피드백 페이지에 보여주기 위해 전달
    latest_session = all_sessions[-1] if all_sessions else {}
    return render_template('feedback.html', session=latest_session)
    # 쿼리스트링에서 넘어온 값 읽기
    workMinutes  = request.args.get('workMinutes',  25, type=int)
    breakMinutes = request.args.get('breakMinutes', 5,  type=int)
    repeatCount  = request.args.get('repeatCount',  1,  type=int)
    task         = request.args.get('task',         '', type=str)
    goal         = request.args.get('goal',         '', type=str)

    return render_template(
        'feedback.html',
        workMinutes=workMinutes,
        breakMinutes=breakMinutes,
        repeatCount=repeatCount,
        task=task,
        goal=goal
    )

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.form.to_dict()
    recorder.save_feedback(data) # 피드백 데이터 저장 return redirect(url_for('index'))

@app.route('/stats')
def stats():
    all_sessions = recorder.get_all_sessions_data() # 모든 세션 데이터 가져오기
    stats_data = recorder.calculate_stats(all_sessions) # 통계 계산

    # stats.html로 전달할 데이터를 구성
    # 예시: 일별 집중도 (차트에서 사용하기 좋게 변환)
    daily_focus_chart_data = {
        "labels": sorted(stats_data["daily_focus"].keys()),
        "datasets": [
            {"label": "매우 집중", "data": [stats_data["daily_focus"][date].get('매우 집중', 0) for date in sorted(stats_data["daily_focus"].keys())]},
            {"label": "잘 집중", "data": [stats_data["daily_focus"][date].get('잘 집중', 0) for date in sorted(stats_data["daily_focus"].keys())]},
            {"label": "보통", "data": [stats_data["daily_focus"][date].get('보통', 0) for date in sorted(stats_data["daily_focus"].keys())]},
            {"label": "집중 어려움", "data": [stats_data["daily_focus"][date].get('집중 어려움', 0) for date in sorted(stats_data["daily_focus"].keys())]},
            {"label": "평가 없음", "data": [stats_data["daily_focus"][date].get('평가 없음', 0) for date in sorted(stats_data["daily_focus"].keys())]},
        ]
    }
    
    # 작업 유형 (파이 차트 등에 사용)
    task_types_chart_data = {
        "labels": list(stats_data["task_types"].keys()),
        "data": list(stats_data["task_types"].values())
    }

    # 포모도로 세팅 (막대 차트 등에 사용)
    pomodoro_settings_chart_data = {
        "labels": list(stats_data["pomodoro_settings"].keys()),
        "data": list(stats_data["pomodoro_settings"].values())
    }

    return render_template("stats.html", 
                           daily_focus_chart_data=daily_focus_chart_data,
                           task_types_chart_data=task_types_chart_data,
                           pomodoro_settings_chart_data=pomodoro_settings_chart_data)

if __name__ == '__main__':
    app.run(debug=True)