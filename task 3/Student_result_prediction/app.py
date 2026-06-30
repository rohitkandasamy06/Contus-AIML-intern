from flask import Flask, render_template, request
from predictor import predict

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    form_data = {}
    if request.method == "POST":
        try:
            form_data = {
                "study_hours_per_day": float(request.form["study_hours_per_day"]),
                "attendance_percent": float(request.form["attendance_percent"]),
                "previous_score": float(request.form["previous_score"]),
                "assignments_completed_percent": float(request.form["assignments_completed_percent"]),
                "sleep_hours": float(request.form["sleep_hours"]),
                "extra_activities": int(request.form["extra_activities"]),
                "parental_support": int(request.form["parental_support"]),
                "internet_access": int(request.form["internet_access"]),
            }
            result = predict(form_data)
        except (KeyError, ValueError):
            result = {"error": "Please fill in all fields with valid values."}

    return render_template("index.html", result=result, form_data=form_data)

if __name__ == "__main__":
    app.run(debug=False, port=5050)