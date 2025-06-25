from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, make_response
from functools import wraps
import mysql.connector
from dotenv import load_dotenv
import os
import csv
from io import StringIO
import logging
from weasyprint import HTML

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment and create Flask app
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Santino250')

def get_db_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='flask_user',
        password='secure_password',
        database='vndlv_db'
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/download_filtered_pdf')
@login_required
def download_filtered_pdf():
    if session['role'] != 'admin':
        return 'Access denied'

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    issue_filter = request.args.get('issue_filter', 'none')

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT ReportID, ReportedBy, PlateNumber, LicenseID, Timestamp, Feedback, IssueDescription FROM Reports WHERE 1=1"
    params = []

    if start_date and end_date:
        query += " AND DATE(Timestamp) BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    if issue_filter and issue_filter != "none":
        query += " AND IssueDescription = %s"
        params.append(issue_filter)

    query += " ORDER BY Timestamp DESC"
    cursor.execute(query, params)
    reports = cursor.fetchall()
    cursor.close()
    connection.close()

    html = render_template('filtered_pdf.html', reports=reports)
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=filtered_reports.pdf'
    return response

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            session['username'] = username
            session['role'] = user[2]
            return redirect(url_for('verify'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=None)

@app.route('/verify', methods=['GET'])
@login_required
def verify():
    return render_template('verify.html', username=session['username'])

@app.route('/verify_plate', methods=['POST'])
@login_required
def verify_plate():
    plate_number = request.json['plate_number']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT PlateNumber, OwnerName, RegistrationStatus, Model, Contact FROM Vehicles WHERE PlateNumber = %s", (plate_number,))
    vehicle = cursor.fetchone()
    logger.debug(f"Queried plate {plate_number}, result: {vehicle}")
    cursor.close()
    connection.close()
    if vehicle:
        return jsonify({
            'status': 'found',
            'details': {
                'plate': vehicle[0],
                'owner': vehicle[1],
                'status': vehicle[2],
                'model': vehicle[3],
                'contact': vehicle[4] if vehicle[4] else 'Not available'
            }
        })
    else:
        logger.debug(f"No vehicle found for plate {plate_number}")
        return jsonify({'status': 'not_found'})

@app.route('/verify_license', methods=['POST'])
@login_required
def verify_license():
    license_id = request.json['license_id']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Drivers WHERE LicenseID = %s", (license_id,))
    driver = cursor.fetchone()
    cursor.close()
    connection.close()
    if driver:
        return jsonify({
            'status': 'found',
            'details': {
                'license_id': driver[0],
                'name': driver[1],
                'status': driver[2]
            }
        })
    else:
        return jsonify({'status': 'not_found'})

@app.route('/report_issue', methods=['POST'])
@login_required
def report_issue():
    reported_by = session['username']
    plate_number = request.json.get('plate_number', '')
    license_id = request.json.get('license_id', '')
    issue_description = request.json.get('issue_description', '')
    logger.debug(f"Reporting issue: reported_by={reported_by}, plate_number={plate_number}, license_id={license_id}, issue={issue_description}")
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Reports (ReportedBy, PlateNumber, LicenseID, Timestamp, IssueDescription) VALUES (%s, %s, %s, NOW(), %s)",
            (reported_by, plate_number, license_id, issue_description)
        )
        connection.commit()
        logger.info(f"Report submitted for plate {plate_number} and license {license_id}")
        cursor.close()
        connection.close()
        return jsonify({'status': 'reported'})
    except Exception as e:
        logger.error(f"Error reporting issue: {str(e)}")
        cursor.close()
        connection.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if session['role'] != 'admin':
        return 'Access denied'

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    issue_filter = request.args.get('issue_filter', 'none')

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT ReportID, ReportedBy, PlateNumber, LicenseID, Timestamp, Feedback, IssueDescription FROM Reports WHERE 1=1"
    params = []

    if start_date and end_date:
        query += " AND DATE(Timestamp) BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    if issue_filter and issue_filter != "none":
        query += " AND IssueDescription = %s"
        params.append(issue_filter)

    query += " ORDER BY Timestamp DESC"
    cursor.execute(query, params)
    reports = cursor.fetchall()
    cursor.close()
    connection.close()

    if (start_date and end_date) or (issue_filter and issue_filter != "none"):
        return render_template('filtered_admin.html', reports=reports)
    
    return render_template('admin.html', reports=reports, start_date=start_date,
             end_date=end_date, issue_filter=issue_filter)

@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    if session['role'] != 'admin':
        return 'Access denied'
    report_id = request.form['report_id']
    feedback = request.form['feedback']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE Reports SET Feedback = %s WHERE ReportID = %s", (feedback, report_id))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('admin'))

@app.route('/download_reports', methods=['GET'])
@login_required
def download_reports():
    if session['role'] != 'admin':
        return 'Access denied'

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    connection = get_db_connection()
    cursor = connection.cursor()

    if start_date and end_date:
        query = "SELECT * FROM Reports WHERE DATE(Timestamp) BETWEEN %s AND %s"
        cursor.execute(query, (start_date, end_date))
    else:
        cursor.execute("SELECT * FROM Reports")

    reports = cursor.fetchall()
    cursor.close()
    connection.close()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['VNDLV SYSTEM Report'])
    cw.writerow(['ReportID', 'ReportedBy', 'PlateNumber', 'LicenseID', 'Timestamp', 'Feedback'])
    cw.writerows(reports)

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=reports.csv"}
    )

@app.route('/my_reports', methods=['GET'])
@login_required
def my_reports():
    username = session['username']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT ReportID, PlateNumber, LicenseID, Timestamp, IssueDescription, Feedback FROM Reports WHERE ReportedBy = %s ORDER BY Timestamp DESC",
        (username,)
    )
    reports = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('my_reports.html', reports=reports, username=username)

@app.route('/plate_history/<plate_number>')
@login_required
def plate_history(plate_number):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT Timestamp, ReportedBy, IssueDescription FROM Reports WHERE PlateNumber = %s ORDER BY Timestamp DESC",
        (plate_number,)
    )
    history = cursor.fetchall()
    cursor.close()
    connection.close()

    history_data = [{'timestamp': str(row[0]), 'user': row[1], 'issue': row[2]} for row in history] if history else []
    issue_count = len(history_data)

    return render_template('history.html', plate_number=plate_number, history=history_data, issue_count=issue_count)

@app.route('/sync_vehicles', methods=['POST'])
@login_required
def sync_vehicles():
    if session['role'] != 'admin':
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW COLUMNS FROM Vehicles LIKE 'Contact'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Vehicles ADD Contact VARCHAR(15)")
        cursor.execute("SELECT COUNT(*) FROM Vehicles")
        count = cursor.fetchone()[0]
        if count == 0:
            return jsonify({'status': 'error', 'message': 'Vehicles table is empty. Run init_vehicles.sql to populate.'}), 400
        cursor.close()
        connection.close()
        logger.info("Vehicles table checked successfully")
        return jsonify({'status': 'success', 'message': 'Vehicles table already populated'})
    except Exception as e:
        logger.error(f"Error checking vehicles: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
