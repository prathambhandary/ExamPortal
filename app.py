from flask import Flask, request, jsonify
from flask_cors import CORS
import database

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return "Server Running..."


@app.route('/login', methods=['POST'])
def login():

    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    is_valid = database.login_user(username, password)

    if is_valid[0]:
        return jsonify({"message": "Login successful", "role": is_valid[1]}), 200

    return jsonify({"error": "Invalid username or password"}), 401


@app.route('/register', methods=['POST'])
def register():

    data = request.json

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"error": "Missing fields"}), 400

    status, message = database.add_user(
        username,
        password,
        role
    )

    if status:
        return jsonify({"message": message}), 201

    return jsonify({"error": message}), 400


if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=7000
    )