from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import database

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    password_hash = generate_password_hash(password)

    if not email or not password_hash:
        return jsonify({"error": "Email and password hash are required"}), 400

    is_valid = database.login_user(email, password_hash)
    if is_valid:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

if __name__ == "__main__":
    app.run(debug=True)