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

    email = data.get('email')
    password = data.get('password')

    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 400

    is_valid = database.login_user(email, password)

    if is_valid[0]:

        return jsonify({
            "message": "Login successful",
            "role": is_valid[1]
        }), 200

    return jsonify({
        "error": "Invalid email or password"
    }), 401


if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=7000
    )