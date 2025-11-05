from flask import Flask, jsonify, request

fitness_app = Flask(__name__)
workouts = []

@fitness_app.route("/")
def home():
    return jsonify({"message": "Welcome to ACEest Fitness Web API"})

@fitness_app.route("/add", methods=["POST"])
def add_workout():
    data = request.json
    workouts.append(data)
    return jsonify({"message": "Workout added successfully"}), 201

@fitness_app.route("/view", methods=["GET"])
def view_workouts():
    return jsonify(workouts)

if __name__ == '__main__':
    fitness_app.run(host='0.0.0.0', port=5000)
