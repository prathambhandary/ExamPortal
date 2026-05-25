from flask import Flask, request, jsonify
from flask_cors import CORS
import database
import subprocess
import os

app = Flask(__name__)
CORS(app)

database.create_tables()

@app.route('/api/github-deploy-webhook', methods=['POST'])
def github_webhook():
    incoming_secret = request.headers.get('X-Hub-Signature-256') or request.args.get('token')
    
    server_secret = os.environ.get('DEPLOY_SECRET')

    if not server_secret or request.args.get('token') != server_secret:
        return jsonify({"error": "Unauthorized webhook token matching verification failed."}), 403

    if request.headers.get('X-GitHub-Event') == 'push':
        try:
            project_dir = '/home/sharmaji/ExamPortal'
            subprocess.run(['git', '-C', project_dir, 'pull'], check=True)
            
            wsgi_file = "/var/www/sharmaji_pythonanywhere_com_wsgi.py"
            if os.path.exists(wsgi_file):
                os.utime(wsgi_file, None)
                
            return jsonify({"message": "Deployment successful. ExamPortal repo synced and reloaded."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"message": "Ignored non-push configuration event"}), 200

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


@app.route("/add_batch", methods=['POST'])
def add_batch():
    data = request.json
    batch_name = data.get('batch_name')
    course = data.get('course')
    year = data.get('year')
    
    if not batch_name or not course or not year:
        return jsonify({'error': "Missing fields"}), 400
    
    status, message = database.add_batch(batch_name, course, year)
    if status:
        return jsonify({"message": message}), 201
    return jsonify({'error': message}), 400
    


# Temporary

@app.route("/delete_user", methods=['POST'])
def delete_user():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    database.delete_user(username)
    return jsonify({"message": "User deleted successfully"}), 200



if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=7000
    )