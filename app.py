from flask import Flask, render_template, request, redirect, url_for, session
from modules import recorder
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here_for_security'

# ───────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ───────────────────────────────────────────────────
@app.route('/session')
def session_setup():
    return render_template(
        'session.html',
        bgm=session.get('last_bgm', 'off'),
        task=session.get('last_task', ''),
        goal=session.get('last_goal', ''),
        task_category=session.get('last_task_category', '')
    )

# ───────────────────────────────────────────────────
@app.route('/start', methods=['POST'])
def start_session():
    data = request.form.to_dict()

    data['theme']         = '땅'
    data['bgm']           = data.get('bgm', 'off')
    data['workMinutes']   = int(data.get('workMinutes', 25))
    data['breakMinutes']  = int(data.get('breakMinutes', 5))
    data['repeatCount']   = int(data.get('repeatCount', 1))
    data['task']          = data.get('task', '')
    data['goal']          = data.get('goal', '')
    data['focusUnits']    = int(data.get('focusUnits', 1))
    data['task_category'] = data.get('task_category', '미분류')

    # 세션 저장
    session['current_pomodoro_data'] = {
        k: data[k] for k in ['task', 'goal', 'workMinutes', 'breakMinutes',
                             'repeatCount', 'focusUnits', 'task_category']
    }

    recorder.save_task(data)

    return render_template('timer.html', session=data)

# ───────────────────────────────────────────────────
@app.route('/feedback')
def feedback_page():
    p = session.get('current_pomodoro_data', {})
    return render_template(
        'feedback.html',
        task=p.get('task', '정보 없음'),
        goal=p.get('goal', '정보 없음'),
        workMinutes=p.get('workMinutes', 25),
        breakMinutes=p.get('breakMinutes', 5),
        repeatCount=p.get('repeatCount', 1),
        task_category=p.get('task_category', '미분류')
    )

# ───────────────────────────────────────────────────
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.form.to_dict()
    if 'saveStats' in data:
        recorder.save_feedback(data)
    session.pop('current_pomodoro_data', None)
    return redirect(url_for('index'))

# ───────────────────────────────────────────────────
@app.route('/stats')
def stats():
    all_sessions = recorder.get_all_sessions_data()
    stats_data   = recorder.calculate_stats(all_sessions)
    user_type, user_desc = recorder.classify_user_type(all_sessions)

    daily_focus_chart_data = {
        "labels": sorted(stats_data["daily_focus"].keys()),
        "datasets": [
            {
                "label": level,
                "data": [
                    stats_data["daily_focus"][date].get(level, 0)
                    for date in sorted(stats_data["daily_focus"].keys())
                ]
            } for level in ["매우 집중", "잘 집중", "보통", "집중 어려움", "평가 없음"]
        ]
    }
    task_types_chart_data = {
        "labels": list(stats_data["task_types"].keys()),
        "data": list(stats_data["task_types"].values())
    }
    pomodoro_settings_chart_data = {
        "labels": list(stats_data["pomodoro_settings"].keys()),
        "data": list(stats_data["pomodoro_settings"].values())
    }

    return render_template(
        "stats.html",
        daily_focus_chart_data=daily_focus_chart_data,
        task_types_chart_data=task_types_chart_data,
        pomodoro_settings_chart_data=pomodoro_settings_chart_data,
        daily_summary_data=stats_data["daily_summary"],
        weekly_growth_data=stats_data["weekly_growth"],
        user_type=user_type,
        user_desc=user_desc
    )

# ───────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
