from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save_record", methods=["POST"])
def save_record():
    data = request.get_json()
    record = (
        f"[{data['timestamp']}]\n"
        f"Focus Level: {data['focus']}\n"
        f"Work Flow: {data['flow']}\n"
        f"Task Type: {data['task']}\n"
        f"{'-'*30}\n"
    )
    
    with open("record.txt", "a", encoding="utf-8") as f:
        f.write(record)
        
    return {"status": "saved"}

if __name__ == "__main__":
    app.run(debug=True)
