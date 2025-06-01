from flask import Flask, render_template, request
from modules.recorder import load_records
from modules.feedback import summarize_feedback, calculate_total_focus_time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save_record", methods=["POST"])
def save_record():
    data = request.get_json()
    with open("record.txt", "a", encoding="utf-8") as f:
        f.write(
            f"[{data['timestamp']}]\n"
            f"Focus Level: {data['focus']}\n"
            f"Work Flow: {data['flow']}\n"
            f"Task Type: {data['task']}\n"
            f"{'-'*30}\n"
        )
    return {"status": "saved"}

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    with open("record.txt", "a", encoding="utf-8") as f:
        f.write(
            f"[{data['timestamp']}]\n"
            f"Focus Level: {data['focus']}\n"
            f"Work Flow: {data['flow']}\n"
            f"Task Type: {data['task']}\n"
            f"Focus Duration Feedback: {data['focusFeedback']}\n"
            f"Break Duration Feedback: {data['breakFeedback']}\n"
            f"{'-'*30}\n"
        )
    return {"status": "feedback_saved"}

@app.route("/stats")
def stats():
    try:
        records = load_records()
        summary = summarize_feedback(records)
        total_time = calculate_total_focus_time(records)
    except Exception as e:
        summary = {}
        total_time = 0
        print(f"[ERROR] stats page failed: {e}")
    return render_template("stats.html", summary=summary, total_time=total_time)

if __name__ == "__main__":
    app.run(debug=True)
