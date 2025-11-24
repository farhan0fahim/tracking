from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import csv
import datetime

app = Flask(__name__)
CORS(app)

# ---------------------------
# In-memory status and notice
# ---------------------------
current_status = {
    "Location": "302",
    "Room number": "302",
    "state": "Class"
}

current_notice = "নোটিশ: আগামীকাল Class বন্ধ থাকবে।"

# ---------------------------
# Helper: Read timetable CSV
# ---------------------------
def get_today_timetable():
    filename = "static/7400.csv"
    today_name = datetime.datetime.now().strftime("%A")  # e.g., 'Sunday'
    timetable = []

    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # ['Day', '08:30-10:00', '10:00-11:30', ...]
        for row in reader:
            day = row[0]
            if day.lower() == today_name.lower():
                # Map timeslot -> activity
                for i, activity in enumerate(row[1:], 1):
                    if activity.strip():  # ignore empty
                        timetable.append({
                            "time": header[i],
                            "course": activity
                        })
                break

    if not timetable:
        timetable.append({"time": "-", "course": "Day off"})

    return timetable

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/current")
def current():
    return jsonify({
        "status": current_status,
        "notice": current_notice
    })

@app.route("/timetable")
def timetable():
    now = datetime.datetime.now()
    data = {
        "day": now.strftime("%A"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "slots": get_today_timetable()
    }
    return jsonify(data)

@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    print("Received at /login:", data)
    return "accepted", 200, {"Content-Type": "text/plain"}

@app.route("/notice", methods=["POST", "OPTIONS"])
def notice():
    global current_notice
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    print("Received at /notice:", data)
    if "message" in data:
        current_notice = data["message"]
    return "accepted", 200, {"Content-Type": "text/plain"}

@app.route("/status", methods=["POST", "OPTIONS"])
def status():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    print("Received at /status:", data)
    current_status["Location"] = data.get("Location", current_status["Location"])
    current_status["Room number"] = data.get("Room number", current_status["Room number"])
    current_status["state"] = data.get("state", current_status["state"])
    return "accepted", 200, {"Content-Type": "text/plain"}

# ---------------------------
# Run server on LAN
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
