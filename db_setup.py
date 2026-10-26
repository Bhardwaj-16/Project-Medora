# db_setup.py - Database connection, setup.

import mysql.connector
from mysql.connector import Error
import hashlib
import sys

# ─── Database Configuration ───────────────────────────────────────────────────
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'medora_db',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True,
}


def _hash(password: str) -> str:
    """Return SHA-256 hex digest of a plaintext password."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
    """Return a live MySQL connection using db_config."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        raise ConnectionError(f"Cannot connect to MySQL: {e}")


def _get_root_connection():
    """Connect without specifying a database (for initial setup)."""
    cfg = {k: v for k, v in db_config.items() if k != 'database'}
    return mysql.connector.connect(**cfg)


def setup_database():
    """Create database, tables and insert sample data (idempotent)."""
    try:
        # 1. Create database if not exists
        root_conn = _get_root_connection()
        root_cursor = root_conn.cursor()
        root_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {db_config['database']} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        root_cursor.close()
        root_conn.close()

        # 2. Use the database
        conn = get_connection()
        cursor = conn.cursor()

        # ── Create Tables ────────────────────────────────────────────────────

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_details (
                PatID         INT PRIMARY KEY AUTO_INCREMENT,
                PatName       VARCHAR(100)  NOT NULL,
                MobileNumber  VARCHAR(15),
                Address       TEXT,
                Age           INT,
                DOB           DATE,
                Weight        DECIMAL(5,2),
                LoginID       VARCHAR(50)   UNIQUE NOT NULL,
                Password      VARCHAR(255)  NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_test_results (
                ResultID     INT PRIMARY KEY AUTO_INCREMENT,
                PatID        INT  NOT NULL,
                TestDate     DATE NOT NULL,
                RBC          DECIMAL(5,2),
                WBC          DECIMAL(7,2),
                Haemoglobin  DECIMAL(5,2),
                Platelets    DECIMAL(7,2),
                TLC          DECIMAL(7,2),
                Neutrophils  DECIMAL(5,2),
                Lymphocytes  DECIMAL(5,2),
                Eosinophils  DECIMAL(5,2),
                Basophils    DECIMAL(5,2),
                Monocytes    DECIMAL(5,2),
                FOREIGN KEY (PatID) REFERENCES patient_details(PatID)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests_catalog (
                TestID      INT PRIMARY KEY AUTO_INCREMENT,
                TestName    VARCHAR(100),
                Description TEXT,
                Category    VARCHAR(50),
                Price       DECIMAL(8,2)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests_assigned (
                AssignID   INT PRIMARY KEY AUTO_INCREMENT,
                PatID      INT NOT NULL,
                TestID     INT NOT NULL,
                AssignDate DATE,
                Status     VARCHAR(20) DEFAULT 'Pending',
                Notes      TEXT,
                FOREIGN KEY (PatID)  REFERENCES patient_details(PatID)
                    ON DELETE CASCADE,
                FOREIGN KEY (TestID) REFERENCES tests_catalog(TestID)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctor_catalog (
                DoctorID        INT PRIMARY KEY AUTO_INCREMENT,
                DoctorName      VARCHAR(100),
                Speciality      VARCHAR(100),
                YearsExperience INT,
                Qualification   VARCHAR(200),
                ContactNumber   VARCHAR(15)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_doctor_assignment (
                AssignID   INT PRIMARY KEY AUTO_INCREMENT,
                PatID      INT NOT NULL,
                DoctorID   INT NOT NULL,
                AssignDate DATE,
                Notes      TEXT,
                FOREIGN KEY (PatID)     REFERENCES patient_details(PatID)
                    ON DELETE CASCADE,
                FOREIGN KEY (DoctorID)  REFERENCES doctor_catalog(DoctorID)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                AdminID   INT PRIMARY KEY AUTO_INCREMENT,
                Username  VARCHAR(50) UNIQUE NOT NULL,
                Password  VARCHAR(255) NOT NULL,
                FullName  VARCHAR(100) DEFAULT 'System Administrator',
                Role      VARCHAR(50)  DEFAULT 'SuperAdmin'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── Seed admin_users ─────────────────────────────────────────────────
        cursor.execute("SELECT AdminID FROM admin_users WHERE Username = 'admin'")
        admin_row = cursor.fetchone()
        if not admin_row:
            cursor.execute("""
                INSERT INTO admin_users (Username, Password, FullName, Role)
                VALUES ('admin', %s, 'Chief Medical Administrator', 'SuperAdmin')
            """, (_hash('4469'),))
        else:
            # Ensure password is set to 4469
            cursor.execute("""
                UPDATE admin_users SET Password = %s WHERE Username = 'admin'
            """, (_hash('4469'),))

        # ── Seed patient_details ─────────────────────────────────────────────

        cursor.execute("SELECT COUNT(*) FROM patient_details")
        if cursor.fetchone()[0] == 0:
            patients = [
                ('Arjun Sharma',       '9876543210',
                 '42 Lajpat Nagar, New Delhi - 110024',
                 34, '1990-03-15', 72.5, 'arjun.sharma',  _hash('arjun123')),
                ('Priya Mehta',        '9823456789',
                 '15 Koregaon Park, Pune - 411001',
                 28, '1996-07-22', 58.0, 'priya.mehta',   _hash('priya456')),
                ('Ravi Krishnamurthy', '9711234567',
                 '8 Adyar, Chennai - 600020',
                 45, '1979-11-08', 80.2, 'ravi.krishna',  _hash('ravi789')),
                ('Sneha Patel',        '9654321098',
                 '27 Navrangpura, Ahmedabad - 380009',
                 31, '1993-05-30', 55.5, 'sneha.patel',   _hash('sneha321')),
                ('Vikram Nair',        '9887654321',
                 '3 Indiranagar, Bengaluru - 560038',
                 52, '1972-09-14', 88.0, 'vikram.nair',   _hash('vikram654')),
            ]
            cursor.executemany("""
                INSERT INTO patient_details
                    (PatName, MobileNumber, Address, Age, DOB,
                     Weight, LoginID, Password)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, patients)

        # ── Seed blood_test_results ──────────────────────────────────────────

        cursor.execute("SELECT COUNT(*) FROM blood_test_results")
        if cursor.fetchone()[0] == 0:
            blood_data = [
                # Arjun Sharma (PatID=1) - 3 entries
                (1,'2024-01-10', 5.0, 7.2, 14.5, 230.0, 7.2, 62.0, 28.0, 2.5, 0.5, 4.0),
                (1,'2024-04-15', 4.8, 6.8, 13.9, 215.0, 6.8, 60.0, 30.0, 3.0, 0.4, 3.8),
                (1,'2024-07-20', 5.1, 7.5, 15.0, 240.0, 7.5, 65.0, 26.0, 2.0, 0.5, 4.5),

                # Priya Mehta (PatID=2) - 3 entries
                (2,'2024-02-05', 4.5, 6.0, 12.8, 200.0, 6.0, 55.0, 35.0, 3.0, 0.3, 4.5),
                (2,'2024-05-10', 4.3, 5.8, 12.2, 195.0, 5.8, 54.0, 36.0, 3.5, 0.4, 4.8),
                (2,'2024-08-18', 4.6, 6.2, 13.0, 210.0, 6.2, 57.0, 33.0, 2.8, 0.3, 4.2),

                # Ravi Krishnamurthy (PatID=3) - 4 entries (slightly abnormal)
                (3,'2024-01-20', 3.8, 12.5, 11.2, 140.0,12.5, 75.0, 18.0, 4.5, 0.8, 6.5),
                (3,'2024-03-25', 3.6, 13.0, 10.8, 130.0,13.0, 78.0, 16.0, 5.0, 0.9, 6.8),
                (3,'2024-06-10', 4.0, 11.8, 11.8, 155.0,11.8, 72.0, 20.0, 4.0, 0.7, 6.0),
                (3,'2024-09-15', 4.2, 10.5, 12.5, 165.0,10.5, 68.0, 22.0, 3.5, 0.6, 5.5),

                # Sneha Patel (PatID=4) - 2 entries
                (4,'2024-03-08', 4.4, 6.5, 12.5, 220.0, 6.5, 58.0, 32.0, 2.5, 0.4, 4.0),
                (4,'2024-09-22', 4.6, 6.8, 13.2, 235.0, 6.8, 60.0, 30.0, 2.8, 0.3, 4.2),

                # Vikram Nair (PatID=5) - 4 entries
                (5,'2023-12-01', 4.9, 8.0, 14.0, 180.0, 8.0, 63.0, 27.0, 3.0, 0.5, 4.8),
                (5,'2024-02-20', 4.7, 8.5, 13.5, 175.0, 8.5, 65.0, 25.0, 3.5, 0.6, 5.0),
                (5,'2024-05-30', 5.0, 7.8, 14.5, 190.0, 7.8, 61.0, 28.0, 3.2, 0.5, 4.6),
                (5,'2024-08-25', 4.8, 8.2, 14.0, 185.0, 8.2, 64.0, 26.0, 3.0, 0.5, 4.7),
            ]
            cursor.executemany("""
                INSERT INTO blood_test_results
                    (PatID, TestDate, RBC, WBC, Haemoglobin, Platelets,
                     TLC, Neutrophils, Lymphocytes, Eosinophils,
                     Basophils, Monocytes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, blood_data)

        # ── Seed tests_catalog ───────────────────────────────────────────────

        cursor.execute("SELECT COUNT(*) FROM tests_catalog")
        if cursor.fetchone()[0] == 0:
            tests = [
                ('Complete Blood Picture (CBC)',
                 'Full blood count including RBC, WBC, platelets and differentials.',
                 'Haematology', 350.00),
                ('Liver Function Test (LFT)',
                 'Panel of blood tests evaluating liver health and function.',
                 'Biochemistry', 650.00),
                ('Kidney Function Test (KFT)',
                 'Creatinine, BUN and eGFR to assess kidney function.',
                 'Biochemistry', 550.00),
                ('Lipid Profile',
                 'Total cholesterol, HDL, LDL and triglycerides.',
                 'Biochemistry', 500.00),
                ('Thyroid Function Test (TFT)',
                 'TSH, T3 and T4 levels to assess thyroid function.',
                 'Endocrinology', 800.00),
                ('HbA1c (Glycated Haemoglobin)',
                 '3-month average blood sugar control indicator.',
                 'Diabetology', 450.00),
                ('Urine Routine & Microscopy',
                 'Physical, chemical and microscopic examination of urine.',
                 'Microbiology', 150.00),
                ('Chest X-Ray',
                 'PA view X-Ray of the chest for lung and cardiac assessment.',
                 'Radiology', 400.00),
                ('ECG',
                 '12-lead electrocardiogram for cardiac rhythm and activity.',
                 'Cardiology', 300.00),
                ('Vitamin D & B12 Panel',
                 'Serum Vitamin D (25-OH) and Vitamin B12 levels.',
                 'Nutrition', 1200.00),
            ]
            cursor.executemany("""
                INSERT INTO tests_catalog (TestName, Description, Category, Price)
                VALUES (%s,%s,%s,%s)
            """, tests)

        # ── Seed tests_assigned ──────────────────────────────────────────────

        cursor.execute("SELECT COUNT(*) FROM tests_assigned")
        if cursor.fetchone()[0] == 0:
            assigned_tests = [
                # Arjun Sharma
                (1, 1, '2024-01-10', 'Completed', 'Routine annual check'),
                (1, 4, '2024-04-15', 'Completed', 'Follow-up lipid profile'),
                (1, 6, '2024-07-20', 'Pending',   'Diabetes screening'),
                # Priya Mehta
                (2, 1, '2024-02-05', 'Completed', 'General health check'),
                (2, 5, '2024-05-10', 'Completed', 'Thyroid workup'),
                (2, 7, '2024-08-18', 'Pending',   'Routine urine test'),
                # Ravi Krishnamurthy
                (3, 1, '2024-01-20', 'Completed', 'CBC for anaemia workup'),
                (3, 2, '2024-03-25', 'Completed', 'LFT - follow up'),
                (3, 3, '2024-06-10', 'Completed', 'KFT monitoring'),
                (3, 9, '2024-09-15', 'Pending',   'Cardiac evaluation ECG'),
                # Sneha Patel
                (4, 1, '2024-03-08', 'Completed', 'Annual blood test'),
                (4, 10,'2024-09-22', 'Pending',   'Vitamin D deficiency check'),
                # Vikram Nair
                (5, 1, '2023-12-01', 'Completed', 'Routine CBC'),
                (5, 4, '2024-02-20', 'Completed', 'Lipid screening'),
                (5, 8, '2024-05-30', 'Cancelled', 'Chest X-ray - rescheduled'),
                (5, 9, '2024-08-25', 'Pending',   'ECG annual'),
            ]
            cursor.executemany("""
                INSERT INTO tests_assigned
                    (PatID, TestID, AssignDate, Status, Notes)
                VALUES (%s,%s,%s,%s,%s)
            """, assigned_tests)

        # ── Seed doctor_catalog ──────────────────────────────────────────────

        cursor.execute("SELECT COUNT(*) FROM doctor_catalog")
        if cursor.fetchone()[0] == 0:
            doctors = [
                ('Dr. Ananya Krishnaswamy', 'Haematologist',
                 18, 'MBBS, MD (Haematology)', '9811000001'),
                ('Dr. Suresh Iyer',         'General Physician',
                 25, 'MBBS, MD (General Medicine)', '9811000002'),
                ('Dr. Meenakshi Raghunathan','Cardiologist',
                 15, 'MBBS, DM (Cardiology)', '9811000003'),
                ('Dr. Prakash Venkataraman','Endocrinologist',
                 12, 'MBBS, MD, DM (Endocrinology)', '9811000004'),
                ('Dr. Kavitha Sundaram',    'Nephrologist',
                 20, 'MBBS, MD, DM (Nephrology)', '9811000005'),
                ('Dr. Rajesh Bhattacharya','Pulmonologist',
                 22, 'MBBS, MD (Respiratory Medicine)', '9811000006'),
            ]
            cursor.executemany("""
                INSERT INTO doctor_catalog
                    (DoctorName, Speciality, YearsExperience,
                     Qualification, ContactNumber)
                VALUES (%s,%s,%s,%s,%s)
            """, doctors)

        # ── Seed patient_doctor_assignment ───────────────────────────────────

        cursor.execute("SELECT COUNT(*) FROM patient_doctor_assignment")
        if cursor.fetchone()[0] == 0:
            doc_assignments = [
                # Arjun Sharma
                (1, 1, '2024-01-10', 'Primary haematologist'),
                (1, 2, '2024-04-15', 'General physician for follow-up'),
                # Priya Mehta
                (2, 4, '2024-02-05', 'Endocrinologist for thyroid'),
                (2, 2, '2024-05-10', 'GP for general health'),
                # Ravi Krishnamurthy
                (3, 1, '2024-01-20', 'Haematologist for anaemia'),
                (3, 5, '2024-06-10', 'Nephrologist for kidney monitoring'),
                # Sneha Patel
                (4, 2, '2024-03-08', 'General physician'),
                (4, 4, '2024-09-22', 'Nutrition and endocrinology'),
                # Vikram Nair
                (5, 3, '2023-12-01', 'Cardiologist - cardiac care'),
                (5, 6, '2024-05-30', 'Pulmonologist - respiratory'),
            ]
            cursor.executemany("""
                INSERT INTO patient_doctor_assignment
                    (PatID, DoctorID, AssignDate, Notes)
                VALUES (%s,%s,%s,%s)
            """, doc_assignments)

        cursor.close()
        conn.close()
        print("[MEDORA] Database setup complete.")
        return True

    except Error as e:
        print(f"[MEDORA] Database setup failed: {e}", file=sys.stderr)
        return False
