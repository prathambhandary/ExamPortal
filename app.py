from flask import Flask, request, jsonify
from flask_cors import CORS
import database
import subprocess
import os
from datetime import timedelta
from auth import admin_required
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt
)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-change-this"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)
CORS(app)

database.create_tables()
database.create_indexes()
database.ensure_login_logs_columns(database.get_connection())

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

    data=request.get_json(silent=True) or {}

    username=data.get('username')
    password=data.get('password')

    if not username or not password:
        return jsonify({"error":"Username and password are required"}),400

    ip_address = data.get("ip_address")
    user_agent = data.get("user_agent")
    fingerprint = data.get("fingerprint", {})

    is_valid = database.login_user(username, password)
    user_id = database.get_user_id(username)

    if not is_valid[0]:
        database.add_login_log(
            user_id=user_id,
            success=False,
            ip_address=ip_address,
            forwarded_for=data.get("forwarded_for"),
            host=data.get("host"),
            origin=data.get("origin"),
            referer=data.get("referer"),
            user_agent=user_agent,
            accept_language=data.get("accept_language"),
            sec_ch_ua=data.get("sec_ch_ua"),
            sec_ch_platform=data.get("sec_ch_platform"),
            sec_ch_mobile=data.get("sec_ch_mobile"),
            method=data.get("method"),
            path=data.get("path"),
            screen_resolution=fingerprint.get("screen_resolution"),
            viewport=fingerprint.get("viewport"),
            timezone=fingerprint.get("timezone"),
            timezone_offset=fingerprint.get("timezone_offset"),
            language=fingerprint.get("language"),
            languages=fingerprint.get("languages"),
            platform=fingerprint.get("platform"),
            cpu_cores=fingerprint.get("cpu_cores"),
            device_memory=fingerprint.get("device_memory"),
            touch_points=fingerprint.get("touch_points"),
            cookies_enabled=fingerprint.get("cookies_enabled"),
            online_status=fingerprint.get("online_status"),
            connection_type=fingerprint.get("connection_type"),
            device_pixel_ratio=fingerprint.get("device_pixel_ratio"),
            local_storage=fingerprint.get("local_storage"),
            session_storage=fingerprint.get("session_storage"),
            do_not_track=fingerprint.get("do_not_track"),
            login_id=data.get("login_id"),
            request_id=data.get("request_id"),
            session_id=data.get("session_id"),
            device_id=data.get("device_id")
        )
        
        return jsonify({"error":"Invalid username or password"}),401

    role=is_valid[1]
    profile_data=is_valid[2] if len(is_valid)>2 else None

    database.add_login_log(
        user_id=user_id,
        success=True,
        ip_address=ip_address,
        forwarded_for=data.get("forwarded_for"),
        host=data.get("host"),
        origin=data.get("origin"),
        referer=data.get("referer"),
        user_agent=user_agent,
        accept_language=data.get("accept_language"),
        sec_ch_ua=data.get("sec_ch_ua"),
        sec_ch_platform=data.get("sec_ch_platform"),
        sec_ch_mobile=data.get("sec_ch_mobile"),
        method=data.get("method"),
        path=data.get("path"),
        screen_resolution=fingerprint.get("screen_resolution"),
        viewport=fingerprint.get("viewport"),
        timezone=fingerprint.get("timezone"),
        timezone_offset=fingerprint.get("timezone_offset"),
        language=fingerprint.get("language"),
        languages=fingerprint.get("languages"),
        platform=fingerprint.get("platform"),
        cpu_cores=fingerprint.get("cpu_cores"),
        device_memory=fingerprint.get("device_memory"),
        touch_points=fingerprint.get("touch_points"),
        cookies_enabled=fingerprint.get("cookies_enabled"),
        online_status=fingerprint.get("online_status"),
        connection_type=fingerprint.get("connection_type"),
        device_pixel_ratio=fingerprint.get("device_pixel_ratio"),
        local_storage=fingerprint.get("local_storage"),
        session_storage=fingerprint.get("session_storage"),
        do_not_track=fingerprint.get("do_not_track"),
        login_id=data.get("login_id"),
        request_id=data.get("request_id"),
        session_id=data.get("session_id"),
        device_id=data.get("device_id")
    )

    token=create_access_token(
        identity=username,
        additional_claims={"role":role}
    )

    if role=="admin":
        return jsonify({
            "message":"Login successful",
            "access_token":token,
            "role":role
        }),200

    if role=="student":

        if profile_data.get("access")==0:
            return jsonify({"error":"Access denied"}),403

        return jsonify({
            "message":"Login successful",
            "access_token":token,
            "role":role,
            "username":username,
            "first_name":profile_data.get("first_name"),
            "last_name":profile_data.get("last_name"),
            "roll_number":profile_data.get("roll_number"),
            "email":profile_data.get("email"),
            "student_phone":profile_data.get("student_phone"),
            "parent_phone":profile_data.get("parent_phone"),
            "stream":profile_data.get("stream"),
            "target_year":profile_data.get("target_year"),
            "gender":profile_data.get("gender"),
            "batch_name":profile_data.get("batch_name")
        }),200

    return jsonify({
        "message":"Login successful",
        "access_token":token,
        "role":role
    }),200

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

@app.route("/get_streams", methods=['GET'])
def get_stream_names():
    streams = database.all_streams()
    return jsonify(streams), 200

@app.route("/register_student", methods=['POST'])
@jwt_required()
@admin_required
def add_student_endpoint():
    data = request.json

    if data is None:
        return jsonify({"error": "Invaild JSON data"}), 400
    
    claims = get_jwt()
    if claims.get("role") != "admin":
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
    # return {'message': 'closed'}, 200
    allowed_tables = [
        "batches",
        "login",
        "student_profiles",
        "staff_profiles"
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

@app.route("/get_student_profile", methods=['POST'])
@jwt_required()
@admin_required
def get_student_profile():
    data = request.json

    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    profile = database.get_student_profile(username)
    if profile:
        print(profile)
        return jsonify(profile), 200
    
    return jsonify({'error': 'Student not found'}), 404

@app.route("/login_table", methods=['GET']) # security risk
def get_login_table():
    return {'message': 'closed'}, 200
    return jsonify(database.get_login_table()), 200

@app.route("/revoke_access", methods=['POST'])
@jwt_required()
@admin_required
def revoke_access():
    data = request.json
    
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username')  
    if not username:
        return jsonify({'error': 'Username required'}), 400  

    status, message = database.revoke_access(username)
    if status:
        return jsonify({'message': message}), 200
    
    return jsonify({'error': message}), 400

@app.route("/grant_access", methods=['POST'])
@jwt_required()
@admin_required
def grant_access():
    data = request.json
    
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username')  
    if not username:
        return jsonify({'error': 'Username required'}), 400  

    status, message = database.grant_access(username)
    if status:
        return jsonify({'message': message}), 200
    
    return jsonify({'error': message}), 400

@app.route("/get_all_student_profile_admin", methods=['POST'])
@jwt_required()
@admin_required
def get_all_student_profiles():
    data = request.json

    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    profiles = database.all()
    return jsonify(profiles), 200

@app.route("/students/search", methods=["POST"])
@jwt_required()
@admin_required
def search_students():

    data = request.get_json(silent=True) or {}

    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400

    search = data.get("search", "")
    batch_name = data.get("batch_name")
    stream = data.get("stream")
    target_year = data.get("target_year")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    username = data.get("username")
    roll_number = data.get("roll_number")
    min_year = data.get("min_year")
    max_year = data.get("max_year")
    access = data.get("access")

    page = int(data.get("page", 1))
    limit = int(data.get("limit", 10))
    offset = (page - 1) * limit

    rows = database.all_students(
        search=search,
        batch_name=batch_name,
        stream=stream,
        target_year=target_year,
        first_name=first_name,
        last_name=last_name,
        username=username,
        roll_number=roll_number,
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

@app.route("/login_logs",methods=["POST"])
@jwt_required()
@admin_required
def login_logs():
    data=request.get_json(silent=True) or {}

    page=int(data.get("page",1))
    limit=int(data.get("limit",50))
    offset=(page-1)*limit

    logs=database.get_login_logs(limit,offset)

    return jsonify({
        "page":page,
        "limit":limit,
        "count":len(logs),
        "logs":logs
    }),200

@app.route("/register_staff", methods=['POST'])
@jwt_required()
@admin_required
def add_staff_endpoint():
    data = request.json

    if data is None:
        return jsonify({"error": "Invaild JSON data"}), 400
    
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized Access"}), 403

    required_fields = [
        "username",
        "password",
        "first_name",
        "email",
        "phone",
        "department",
        "designation"
    ]

    # CHECK REQUIRED FIELDS
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    status, message = database.add_staff(
        username=data.get("username"),
        password=data.get("password"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name", ""),
        email=data.get("email"),
        phone=data.get("phone"),
        department=data.get("department"),
        designation=data.get("designation")
    )

    if status:
        return jsonify({
            "message": message
        }), 200

    return jsonify({
        "error": message
    }), 400


if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=7000
    )
