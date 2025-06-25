import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    """Connect to the MySQL database."""
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return connection

def verify_user(username, password):
    """Verify user credentials."""
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM Users WHERE Username = %s AND Password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

def get_vehicle_details(plate_number):
    """Get vehicle details by plate number."""
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM Vehicles WHERE PlateNumber = %s"
    cursor.execute(query, (plate_number,))
    vehicle = cursor.fetchone()
    cursor.close()
    connection.close()
    return vehicle

def get_driver_details(license_id):
    """Get driver details by license ID."""
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM Drivers WHERE LicenseID = %s"
    cursor.execute(query, (license_id,))
    driver = cursor.fetchone()
    cursor.close()
    connection.close()
    return driver

def report_issue(reported_by, plate_number, license_id):
    """Log a report in the database."""
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO Reports (ReportedBy, PlateNumber, LicenseID, Timestamp) VALUES (%s, %s, %s, NOW())"
    cursor.execute(query, (reported_by, plate_number, license_id))
    connection.commit()
    cursor.close()
    connection.close()
