# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import os
from modules import recorder, feedback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/session')
def session_setup():
    return render_template('session.html')

@app.route('/start', methods=['POST'])
def start_session():
    data = request.form.to_dict()
    recorder.save_task(data)
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
    # 예시 데이터: 딕셔너리 형태로 제공
    stats_data = {
        "focus": 5,
        "flow": 3,
        "task": 2
    }
    return render_template("stats.html", stats=stats_data)
if __name__ == '__main__':
    app.run(debug=True)
