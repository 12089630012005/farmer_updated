from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)
#     farmers = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify(farmers)

# # API: Add Crop Type
# @app.route('/add_crop', methods=['POST'])
# def add_crop():
#     data = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     sql = "INSERT INTO CropTypes (name, category) VALUES (%s, %s)"
#     cursor.execute(sql, (data['name'], data['category']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return jsonify({"message": "Crop added successfully"})

# # API: Get Crops
# @app.route('/get_crops', methods=['GET'])
# def get_crops():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM CropTypes")
#     crops = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify(crops)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for, make_response, session
from flask_babel import Babel, gettext as _, lazy_gettext as _l
from werkzeug.utils import secure_filename
import os
import mysql.connector

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = 'change-this-secret'  # required for sessions

# ------------------ i18n / Flask-Babel ------------------
# Supported Indian locales. Keys should match translation folder names under 'translations'.
SUPPORTED_LANGUAGES = [
    "en",  # English
    "hi",  # Hindi
    "mr",  # Marathi
    "ta",  # Tamil
    "te",  # Telugu
    "bn",  # Bengali
    "gu",  # Gujarati
    "kn",  # Kannada
    "ml",  # Malayalam
    "pa",  # Punjabi
]

app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

def select_locale():
    # Priority: explicit query param > cookie > Accept-Language header
    lang_from_query = request.args.get("lang")
    if lang_from_query and lang_from_query in SUPPORTED_LANGUAGES:
        return lang_from_query

    lang_from_cookie = request.cookies.get("lang")
    if lang_from_cookie and lang_from_cookie in SUPPORTED_LANGUAGES:
        return lang_from_cookie

    return request.accept_languages.best_match(SUPPORTED_LANGUAGES) or app.config["BABEL_DEFAULT_LOCALE"]

# For Flask-Babel >= 3.0
babel = Babel(app, locale_selector=select_locale)

# ------------------ Language Helpers ------------------
LANG_NAME_TO_CODE = {
    "english": "en",
    "en": "en",
    "hindi": "hi",
    "hi": "hi",
    "marathi": "mr",
    "mr": "mr",
    "tamil": "ta",
    "ta": "ta",
    "telugu": "te",
    "te": "te",
    "bengali": "bn",
    "bangla": "bn",
    "bn": "bn",
    "gujarati": "gu",
    "gu": "gu",
    "kannada": "kn",
    "kn": "kn",
    "malayalam": "ml",
    "ml": "ml",
    "punjabi": "pa",
    "pa": "pa",
}

def normalize_language_code(lang_value: str) -> str:
    if not lang_value:
        return None
    key = str(lang_value).strip().lower()
    code = LANG_NAME_TO_CODE.get(key, None)
    if code in SUPPORTED_LANGUAGES:
        return code
    # If user already passed a code like 'hi-IN', trim region
    short = key.split("-")[0]
    if short in SUPPORTED_LANGUAGES:
        return short
    return None

# ------------------ File Upload Config ------------------
UPLOAD_SUBDIR = os.path.join('public', 'uploads')
UPLOAD_DIR = os.path.join(app.root_path, 'public', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_AUDIO_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "webm"}

def is_allowed_image_filename(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS

def is_allowed_audio_filename(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_AUDIO_EXTENSIONS

# ------------------ DB Connection ------------------
def get_db_config():
    """Read DB config from environment (for Docker/production). Fallbacks for local dev."""
    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "farmer_updated"),
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
        "use_unicode": True,
    }


def get_db_connection():
    cfg = get_db_config()
    conn = mysql.connector.connect(**cfg)
    return conn


# ------------------ Serve Frontend ------------------
@app.route('/')
def index():
    return render_template("index.html")


# ------------------ Language Setter ------------------
@app.route('/set_language', methods=['GET', 'POST'])
def set_language():
    try:
        # Accept JSON or form-encoded
        data = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or data.get('lang')
        
        if not lang or lang not in SUPPORTED_LANGUAGES:
            return jsonify({"error": "Invalid language"}), 400

        # Set session
        session['lang'] = lang
        
        # Create response with proper headers
        resp = make_response(jsonify({"success": True, "lang": lang}))
        resp.set_cookie('lang', lang, max_age=60*60*24*180, samesite='Lax', secure=False, httponly=False)
        
        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ STATIC VIDEO FOR LANDING ------------------
#@app.route('/landing_video')
#def landing_video():
    # Serve the requested video from absolute path
    # Update this filename if you change the file or location.
    #video_path = r"C:\Users\shri\Downloads\farming-main (1)\farming-main\static\videos\landing_video.mp4"
    #return send_file(video_path, mimetype='video/mp4', conditional=True)
@app.route('/add_farmer', methods=['POST'])
def add_farmer():
    data = request.get_json(silent=True) or {}
    try:
        required = ['name', 'location', 'language', 'field_size', 'contact_info']
        for field in required:
            if field not in data or data[field] in (None, ""):
                return jsonify({"message": f"{field} is required"}), 400

        # Normalize language to supported locale code
        normalized_lang = normalize_language_code(data.get('language'))
        if not normalized_lang:
            return jsonify({"message": "Unsupported language"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO Farmers (name, location, language, field_size, contact_info) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            data['name'],
            data['location'],
            normalized_lang,
            data['field_size'],
            data['contact_info']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        # Also set cookie so UI switches immediately
        resp = make_response(jsonify({"message": "Farmer added successfully", "lang": normalized_lang}))
        resp.set_cookie('lang', normalized_lang, max_age=60*60*24*180, samesite='Lax')
        return resp
    except Exception as e:
        return jsonify({"message": f"Error adding farmer: {str(e)}"}), 500


@app.route('/get_farmers', methods=['GET'])
def get_farmers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Farmers")
    farmers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(farmers)


@app.route('/update_farmer', methods=['POST'])
def update_farmer():
    try:
        data = request.get_json(silent=True) or {}
        farmer_id = data.get('FarmerID')
        if not farmer_id:
            return jsonify({"message": "FarmerID is required"}), 400

        # Build update fields dynamically but only for allowed columns
        allowed_fields = ['name', 'location', 'language', 'field_size', 'contact_info']
        updates = []
        values = []
        for key in allowed_fields:
            if key in data and data[key] not in (None, ""):
                if key == 'language':
                    normalized_lang = normalize_language_code(data[key])
                    if not normalized_lang:
                        return jsonify({"message": "Unsupported language"}), 400
                    updates.append(f"{key} = %s")
                    values.append(normalized_lang)
                else:
                    updates.append(f"{key} = %s")
                    values.append(data[key])

        if not updates:
            return jsonify({"message": "No updatable fields provided"}), 400

        values.append(int(farmer_id))

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = f"UPDATE Farmers SET {', '.join(updates)} WHERE FarmerID = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        cursor.close()
        conn.close()
        # If language was updated, set cookie as well
        if 'language' in data and data['language'] not in (None, ""):
            lang_code = normalize_language_code(data['language'])
            if lang_code:
                resp = make_response(jsonify({"message": "Farmer updated successfully", "lang": lang_code}))
                resp.set_cookie('lang', lang_code, max_age=60*60*24*180, samesite='Lax')
                return resp
        return jsonify({"message": "Farmer updated successfully"})
    except Exception as e:
        return jsonify({"message": f"Error updating farmer: {str(e)}"}), 500


@app.route('/get_farmer_by_email', methods=['GET'])
def get_farmer_by_email():
    """Get farmer by email (contact_info) - used for Firebase auth mapping"""
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"message": "Email parameter required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Farmers WHERE contact_info = %s LIMIT 1", (email,))
        farmer = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if farmer:
            return jsonify(farmer)
        else:
            return jsonify({"message": "Farmer not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# ------------------ CROPS ------------------
@app.route('/add_crop', methods=['POST'])
def add_crop():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO CropTypes (name, category) VALUES (%s, %s)"
    cursor.execute(sql, (data['name'], data['category']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Crop added successfully"})


@app.route('/get_crops', methods=['GET'])
def get_crops():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CropTypes")
    crops = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(crops)


# ------------------ QUERIES ------------------
@app.route('/add_query', methods=['POST'])
def add_query():
    try:
        # Support JSON or multipart form-data (FormData)
        if request.content_type and 'multipart/form-data' in request.content_type:
            form = request.form
            FarmerID = int(form.get('FarmerID')) if form.get('FarmerID') else None
            title = form.get('title')
            description = form.get('description')
            crop_type = int(form.get('crop_type')) if form.get('crop_type') else None
            # Optional image handling: accept uploaded file or URL in image_url
            image_url = form.get('image_url')
            audio_url = form.get('audio_url')
            file = request.files.get('image')
            if file and file.filename:
                if not is_allowed_image_filename(file.filename):
                    return jsonify({"message": "Unsupported image type"}), 400
                filename = secure_filename(file.filename)
                # Ensure unique filename to avoid collisions
                base, ext = os.path.splitext(filename)
                unique_name = filename
                counter = 1
                while os.path.exists(os.path.join(UPLOAD_DIR, unique_name)):
                    unique_name = f"{base}_{counter}{ext}"
                    counter += 1
                file.save(os.path.join(UPLOAD_DIR, unique_name))
                # Public URL path served via Flask static from 'public'
                image_url = f"/uploads/{unique_name}"

            # Optional audio handling: accept uploaded file or URL in audio_url
            audio_file = request.files.get('audio')
            if audio_file and audio_file.filename:
                if not is_allowed_audio_filename(audio_file.filename):
                    return jsonify({"message": "Unsupported audio type"}), 400
                filename = secure_filename(audio_file.filename)
                base, ext = os.path.splitext(filename)
                unique_name = filename
                counter = 1
                while os.path.exists(os.path.join(UPLOAD_DIR, unique_name)):
                    unique_name = f"{base}_{counter}{ext}"
                    counter += 1
                audio_file.save(os.path.join(UPLOAD_DIR, unique_name))
                audio_url = f"/uploads/{unique_name}"
        else:
            data = request.get_json(silent=True) or {}
            FarmerID = int(data.get('FarmerID')) if data.get('FarmerID') is not None else None
            title = data.get('title')
            description = data.get('description')
            crop_type = int(data.get('crop_type')) if data.get('crop_type') is not None else None
            image_url = data.get('image_url')
            audio_url = data.get('audio_url')

        if not FarmerID or not title:
            return jsonify({"message": "FarmerID and title are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO Queries (FarmerID, title, description, image_url, audio_url, crop_type) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (FarmerID, title, description, image_url, audio_url, crop_type))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Query added successfully"})
    except Exception as e:
        return jsonify({"message": f"Error adding query: {str(e)}"}), 500


@app.route('/get_queries', methods=['GET'])
def get_queries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT q.*, (
            SELECT COUNT(*) FROM Responses r WHERE r.QueryID = q.QueryID
        ) AS responses_count
        FROM Queries q
        ORDER BY q.QueryID DESC
        """
    )
    queries = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(queries)


# ------------------ RESPONSES ------------------
@app.route('/add_response', methods=['POST'])
def add_response():
    try:
        data = request.get_json(silent=True) or {}
        required = ['QueryID', 'ResponderID', 'response_text']
        for f in required:
            if f not in data or data[f] in (None, ""):
                return jsonify({"message": f"{f} is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        # Prevent responding to own query
        cursor.execute("SELECT FarmerID FROM Queries WHERE QueryID = %s", (int(data['QueryID']),))
        row = cursor.fetchone()
        if not row:
            cursor.close(); conn.close()
            return jsonify({"message": "Query not found"}), 400
        owner_id = int(row[0])
        if int(data['ResponderID']) == owner_id:
            cursor.close(); conn.close()
            return jsonify({"message": "You cannot respond to your own query"}), 400

        sql = """INSERT INTO Responses (QueryID, ResponderID, response_text, is_expert, votes) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            int(data['QueryID']),
            int(data['ResponderID']),
            data['response_text'],
            bool(data.get('is_expert', False)),
            int(data.get('votes', 0))
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Response added successfully"})
    except Exception as e:
        return jsonify({"message": f"Error adding response: {str(e)}"}), 500


@app.route('/get_responses', methods=['GET'])
def get_responses():
    try:
        query_id = request.args.get('query_id', type=int)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if query_id is not None:
            cursor.execute("SELECT * FROM Responses WHERE QueryID = %s", (query_id,))
        else:
            cursor.execute("SELECT * FROM Responses")
        responses = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(responses)
    except Exception as e:
        return jsonify({"message": f"Error fetching responses: {str(e)}"}), 500


@app.route('/vote_response', methods=['POST'])
def vote_response():
    try:
        data = request.get_json(silent=True) or {}
        response_id = data.get('ResponseID')
        delta = int(data.get('delta', 1))
        if not response_id:
            return jsonify({"message": "ResponseID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Responses SET votes = COALESCE(votes,0) + %s WHERE ResponseID = %s", (delta, int(response_id)))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Vote recorded"})
    except Exception as e:
        return jsonify({"message": f"Error voting response: {str(e)}"}), 500


# ------------------ TOGGLE LIKE (one per user) ------------------
@app.route('/toggle_like', methods=['POST'])
def toggle_like():
    try:
        data = request.get_json(silent=True) or {}
        response_id = data.get('ResponseID')
        farmer_id = data.get('FarmerID')
        if not response_id or not farmer_id:
            return jsonify({"message": "ResponseID and FarmerID are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        # Ensure likes table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ResponseLikes (
                ResponseID INT NOT NULL,
                FarmerID INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ResponseID, FarmerID)
            )
            """
        )
        # Check if already liked
        cursor.execute("SELECT 1 FROM ResponseLikes WHERE ResponseID=%s AND FarmerID=%s", (int(response_id), int(farmer_id)))
        exists = cursor.fetchone() is not None
        if exists:
            # Unlike: remove record, decrement vote (min 0)
            cursor.execute("DELETE FROM ResponseLikes WHERE ResponseID=%s AND FarmerID=%s", (int(response_id), int(farmer_id)))
            cursor.execute("UPDATE Responses SET votes = GREATEST(COALESCE(votes,0) - 1, 0) WHERE ResponseID = %s", (int(response_id),))
            conn.commit()
            cursor.close(); conn.close()
            return jsonify({"liked": False, "message": "Unliked"})
        else:
            # Like: insert record, increment vote
            cursor.execute("INSERT INTO ResponseLikes (ResponseID, FarmerID) VALUES (%s, %s)", (int(response_id), int(farmer_id)))
            cursor.execute("UPDATE Responses SET votes = COALESCE(votes,0) + 1 WHERE ResponseID = %s", (int(response_id),))
            conn.commit()
            cursor.close(); conn.close()
            return jsonify({"liked": True, "message": "Liked"})
    except Exception as e:
        return jsonify({"message": f"Error toggling like: {str(e)}"}), 500
# ------------------ EQUIPMENT ------------------
@app.route('/add_equipment', methods=['POST'])
def add_equipment():
    try:
        data = request.get_json(silent=True) or {}

        required = ['OwnerID', 'name', 'type', 'condition', 'hourly_rate']
        for field in required:
            if field not in data or data[field] in (None, ""):
                return jsonify({"message": f"{field} is required"}), 400

        owner_id = int(data['OwnerID'])
        hourly_rate = float(data['hourly_rate'])
        availability = data.get('availability_status', 'Available')
        if availability not in ['Available', 'Unavailable']:
            return jsonify({"message": "availability_status must be 'Available' or 'Unavailable'"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Validate that the owner exists to satisfy FK
        cursor.execute("SELECT FarmerID FROM Farmers WHERE FarmerID = %s", (owner_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return jsonify({"message": "OwnerID does not exist"}), 400

        sql = """INSERT INTO Equipment (OwnerID, name, type, `condition`, hourly_rate, availability_status) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            owner_id,
            data['name'],
            data['type'],
            data['condition'],
            hourly_rate,
            availability
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Equipment added successfully"})
    except Exception as e:
        return jsonify({"message": f"Error adding equipment: {str(e)}"}), 500


@app.route('/get_equipment', methods=['GET'])
def get_equipment():
    """Optionally filter by owner_id, exclude_owner_id, availability."""
    try:
        owner_id = request.args.get('owner_id', type=int)
        exclude_owner_id = request.args.get('exclude_owner_id', type=int)
        availability = request.args.get('availability')  # 'Available' or 'Unavailable'

        where = []
        params = []
        if owner_id is not None:
            where.append("OwnerID = %s")
            params.append(owner_id)
        if exclude_owner_id is not None:
            where.append("OwnerID <> %s")
            params.append(exclude_owner_id)
        if availability in ('Available', 'Unavailable'):
            where.append("availability_status = %s")
            params.append(availability)

        sql = "SELECT * FROM Equipment"
        if where:
            sql += " WHERE " + " AND ".join(where)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, tuple(params))
        equipment = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(equipment)
    except Exception as e:
        return jsonify({"message": f"Error fetching equipment: {str(e)}"}), 500


# ------------------ LENDING REQUESTS ------------------
@app.route('/add_lending_request', methods=['POST'])
def add_lending_request():
    try:
        data = request.json

        # Validate required fields (LenderID is derived on server)
        required_fields = ['EquipmentID', 'BorrowerID', 'start_date', 'duration']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"message": _("%s is required") % field}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Always set LenderID to the equipment owner (ignore client-passed LenderID)
        cursor.execute("SELECT OwnerID FROM Equipment WHERE EquipmentID = %s", (int(data['EquipmentID']),))
        row = cursor.fetchone()
        if row is None:
            cursor.close(); conn.close()
            return jsonify({"message": _("Equipment not found")}), 400
        owner_id = int(row[0])

        if int(data['BorrowerID']) == owner_id:
            cursor.close(); conn.close()
            return jsonify({"message": _("Owner cannot borrow own equipment")}), 400

        sql = """INSERT INTO LendingRequests 
                 (EquipmentID, LenderID, BorrowerID, start_date, duration, status) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""

        cursor.execute(sql, (
            int(data['EquipmentID']),
            owner_id,
            int(data['BorrowerID']),
            data['start_date'],          # YYYY-MM-DD format
            int(data['duration']),
            data.get('status', 'Pending')
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": _("Lending request added successfully")})

    except Exception as e:
        print("Error adding lending request:", e)
        return jsonify({"message": _("Error adding lending request: %s") % str(e)}), 500


@app.route('/get_lending_requests', methods=['GET'])
def get_lending_requests():
    try:
        borrower_id = request.args.get('borrower_id', type=int)
        lender_id = request.args.get('lender_id', type=int)

        where = []
        params = []
        if borrower_id is not None:
            where.append("lr.BorrowerID = %s")
            params.append(borrower_id)
        if lender_id is not None:
            where.append("lr.LenderID = %s")
            params.append(lender_id)

        base_sql = (
            "SELECT lr.*, e.name AS equipment_name, f1.name AS lender_name, f2.name AS borrower_name "
            "FROM LendingRequests lr "
            "JOIN Equipment e ON lr.EquipmentID = e.EquipmentID "
            "JOIN Farmers f1 ON lr.LenderID = f1.FarmerID "
            "JOIN Farmers f2 ON lr.BorrowerID = f2.FarmerID"
        )
        if where:
            base_sql += " WHERE " + " AND ".join(where)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(base_sql, tuple(params))
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(requests)
    except Exception as e:
        print("Error fetching lending requests:", e)
        return jsonify({"message": f"Error fetching lending requests: {str(e)}"}), 500



@app.route('/update_lending_request_status', methods=['POST'])
def update_lending_request_status():
    try:
        data = request.get_json(silent=True) or {}
        request_id = data.get('RequestID')
        new_status = data.get('status')

        if not request_id or not new_status:
            return jsonify({"message": _("RequestID and status are required")}), 400

        # Align with DB enum: Pending, Approved, Rejected, Completed
        if new_status not in ['Pending', 'Approved', 'Rejected', 'Completed']:
            return jsonify({"message": _("Invalid status")}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE LendingRequests SET status = %s WHERE RequestID = %s", (new_status, int(request_id)))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": _("Lending request updated")})
    except Exception as e:
        print("Error updating lending request:", e)
        return jsonify({"message": _("Error updating lending request: %s") % str(e)}), 500


# ------------------ DELETE ENDPOINTS ------------------
@app.route('/delete_equipment', methods=['POST'])
def delete_equipment():
    """Delete equipment by ID. Requires OwnerID to match for safety."""
    try:
        data = request.get_json(silent=True) or {}
        equipment_id = data.get('EquipmentID')
        owner_id = data.get('OwnerID')
        if not equipment_id or not owner_id:
            return jsonify({"message": "EquipmentID and OwnerID are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        # verify ownership
        cursor.execute("SELECT OwnerID FROM Equipment WHERE EquipmentID=%s", (int(equipment_id),))
        row = cursor.fetchone()
        if not row:
            cursor.close(); conn.close()
            return jsonify({"message": "Equipment not found"}), 404
        if int(row[0]) != int(owner_id):
            cursor.close(); conn.close()
            return jsonify({"message": "Not authorized to delete this equipment"}), 403

        # delete any dependent lending requests first (to satisfy FK if exists)
        try:
            cursor.execute("DELETE FROM LendingRequests WHERE EquipmentID=%s", (int(equipment_id),))
        except Exception:
            pass
        cursor.execute("DELETE FROM Equipment WHERE EquipmentID=%s", (int(equipment_id),))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"message": "Equipment deleted"})
    except Exception as e:
        return jsonify({"message": f"Error deleting equipment: {str(e)}"}), 500


@app.route('/delete_lending_request', methods=['POST'])
def delete_lending_request():
    """Borrower can cancel their pending lending request."""
    try:
        data = request.get_json(silent=True) or {}
        request_id = data.get('RequestID')
        borrower_id = data.get('BorrowerID')
        if not request_id or not borrower_id:
            return jsonify({"message": _("RequestID and BorrowerID are required")}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BorrowerID, status FROM LendingRequests WHERE RequestID=%s", (int(request_id),))
        row = cursor.fetchone()
        if not row:
            cursor.close(); conn.close()
            return jsonify({"message": _("Lending request not found")}), 404
        if int(row[0]) != int(borrower_id):
            cursor.close(); conn.close()
            return jsonify({"message": _("Not authorized to cancel this request")}), 403
        if row[1] != 'Pending':
            cursor.close(); conn.close()
            return jsonify({"message": _("Only pending requests can be cancelled")}), 400

        cursor.execute("DELETE FROM LendingRequests WHERE RequestID=%s", (int(request_id),))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"message": _("Request cancelled")})
    except Exception as e:
        return jsonify({"message": _("Error cancelling request: %s") % str(e)}), 500


@app.route('/delete_crop', methods=['POST'])
def delete_crop():
    try:
        data = request.get_json(silent=True) or {}
        crop_type_id = data.get('CropTypeID')
        if not crop_type_id:
            return jsonify({"message": "CropTypeID is required"}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CropTypes WHERE CropTypeID=%s", (int(crop_type_id),))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"message": "Crop deleted"})
    except Exception as e:
        return jsonify({"message": f"Error deleting crop: {str(e)}"}), 500


# ------------------ REVIEWS ------------------
@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO Reviews (FromFarmerID, ToFarmerID, rating, feedback, type) 
             VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(sql, (data['FromFarmerID'], data['ToFarmerID'], data['rating'],
                         data['feedback'], data['type']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": _("Review added successfully")})


@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reviews")
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(reviews)


# ------------------ MAIN ------------------
if __name__ == '__main__':
    app.run(debug=True)
