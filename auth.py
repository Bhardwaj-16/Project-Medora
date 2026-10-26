# auth.py - Login and Registration logic for Project MEDORA

import hashlib
from db_setup import get_connection
from mysql.connector import Error


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login(login_id: str, password: str):
    """
    Verify credentials for either Administrator or Patient.
    Returns user dict with 'is_admin': True/False on success, or None on failure.
    """
    uid = login_id.strip()
    pwd_hash = _hash(password)

    # 1. Built-in Admin check (username: admin, password: 4469)
    if uid == 'admin' and password == '4469':
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admin_users WHERE Username = 'admin'")
            admin_rec = cursor.fetchone()
            cursor.close()
            conn.close()
            if admin_rec:
                admin_rec['is_admin'] = True
                return admin_rec
        except Exception:
            pass
        return {
            'is_admin': True,
            'AdminID': 1,
            'Username': 'admin',
            'FullName': 'Chief Medical Administrator',
            'Role': 'SuperAdmin'
        }

    # 2. Query admin_users table
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM admin_users WHERE Username = %s AND Password = %s",
            (uid, pwd_hash)
        )
        admin_rec = cursor.fetchone()
        if admin_rec:
            cursor.close()
            conn.close()
            admin_rec['is_admin'] = True
            return admin_rec

        # 3. Query patient_details table
        cursor.execute(
            "SELECT * FROM patient_details WHERE LoginID = %s AND Password = %s",
            (uid, pwd_hash)
        )
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        if patient:
            patient['is_admin'] = False
            return patient

        return None
    except (Error, ConnectionError, Exception) as e:
        raise RuntimeError(f"Database query failed: {e}")


def register(pat_name: str, mobile: str, address: str, age: int,
             dob: str, weight: float, login_id: str, password: str) -> tuple:
    """
    Register a new patient.
    Returns (True, '') on success, (False, error_message) on failure.
    """
    if not all([pat_name.strip(), login_id.strip(), password]):
        return False, "Name, Login ID and Password are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if login_id.strip().lower() == 'admin':
        return False, "Username 'admin' is reserved for system administration."
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO patient_details
               (PatName, MobileNumber, Address, Age, DOB, Weight, LoginID, Password)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (pat_name.strip(), mobile.strip(), address.strip(),
             int(age) if age else None,
             dob if dob else None,
             float(weight) if weight else None,
             login_id.strip(), _hash(password))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, ""
    except Error as e:
        if e.errno == 1062:
            return False, "Login ID already exists. Please choose another."
        return False, f"Registration failed: {e}"
