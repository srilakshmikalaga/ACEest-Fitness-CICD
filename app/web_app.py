from flask import Flask, request, jsonify

app = Flask(__name__)

workouts = []

@app.route("/")
def home():
    return jsonify({"message": "Welcome to ACEest Fitness Web API"})

@app.route("/add", methods=["POST"])
def add_workout():
    data = request.json
    workouts.append(data)
    return jsonify({"message": "Workout added successfully"}), 201

@app.route("/view", methods=["GET"])
def view_workouts():
    return jsonify(workouts)

# ✅ ADD THIS SECTION
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
