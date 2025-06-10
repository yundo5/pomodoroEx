from flask import Flask, render_template, request, redirect, url_for
from modules import recorder

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/session')
def session_setup():
    # session.html 폼을 띄울 때 기본값 지정
    return render_template('session.html',
                           bgm='off',
                           task='',
                           goal='')

@app.route('/start', methods=['POST'])
def start_session():
    # form 에서 전달된 모든 값을 딕셔너리로 수집
    data = request.form.to_dict()

    # 기본값 처리
    data['theme']        = '땅'                       # 기본 테마
    data['bgm']          = data.get('bgm', 'off')     # BGM 기본값
    data['workMinutes']  = int(data.get('workMinutes', 25))
    data['breakMinutes'] = int(data.get('breakMinutes', 5))
    # ★ 여기서 폼의 repeatCount 값을 받아 저장합니다.
    data['repeatCount']  = int(data.get('repeatCount', 1))
    data['task']         = data.get('task', '')
    data['goal']         = data.get('goal', '')

    # 데이터 저장 (로그나 기록용)
    recorder.save_task(data)

    # timer.html 로 넘어갈 때 data 를 session 이라는 이름으로 넘겨줍니다.
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
