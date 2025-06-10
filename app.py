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
    return render_template('timer.html', session=data)

@app.route('/feedback')
def feedback_page():
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
    recorder.save_feedback(data)
    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    # 1) 모든 세션 데이터 로드
    all_sessions = recorder.get_all_sessions_data()

    # 2) 통계 계산 (modules/recorder.calculate_stats 구현 필요)
    stats_data = recorder.calculate_stats(all_sessions)

    # 3) 차트용 데이터 구조 생성
    daily_focus_chart_data = {
        "labels": sorted(stats_data["daily_focus"].keys()),
        "datasets": [
            {
              "label": level,
              "data": [ stats_data["daily_focus"][date].get(level, 0)
                        for date in sorted(stats_data["daily_focus"].keys()) ]
            }
            for level in ["매우 집중", "잘 집중", "보통", "집중 어려움", "평가 없음"]
        ]
    }
    task_types_chart_data = {
        "labels": list(stats_data["task_types"].keys()),
        "data":   list(stats_data["task_types"].values())
    }
    pomodoro_settings_chart_data = {
        "labels": list(stats_data["pomodoro_settings"].keys()),
        "data":   list(stats_data["pomodoro_settings"].values())
    }

    # 4) stats.html 에 3가지 차트 데이터 전달
    return render_template(
        "stats.html",
        daily_focus_chart_data=daily_focus_chart_data,
        task_types_chart_data=task_types_chart_data,
        pomodoro_settings_chart_data=pomodoro_settings_chart_data
    )

if __name__ == '__main__':
    app.run(debug=True)
