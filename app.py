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
            
            subprocess.run(['git', '-C', project_dir, 'fetch', '--all'], check=True)
            
            subprocess.run(['git', '-C', project_dir, 'reset', '--hard', 'origin/main'], check=True)
             
            wsgi_file = "/var/www/sharmaji_pythonanywhere_com_wsgi.py"
            if os.path.exists(wsgi_file):
                os.utime(wsgi_file, None)
                
            return jsonify({"message": "Force deployment successful. ExamPortal synced perfectly."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"message": "Ignored non-push configuration event"}), 200

@app.route('/')
def home():
    return jsonify({"message": "Server is live"}), 200

@app.route('/login', methods=['POST'])
def login():

    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    is_valid = database.login_user(username, password)
    profile_data = is_valid[2] if len(is_valid) > 2 else None

    if is_valid[0] and is_valid[1] == "student":
        if profile_data.get("access") == 0:
            return jsonify(("error", "Access denied")), 403
        
        return jsonify({
                "message": "Login successful", 
                "role": is_valid[1],
                "username": username,
                "first_name": profile_data.get("first_name"),
                "last_name": profile_data.get("last_name"),
                "roll_number": profile_data.get("roll_number"),
                "email": profile_data.get("email"),
                "student_phone": profile_data.get("student_phone"),
                "parent_phone": profile_data.get("parent_phone"),
                "stream": profile_data.get("stream"),
                "target_year": profile_data.get("target_year"),
                "gender": profile_data.get("gender"),
                "batch_name": database.get_batch_name(profile_data.get("batch_id"))
            }), 200
    
    if is_valid[0]:
        return jsonify({
                "message": "Login successful", 
                "role": is_valid[1]
            })

    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/register', methods=['POST'])  #security risk
def register():
    return {'message': 'closed'}, 200

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
    
@app.route("/get_batches", methods=['GET'])
def get_batch_names():
    batches = database.all_batches()
    return jsonify(batches), 200

@app.route("/register_student", methods=['POST'])
def add_student_endpoint():

    data = request.json

    if data is None:
        return jsonify({"error": "Invaild JSON data"}), 400
    
    if data.get("current_role") != "admin":
        return jsonify({"error": "Unauthorized Access"}), 403

    required_fields = [
        "username",
        "password",
        "first_name",
        "roll_number",
        "stream",
        "target_year"
    ]

    # CHECK REQUIRED FIELDS
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    status, message = database.add_student(
        username=data.get("username"),
        password=data.get("password"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        roll_number=data.get("roll_number"),
        batch_name=data.get("batch_name"),
        email=data.get("email"),
        student_phone=data.get("student_phone"),
        parent_phone=data.get("parent_phone"),
        stream=data.get("stream"),
        target_year=data.get("target_year"),
        gender=data.get("gender", "").title()
    )

    if status:
        return jsonify({
            "message": message
        }), 201

    return jsonify({
        "error": message
    }), 400

@app.route("/clear_table/<table_name>", methods=["GET"]) #security risk
def clear_table_endpoint(table_name):
    return {'message': 'closed'}, 200
    allowed_tables = [
        "batches",
        "login",
        "student_profiles"
    ]
    if table_name not in allowed_tables:
        return jsonify({
            "error": "Invalid table name"
        }), 400
    status, message = database.clear_table(table_name)
    if status:
        return jsonify({
            "message": message
        }), 200
    return jsonify({
        "error": message
    }), 500

@app.route("/get_student_profile", methods=['GET']) # security risk
def get_student_profile():
    return {'message': 'closed'}, 200
    return jsonify(database.get_student_profile("ram")), 200

@app.route("/login_table", methods=['GET']) # security risk
def get_login_table():
    return {'message': 'closed'}, 200
    return jsonify(database.get_login_table()), 200

@app.route("/revoke_access", methods=['POST'])
def revoke_access():
    data = request.json
    
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    if data.get("current_role") != "admin":
        return jsonify({"error": "Unauthorized Access"}), 403
    
    username = data.get('username')  
    if not username:
        return jsonify({'error': 'Username required'}), 400  

    status, message = database.revoke_access(username)
    if status:
        return jsonify({'message': message}), 200
    
    return jsonify({'error': message}), 400

@app.route("/grant_access", methods=['POST'])
def grant_access():
    data = request.json
    
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400

    if data.get("current_role") != "admin":
        return jsonify({"error": "Unauthorized Access"}), 403
    
    username = data.get('username')  
    if not username:
        return jsonify({'error': 'Username required'}), 400  

    status, message = database.grant_access(username)
    if status:
        return jsonify({'message': message}), 200
    
    return jsonify({'error': message}), 400

@app.route("/get_all_student_profile_admin", methods=['POST'])
def get_all_student_profiles():
    data = request.json

    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400

    if data.get("current_role") != "admin":
        return jsonify({"error": "Unauthorized Access"}), 403
    
    profiles = database.all()
    return jsonify(profiles), 200

@app.route("/students/search", methods=["POST"])
def search_students():

    data = request.get_json(silent=True) or {}

    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400

    if data.get("current_role") != "admin":
        return jsonify({"error": "Unauthorized Access"}), 403

    search = data.get("search", "")
    batch_name = data.get("batch_name")
    stream = data.get("stream")
    target_year = data.get("target_year")

    page = int(data.get("page", 1))
    limit = int(data.get("limit", 10))
    offset = (page - 1) * limit

    rows = database.all_students(
        search=search,
        batch_name=batch_name,
        stream=stream,
        target_year=target_year,
        limit=limit,
        offset=offset
    )

    payload = [
        {
            "username": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "roll_number": r[3],
            "batch_name": r[4],
            "email": r[5],
            "student_phone": r[6],
            "parent_phone": r[7],
            "stream": r[8],
            "target_year": r[9],
            "access": r[10],
            "gender": r[11]
        }
        for r in rows
    ]

    return jsonify({
        "page": page,
        "limit": limit,
        "count": len(payload),
        "data": payload
    }), 200

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=7000
    )
