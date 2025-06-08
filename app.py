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
    
    # 기본 테마를 설정 (땅부터 시작)
    data['theme'] = '땅'
    
    recorder.save_task(data)  # 데이터 저장

    return render_template('timer.html', session=data)  # timer.html로 이동

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
