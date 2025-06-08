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
    data['theme'] = '땅'  # 기본 테마
    data['bgm'] = data.get('bgm', 'off')  # bgm 기본값 설정
    data['workMinutes'] = int(data.get('workMinutes', 25))
    data['breakMinutes'] = int(data.get('breakMinutes', 5))
    data['repeatCount'] = int(data.get('repeatCount', 1))
    data['task'] = data.get('task', '')
    data['goal'] = data.get('goal', '')

    # 작업 저장
    recorder.save_task(data)

    # 타이머 화면으로 전달
    return render_template('timer.html', session=data)

@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.form.to_dict()
    recorder.save_feedback(data)
    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    stats_data = {
        "focus": 5,
        "flow": 3,
        "task": 2
    }
    return render_template("stats.html", stats=stats_data)

if __name__ == '__main__':
    app.run(debug=True)
