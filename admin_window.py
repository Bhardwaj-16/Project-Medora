# admin_window.py - Administrator Workspace & SQL Terminal for Project MEDORA (Windows XP Style)

import os
import sys
import subprocess
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QStatusBar, QAction, QMenuBar, QMessageBox,
    QSizePolicy, QScrollArea, QToolBar, QToolButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QDateEdit, QTextEdit,
    QSplitter, QFileDialog, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QFont, QColor, QBrush

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

from db_setup import get_connection, _hash
from styles import (
    XP_STYLE, SIDEBAR_STYLE, SIDEBAR_HEADER_STYLE,
    NAV_BUTTON_STYLE, LOGOUT_BUTTON_STYLE, SUBHEADER_STYLE,
    SECTION_HEADER_STYLE, TOOLBAR_STYLE, BLUE_BUTTON_STYLE
)
from xp_icons import (
    icon_dashboard, icon_blood, icon_doctor, icon_tests,
    icon_profile, icon_logout, icon_graph, icon_refresh,
    icon_folder, icon_document, icon_medora, icon_console,
    icon_database, icon_admin, icon_users, icon_add,
    icon_edit, icon_delete, icon_save
)
from blood_results import PARAM_META, PARAMS, NORMAL_RANGES, BloodEntryDialog


# ─────────────────────────────────────────────────────────────────────────────
#  Dialogs for Admin CRUD
# ─────────────────────────────────────────────────────────────────────────────

class PatientEditDialog(QDialog):
    """Admin dialog to add a new patient or edit an existing patient."""

    def __init__(self, parent=None, existing: dict = None):
        super().__init__(parent)
        self.existing = existing
        self.pat_id = existing.get('PatID') if existing else None

        title = f"Admin - Edit Patient (ID: PAT-{self.pat_id:04d})" if existing else "Admin - Add New Patient"
        self.setWindowTitle(title)
        self.setFixedSize(520, 620)
        self.setStyleSheet(XP_STYLE)
        self._build_ui()
        if existing:
            self._populate(existing)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Patient Details Form")
        hdr.setFixedHeight(34)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        form_w = QWidget()
        form_w.setStyleSheet("background: #ECE9D8;")
        fl = QFormLayout(form_w)
        fl.setSpacing(8)
        fl.setContentsMargins(20, 16, 20, 10)
        fl.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.f_name    = QLineEdit()
        self.f_mobile  = QLineEdit()
        self.f_address = QLineEdit()
        self.f_age     = QSpinBox()
        self.f_age.setRange(0, 130)
        self.f_age.setValue(30)
        self.f_dob     = QDateEdit()
        self.f_dob.setCalendarPopup(True)
        self.f_dob.setDisplayFormat("yyyy-MM-dd")
        self.f_dob.setDate(QDate(1990, 1, 1))
        self.f_weight  = QDoubleSpinBox()
        self.f_weight.setRange(0.0, 300.0)
        self.f_weight.setDecimals(1)
        self.f_weight.setValue(70.0)
        self.f_loginid = QLineEdit()
        self.f_pass    = QLineEdit()
        self.f_pass.setPlaceholderText("Leave blank to keep existing password" if self.existing else "Required")

        fl.addRow("Full Name *:", self.f_name)
        fl.addRow("Mobile Number:", self.f_mobile)
        fl.addRow("Residential Address:", self.f_address)
        fl.addRow("Age (years):", self.f_age)
        fl.addRow("Date of Birth:", self.f_dob)
        fl.addRow("Weight (kg):", self.f_weight)
        fl.addRow("Portal Login ID *:", self.f_loginid)
        fl.addRow("Password:", self.f_pass)

        layout.addWidget(form_w)

        # Buttons
        btn_bar = QWidget()
        btn_bar.setFixedHeight(44)
        btn_bar.setStyleSheet(TOOLBAR_STYLE)
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(10, 6, 10, 6)
        bl.addStretch()

        btn_save = QPushButton(" Save Patient ")
        btn_save.setIcon(icon_save())
        btn_save.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)

        btn_cancel = QPushButton(" Cancel ")
        btn_cancel.setIcon(icon_delete())
        btn_cancel.clicked.connect(self.reject)

        bl.addWidget(btn_save)
        bl.addWidget(btn_cancel)
        layout.addWidget(btn_bar)

    def _populate(self, data: dict):
        self.f_name.setText(data.get('PatName') or "")
        self.f_mobile.setText(data.get('MobileNumber') or "")
        self.f_address.setText(data.get('Address') or "")
        if data.get('Age'):
            self.f_age.setValue(int(data['Age']))
        if data.get('DOB'):
            d = data['DOB']
            if isinstance(d, str):
                d = datetime.strptime(d, '%Y-%m-%d').date()
            self.f_dob.setDate(QDate(d.year, d.month, d.day))
        if data.get('Weight'):
            self.f_weight.setValue(float(data['Weight']))
        self.f_loginid.setText(data.get('LoginID') or "")

    def _on_save(self):
        name     = self.f_name.text().strip()
        login_id = self.f_loginid.text().strip()
        pwd      = self.f_pass.text()

        if not name or not login_id:
            QMessageBox.warning(self, "Validation", "Patient Name and Login ID are required.")
            return

        if not self.existing and not pwd:
            QMessageBox.warning(self, "Validation", "Password is required for new patient.")
            return

        q_dob = self.f_dob.date()
        dob_str = f"{q_dob.year():04d}-{q_dob.month():02d}-{q_dob.day():02d}"

        try:
            conn = get_connection()
            cur = conn.cursor()
            if self.pat_id:
                if pwd:
                    cur.execute("""
                        UPDATE patient_details SET
                            PatName=%s, MobileNumber=%s, Address=%s, Age=%s,
                            DOB=%s, Weight=%s, LoginID=%s, Password=%s
                        WHERE PatID=%s
                    """, (
                        name, self.f_mobile.text().strip(), self.f_address.text().strip(),
                        self.f_age.value(), dob_str, self.f_weight.value(),
                        login_id, _hash(pwd), self.pat_id
                    ))
                else:
                    cur.execute("""
                        UPDATE patient_details SET
                            PatName=%s, MobileNumber=%s, Address=%s, Age=%s,
                            DOB=%s, Weight=%s, LoginID=%s
                        WHERE PatID=%s
                    """, (
                        name, self.f_mobile.text().strip(), self.f_address.text().strip(),
                        self.f_age.value(), dob_str, self.f_weight.value(),
                        login_id, self.pat_id
                    ))
            else:
                cur.execute("""
                    INSERT INTO patient_details
                        (PatName, MobileNumber, Address, Age, DOB, Weight, LoginID, Password)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    name, self.f_mobile.text().strip(), self.f_address.text().strip(),
                    self.f_age.value(), dob_str, self.f_weight.value(),
                    login_id, _hash(pwd)
                ))
            conn.commit()
            cur.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save patient:\n\n{e}")


class DoctorEditDialog(QDialog):
    """Admin dialog to add or edit a doctor."""

    def __init__(self, parent=None, existing: dict = None):
        super().__init__(parent)
        self.existing = existing
        self.doc_id = existing.get('DoctorID') if existing else None

        title = f"Admin - Edit Doctor #{self.doc_id}" if existing else "Admin - Add New Doctor"
        self.setWindowTitle(title)
        self.setFixedSize(500, 360)
        self.setStyleSheet(XP_STYLE)
        self._build_ui()
        if existing:
            self._populate(existing)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Doctor Profile Details")
        hdr.setFixedHeight(34)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        form_w = QWidget()
        form_w.setStyleSheet("background: #ECE9D8;")
        fl = QFormLayout(form_w)
        fl.setSpacing(8)
        fl.setContentsMargins(20, 16, 20, 10)
        fl.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.f_name   = QLineEdit()
        self.f_spec   = QLineEdit()
        self.f_exp    = QSpinBox()
        self.f_exp.setRange(0, 70)
        self.f_exp.setValue(10)
        self.f_qual   = QLineEdit()
        self.f_phone  = QLineEdit()

        fl.addRow("Doctor Name *:", self.f_name)
        fl.addRow("Speciality *:", self.f_spec)
        fl.addRow("Experience (years):", self.f_exp)
        fl.addRow("Qualifications:", self.f_qual)
        fl.addRow("Contact Phone:", self.f_phone)

        layout.addWidget(form_w)

        btn_bar = QWidget()
        btn_bar.setFixedHeight(44)
        btn_bar.setStyleSheet(TOOLBAR_STYLE)
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(10, 6, 10, 6)
        bl.addStretch()

        btn_save = QPushButton(" Save Doctor ")
        btn_save.setIcon(icon_save())
        btn_save.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)

        btn_cancel = QPushButton(" Cancel ")
        btn_cancel.setIcon(icon_delete())
        btn_cancel.clicked.connect(self.reject)

        bl.addWidget(btn_save)
        bl.addWidget(btn_cancel)
        layout.addWidget(btn_bar)

    def _populate(self, data: dict):
        self.f_name.setText(data.get('DoctorName') or "")
        self.f_spec.setText(data.get('Speciality') or "")
        if data.get('YearsExperience'):
            self.f_exp.setValue(int(data['YearsExperience']))
        self.f_qual.setText(data.get('Qualification') or "")
        self.f_phone.setText(data.get('ContactNumber') or "")

    def _on_save(self):
        name = self.f_name.text().strip()
        spec = self.f_spec.text().strip()
        if not name or not spec:
            QMessageBox.warning(self, "Validation", "Doctor Name and Speciality are required.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            if self.doc_id:
                cur.execute("""
                    UPDATE doctor_catalog SET
                        DoctorName=%s, Speciality=%s, YearsExperience=%s,
                        Qualification=%s, ContactNumber=%s
                    WHERE DoctorID=%s
                """, (name, spec, self.f_exp.value(), self.f_qual.text().strip(), self.f_phone.text().strip(), self.doc_id))
            else:
                cur.execute("""
                    INSERT INTO doctor_catalog
                        (DoctorName, Speciality, YearsExperience, Qualification, ContactNumber)
                    VALUES (%s,%s,%s,%s,%s)
                """, (name, spec, self.f_exp.value(), self.f_qual.text().strip(), self.f_phone.text().strip()))
            conn.commit()
            cur.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save doctor:\n\n{e}")


class TestEditDialog(QDialog):
    """Admin dialog to add or edit a test catalog item."""

    def __init__(self, parent=None, existing: dict = None):
        super().__init__(parent)
        self.existing = existing
        self.test_id = existing.get('TestID') if existing else None

        title = f"Admin - Edit Test #{self.test_id}" if existing else "Admin - Add New Test to Catalog"
        self.setWindowTitle(title)
        self.setFixedSize(500, 360)
        self.setStyleSheet(XP_STYLE)
        self._build_ui()
        if existing:
            self._populate(existing)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Test Catalog Entry")
        hdr.setFixedHeight(34)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        form_w = QWidget()
        form_w.setStyleSheet("background: #ECE9D8;")
        fl = QFormLayout(form_w)
        fl.setSpacing(8)
        fl.setContentsMargins(20, 16, 20, 10)
        fl.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.f_name  = QLineEdit()
        self.f_cat   = QLineEdit()
        self.f_price = QDoubleSpinBox()
        self.f_price.setRange(0.0, 99999.0)
        self.f_price.setValue(500.0)
        self.f_desc  = QLineEdit()

        fl.addRow("Test Name *:", self.f_name)
        fl.addRow("Category / Dept *:", self.f_cat)
        fl.addRow("Standard Tariff (INR):", self.f_price)
        fl.addRow("Description:", self.f_desc)

        layout.addWidget(form_w)

        btn_bar = QWidget()
        btn_bar.setFixedHeight(44)
        btn_bar.setStyleSheet(TOOLBAR_STYLE)
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(10, 6, 10, 6)
        bl.addStretch()

        btn_save = QPushButton(" Save Test ")
        btn_save.setIcon(icon_save())
        btn_save.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)

        btn_cancel = QPushButton(" Cancel ")
        btn_cancel.setIcon(icon_delete())
        btn_cancel.clicked.connect(self.reject)

        bl.addWidget(btn_save)
        bl.addWidget(btn_cancel)
        layout.addWidget(btn_bar)

    def _populate(self, data: dict):
        self.f_name.setText(data.get('TestName') or "")
        self.f_cat.setText(data.get('Category') or "")
        if data.get('Price') is not None:
            self.f_price.setValue(float(data['Price']))
        self.f_desc.setText(data.get('Description') or "")

    def _on_save(self):
        name = self.f_name.text().strip()
        cat  = self.f_cat.text().strip()
        if not name or not cat:
            QMessageBox.warning(self, "Validation", "Test Name and Category are required.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            if self.test_id:
                cur.execute("""
                    UPDATE tests_catalog SET
                        TestName=%s, Category=%s, Price=%s, Description=%s
                    WHERE TestID=%s
                """, (name, cat, self.f_price.value(), self.f_desc.text().strip(), self.test_id))
            else:
                cur.execute("""
                    INSERT INTO tests_catalog
                        (TestName, Category, Price, Description)
                    VALUES (%s,%s,%s,%s)
                """, (name, cat, self.f_price.value(), self.f_desc.text().strip()))
            conn.commit()
            cur.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save test:\n\n{e}")


class AssignDoctorDialog(QDialog):
    """Admin dialog to assign a doctor to a patient."""

    def __init__(self, parent=None, default_pat_id=None):
        super().__init__(parent)
        self.setWindowTitle("Admin - Assign Doctor to Patient")
        self.setFixedSize(480, 280)
        self.setStyleSheet(XP_STYLE)
        self._default_pat_id = default_pat_id
        self._build_ui()
        self._load_combos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Assign Doctor Referral")
        hdr.setFixedHeight(34)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        form_w = QWidget()
        form_w.setStyleSheet("background: #ECE9D8;")
        fl = QFormLayout(form_w)
        fl.setSpacing(8)
        fl.setContentsMargins(20, 16, 20, 10)

        self.cb_patient = QComboBox()
        self.cb_doctor  = QComboBox()
        self.f_date     = QDateEdit()
        self.f_date.setCalendarPopup(True)
        self.f_date.setDate(QDate.currentDate())
        self.f_notes    = QLineEdit()
        self.f_notes.setPlaceholderText("Optional referral / consultation notes")

        fl.addRow("Select Patient *:", self.cb_patient)
        fl.addRow("Select Doctor *:",  self.cb_doctor)
        fl.addRow("Assignment Date:",  self.f_date)
        fl.addRow("Clinical Notes:",   self.f_notes)

        layout.addWidget(form_w)

        btn_bar = QWidget()
        btn_bar.setFixedHeight(44)
        btn_bar.setStyleSheet(TOOLBAR_STYLE)
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(10, 6, 10, 6)
        bl.addStretch()

        btn_save = QPushButton(" Assign Doctor ")
        btn_save.setIcon(icon_doctor())
        btn_save.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_save.clicked.connect(self._on_save)

        btn_cancel = QPushButton(" Cancel ")
        btn_cancel.clicked.connect(self.reject)

        bl.addWidget(btn_save)
        bl.addWidget(btn_cancel)
        layout.addWidget(btn_bar)

    def _load_combos(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT PatID, PatName FROM patient_details ORDER BY PatName")
        patients = cur.fetchall()
        for p in patients:
            self.cb_patient.addItem(f"{p['PatName']} (PAT-{p['PatID']:04d})", p['PatID'])
            if self._default_pat_id == p['PatID']:
                self.cb_patient.setCurrentIndex(self.cb_patient.count() - 1)

        cur.execute("SELECT DoctorID, DoctorName, Speciality FROM doctor_catalog ORDER BY DoctorName")
        docs = cur.fetchall()
        for d in docs:
            self.cb_doctor.addItem(f"{d['DoctorName']} - {d['Speciality']}", d['DoctorID'])

        cur.close()
        conn.close()

    def _on_save(self):
        pat_id = self.cb_patient.currentData()
        doc_id = self.cb_doctor.currentData()
        if not pat_id or not doc_id:
            QMessageBox.warning(self, "Validation", "Please select both a patient and a doctor.")
            return

        q_d = self.f_date.date()
        date_str = f"{q_d.year():04d}-{q_d.month():02d}-{q_d.day():02d}"

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO patient_doctor_assignment (PatID, DoctorID, AssignDate, Notes)
                VALUES (%s, %s, %s, %s)
            """, (pat_id, doc_id, date_str, self.f_notes.text().strip()))
            conn.commit()
            cur.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Assignment failed:\n\n{e}")


class AssignTestDialog(QDialog):
    """Admin dialog to prescribe/assign a test to a patient."""

    def __init__(self, parent=None, default_pat_id=None):
        super().__init__(parent)
        self.setWindowTitle("Admin - Order Test for Patient")
        self.setFixedSize(500, 310)
        self.setStyleSheet(XP_STYLE)
        self._default_pat_id = default_pat_id
        self._build_ui()
        self._load_combos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Order Clinical Diagnostic Test")
        hdr.setFixedHeight(34)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        form_w = QWidget()
        form_w.setStyleSheet("background: #ECE9D8;")
        fl = QFormLayout(form_w)
        fl.setSpacing(8)
        fl.setContentsMargins(20, 16, 20, 10)

        self.cb_patient = QComboBox()
        self.cb_test    = QComboBox()
        self.f_date     = QDateEdit()
        self.f_date.setCalendarPopup(True)
        self.f_date.setDate(QDate.currentDate())
        self.cb_status  = QComboBox()
        self.cb_status.addItems(["Pending", "Completed", "Cancelled"])
        self.f_notes    = QLineEdit()
        self.f_notes.setPlaceholderText("Optional test instructions / fasting note")

        fl.addRow("Select Patient *:", self.cb_patient)
        fl.addRow("Select Test *:",    self.cb_test)
        fl.addRow("Order Date:",       self.f_date)
        fl.addRow("Initial Status:",   self.cb_status)
        fl.addRow("Order Notes:",      self.f_notes)

        layout.addWidget(form_w)

        btn_bar = QWidget()
        btn_bar.setFixedHeight(44)
        btn_bar.setStyleSheet(TOOLBAR_STYLE)
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(10, 6, 10, 6)
        bl.addStretch()

        btn_save = QPushButton(" Assign Test ")
        btn_save.setIcon(icon_tests())
        btn_save.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_save.clicked.connect(self._on_save)

        btn_cancel = QPushButton(" Cancel ")
        btn_cancel.clicked.connect(self.reject)

        bl.addWidget(btn_save)
        bl.addWidget(btn_cancel)
        layout.addWidget(btn_bar)

    def _load_combos(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT PatID, PatName FROM patient_details ORDER BY PatName")
        patients = cur.fetchall()
        for p in patients:
            self.cb_patient.addItem(f"{p['PatName']} (PAT-{p['PatID']:04d})", p['PatID'])
            if self._default_pat_id == p['PatID']:
                self.cb_patient.setCurrentIndex(self.cb_patient.count() - 1)

        cur.execute("SELECT TestID, TestName, Category, Price FROM tests_catalog ORDER BY Category, TestName")
        tests = cur.fetchall()
        for t in tests:
            self.cb_test.addItem(f"[{t['Category']}] {t['TestName']} (INR {t['Price']:.0f})", t['TestID'])

        cur.close()
        conn.close()

    def _on_save(self):
        pat_id  = self.cb_patient.currentData()
        test_id = self.cb_test.currentData()
        if not pat_id or not test_id:
            QMessageBox.warning(self, "Validation", "Please select both a patient and a test.")
            return

        q_d = self.f_date.date()
        date_str = f"{q_d.year():04d}-{q_d.month():02d}-{q_d.day():02d}"

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO tests_assigned (PatID, TestID, AssignDate, Status, Notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (pat_id, test_id, date_str, self.cb_status.currentText(), self.f_notes.text().strip()))
            conn.commit()
            cur.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Test assignment failed:\n\n{e}")


# ─────────────────────────────────────────────────────────────────────────────
#  SQL Console / Terminal Component
# ─────────────────────────────────────────────────────────────────────────────

class SQLConsoleWidget(QWidget):
    """
    Built-in Windows XP Administrative Command Prompt & SQL Shell.
    Allows executing ANY custom SQL query (SELECT, INSERT, UPDATE, DELETE,
    CREATE, DROP, ALTER, SHOW, DESCRIBE) directly on MySQL with real-time grid
    and text console output.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        hdr = QLabel("  SQL Administration Console & Terminal  [C:\\MEDORA\\ADMIN\\SQL>_]")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        # Quick SQL Snippets Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(36)
        toolbar.setStyleSheet(TOOLBAR_STYLE)
        tb_l = QHBoxLayout(toolbar)
        tb_l.setContentsMargins(6, 3, 6, 3)
        tb_l.setSpacing(4)

        tb_l.addWidget(QLabel("Quick Queries:"))
        templates = [
            ("Patients", "SELECT PatID, PatName, MobileNumber, Age, LoginID FROM patient_details;"),
            ("Blood Results", "SELECT * FROM blood_test_results ORDER BY TestDate DESC LIMIT 25;"),
            ("Doctors", "SELECT * FROM doctor_catalog;"),
            ("Tests", "SELECT * FROM tests_catalog;"),
            ("Orders", "SELECT * FROM tests_assigned ORDER BY AssignDate DESC;"),
            ("Show Tables", "SHOW TABLES;"),
        ]
        for name, sql in templates:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background: #FFFFFF;
                    border: 1px solid #7F9DB9;
                    font-size: 8pt;
                    padding: 2px 6px;
                }
                QPushButton:hover { background: #EEF4FF; border-color: #316AC5; }
            """)
            btn.clicked.connect(lambda ch, s=sql: self._set_query(s))
            tb_l.addWidget(btn)

        tb_l.addStretch()

        btn_term = QPushButton(" Launch OS Terminal ")
        btn_term.setIcon(icon_console())
        btn_term.setToolTip("Open external macOS Terminal.app")
        btn_term.clicked.connect(self._open_os_terminal)
        tb_l.addWidget(btn_term)

        layout.addWidget(toolbar)

        # Splitter: Top SQL editor, Bottom Results (Grid + Console Output)
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(5)

        # ── Upper Editor Area ────────────────────────────────────────────────
        editor_frame = QWidget()
        editor_frame.setStyleSheet("background: #ECE9D8;")
        ef_l = QVBoxLayout(editor_frame)
        ef_l.setContentsMargins(6, 6, 6, 4)
        ef_l.setSpacing(4)

        ed_hdr = QLabel("  Enter SQL Query  (Press Ctrl+Enter or click 'Execute Query' to run)")
        ed_hdr.setFixedHeight(22)
        ed_hdr.setStyleSheet(SUBHEADER_STYLE)
        ef_l.addWidget(ed_hdr)

        self.sql_editor = QTextEdit()
        self.sql_editor.setFont(QFont("Consolas", 10))
        self.sql_editor.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF66;
                border: 2px inset #707070;
                font-family: Consolas, "Courier New", monospace;
                font-size: 10pt;
                padding: 4px;
            }
        """)
        self.sql_editor.setText("SELECT * FROM patient_details;\n")
        ef_l.addWidget(self.sql_editor)

        # Editor action bar
        e_bar = QHBoxLayout()
        e_bar.setSpacing(6)

        self.btn_exec = QPushButton(" Execute Query (Ctrl+Enter) ")
        self.btn_exec.setIcon(icon_console())
        self.btn_exec.setStyleSheet(BLUE_BUTTON_STYLE)
        self.btn_exec.clicked.connect(self.execute_query)
        e_bar.addWidget(self.btn_exec)

        btn_clear = QPushButton(" Clear Editor ")
        btn_clear.clicked.connect(self.sql_editor.clear)
        e_bar.addWidget(btn_clear)

        btn_csv = QPushButton(" Export Result (CSV) ")
        btn_csv.clicked.connect(self._export_csv)
        e_bar.addWidget(btn_csv)

        e_bar.addStretch()
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet("color: #333333; font-size: 8.5pt;")
        e_bar.addWidget(self.status_lbl)
        ef_l.addLayout(e_bar)

        splitter.addWidget(editor_frame)

        # ── Lower Output Area (Tabbed: Grid View & Terminal Output) ───────────
        output_frame = QWidget()
        output_frame.setStyleSheet("background: #ECE9D8;")
        of_l = QVBoxLayout(output_frame)
        of_l.setContentsMargins(6, 4, 6, 6)
        of_l.setSpacing(4)

        res_hdr = QLabel("  Execution Output & Results Grid")
        res_hdr.setFixedHeight(22)
        res_hdr.setStyleSheet(SUBHEADER_STYLE)
        of_l.addWidget(res_hdr)

        res_splitter = QSplitter(Qt.Horizontal)
        res_splitter.setHandleWidth(4)

        # Grid view
        self.result_table = QTableWidget()
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setStyleSheet("""
            QTableWidget {
                background: #FFFFFF;
                color: #000000;
                gridline-color: #D0D0D0;
                border: 1px solid #7F9DB9;
            }
        """)
        res_splitter.addWidget(self.result_table)

        # Terminal text log
        self.term_log = QTextEdit()
        self.term_log.setReadOnly(True)
        self.term_log.setFont(QFont("Consolas", 9))
        self.term_log.setStyleSheet("""
            QTextEdit {
                background-color: #0C0C0C;
                color: #E0E0E0;
                border: 1px solid #707070;
                font-family: Consolas, "Courier New", monospace;
                font-size: 9pt;
            }
        """)
        self.term_log.setText(
            "Microsoft Windows XP [Version 5.1.2600]\n"
            "Project MEDORA Administrative Command Shell (MySQL 8.0)\n"
            "Database: medora_db | Host: localhost:3306\n"
            "Type SQL commands and press [Execute Query] to inspect or modify data.\n\n"
        )
        res_splitter.addWidget(self.term_log)
        res_splitter.setSizes([550, 350])

        of_l.addWidget(res_splitter)
        splitter.addWidget(output_frame)
        splitter.setSizes([200, 360])

        layout.addWidget(splitter)

    def _set_query(self, sql: str):
        self.sql_editor.setText(sql)
        self.execute_query()

    def execute_query(self):
        sql = self.sql_editor.toPlainText().strip()
        if not sql:
            return

        t0 = time.time()
        self.status_lbl.setText("Executing query...")
        self.btn_exec.setEnabled(False)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Execute multiple statements if separated by semicolon
            stmts = [s.strip() for s in sql.split(';') if s.strip()]
            last_rows = None
            last_headers = None

            for s in stmts:
                cursor.execute(s)
                if cursor.description:
                    last_headers = [col[0] for col in cursor.description]
                    last_rows = cursor.fetchall()

            conn.commit()
            elapsed = time.time() - t0

            if last_headers is not None:
                # SELECT / SHOW / DESCRIBE
                self._populate_grid(last_headers, last_rows)
                msg = f"\nSQL> {sql}\nQuery OK: {len(last_rows)} row(s) returned ({elapsed:.3f} sec)\n"
                self.term_log.append(msg)
                self.status_lbl.setText(f"Query OK: {len(last_rows)} row(s) ({elapsed:.3f} s)")
            else:
                # INSERT / UPDATE / DELETE / DDL
                affected = cursor.rowcount
                self.result_table.clear()
                self.result_table.setRowCount(0)
                self.result_table.setColumnCount(0)
                msg = f"\nSQL> {sql}\nQuery OK, {affected} row(s) affected ({elapsed:.3f} sec)\n"
                self.term_log.append(msg)
                self.status_lbl.setText(f"Query OK: {affected} row(s) affected ({elapsed:.3f} s)")

            cursor.close()
            conn.close()

        except Exception as e:
            elapsed = time.time() - t0
            err_msg = f"\nSQL> {sql}\nERROR: {e} ({elapsed:.3f} sec)\n"
            self.term_log.append(err_msg)
            self.status_lbl.setText(f"Error: {e}")
            QMessageBox.critical(self, "SQL Execution Error", f"MySQL Error:\n\n{e}")

        finally:
            self.btn_exec.setEnabled(True)

    def _populate_grid(self, headers, rows):
        self.result_table.clear()
        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)
        self.result_table.setRowCount(len(rows))

        BLACK  = QColor('#000000')
        WHITE  = QColor('#FFFFFF')
        ALT_BG = QColor('#F1F6FC')

        for r_idx, row in enumerate(rows):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE
            for c_idx, val in enumerate(row):
                itm = QTableWidgetItem(str(val) if val is not None else "NULL")
                itm.setForeground(QBrush(BLACK))
                itm.setBackground(QBrush(bg))
                itm.setToolTip(f"Column: {headers[c_idx]}\nValue: {val}")
                self.result_table.setItem(r_idx, c_idx, itm)
            self.result_table.setRowHeight(r_idx, 22)

        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def _export_csv(self):
        if self.result_table.rowCount() == 0:
            QMessageBox.information(self, "Export", "No query results to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save SQL Result to CSV", "query_result.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = [self.result_table.horizontalHeaderItem(c).text() for c in range(self.result_table.columnCount())]
                writer.writerow(headers)
                for r in range(self.result_table.rowCount()):
                    row_data = [self.result_table.item(r, c).text() if self.result_table.item(r, c) else "" for c in range(self.result_table.columnCount())]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export Successful", f"Results exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{e}")

    def _open_os_terminal(self):
        """Open system terminal on macOS."""
        try:
            medora_dir = os.path.dirname(os.path.abspath(__file__))
            script = f'tell application "Terminal" to do script "cd {medora_dir} && clear"'
            subprocess.Popen(['osascript', '-e', script])
        except Exception as e:
            QMessageBox.information(self, "Terminal Launch", f"Could not launch Terminal.app: {e}")


# ─────────────────────────────────────────────────────────────────────────────
#  Main Administrator Window
# ─────────────────────────────────────────────────────────────────────────────

class AdminMainWindow(QMainWindow):
    """
    Complete Windows XP Administrator Suite for Project MEDORA.
    Provides total DDL/DML power: Add/Edit/Delete Patients, Doctors, Tests,
    Blood Test Counts, Orders, and embedded SQL Command Shell.
    """

    PAGE_PATIENTS = 0
    PAGE_BLOOD    = 1
    PAGE_DOCTORS  = 2
    PAGE_TESTS    = 3
    PAGE_ORDERS   = 4
    PAGE_CONSOLE  = 5

    def __init__(self, admin_data: dict, login_window, parent=None):
        super().__init__(parent)
        self.admin_data   = admin_data
        self.login_window = login_window
        self.username     = admin_data.get('Username', 'admin')
        self._login_time  = datetime.now().strftime('%d-%b-%Y %H:%M')

        self.setWindowTitle(
            f"MEDORA - System Administration Console - [{self.username.upper()} / SUPERADMIN]"
        )
        self.setWindowIcon(icon_admin())
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(XP_STYLE)

        self._build_menubar()
        self._build_toolbar()
        self._build_ui()
        self._build_statusbar()
        self._navigate(self.PAGE_PATIENTS)

    # ── Menu Bar ─────────────────────────────────────────────────────────────

    def _build_menubar(self):
        mb = self.menuBar()

        # File
        fm = mb.addMenu("&File")
        act_logout = QAction(icon_logout(), "&Log Off Admin", self)
        act_logout.setShortcut("Ctrl+L")
        act_logout.triggered.connect(self._on_logout)
        act_exit = QAction("E&xit", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        fm.addAction(act_logout)
        fm.addSeparator()
        fm.addAction(act_exit)

        # Edit (Quick Creates)
        em = mb.addMenu("&Edit")
        act_add_p = QAction(icon_users(), "Add New Patient...", self)
        act_add_p.triggered.connect(self._on_add_patient)
        act_add_d = QAction(icon_doctor(), "Add New Doctor...", self)
        act_add_d.triggered.connect(self._on_add_doctor)
        act_add_t = QAction(icon_tests(), "Add New Test to Catalog...", self)
        act_add_t.triggered.connect(self._on_add_test)
        act_add_b = QAction(icon_blood(), "Record Patient Blood Counts...", self)
        act_add_b.triggered.connect(self._on_add_blood)
        em.addAction(act_add_p)
        em.addAction(act_add_d)
        em.addAction(act_add_t)
        em.addAction(act_add_b)

        # View
        vm = mb.addMenu("&View")
        views = [
            ("Patients Manager", icon_users(), self.PAGE_PATIENTS),
            ("Blood Tests Log & Charts", icon_blood(), self.PAGE_BLOOD),
            ("Doctors Catalog", icon_doctor(), self.PAGE_DOCTORS),
            ("Tests Available Catalog", icon_tests(), self.PAGE_TESTS),
            ("Test Orders & Workflow", icon_document(), self.PAGE_ORDERS),
            ("SQL Command Console", icon_console(), self.PAGE_CONSOLE),
        ]
        for name, ico, idx in views:
            act = QAction(ico, name, self)
            act.triggered.connect(lambda ch, i=idx: self._navigate(i))
            vm.addAction(act)

        # Tools
        tm = mb.addMenu("&Tools")
        act_cons = QAction(icon_console(), "Open SQL Console (F12)", self)
        act_cons.setShortcut("F12")
        act_cons.triggered.connect(lambda: self._navigate(self.PAGE_CONSOLE))
        act_ref = QAction(icon_refresh(), "Refresh All Tables (F5)", self)
        act_ref.setShortcut("F5")
        act_ref.triggered.connect(self._refresh_all)
        tm.addAction(act_cons)
        tm.addAction(act_ref)

        # Help
        hm = mb.addMenu("&Help")
        act_about = QAction(icon_admin(), "About MEDORA Administrator", self)
        act_about.triggered.connect(self._show_about)
        hm.addAction(act_about)

    # ── Toolbar ──────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        tb = QToolBar("Admin Suite Operations", self)
        tb.setIconSize(QSize(16, 16))
        tb.setMovable(False)

        def _btn(txt, ico, fn):
            b = QToolButton(self)
            b.setText(txt)
            b.setIcon(ico)
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            b.clicked.connect(fn)
            tb.addWidget(b)
            return b

        _btn(" Patients", icon_users(), lambda: self._navigate(self.PAGE_PATIENTS))
        _btn(" Blood Records", icon_blood(), lambda: self._navigate(self.PAGE_BLOOD))
        _btn(" Doctors", icon_doctor(), lambda: self._navigate(self.PAGE_DOCTORS))
        _btn(" Tests Catalog", icon_tests(), lambda: self._navigate(self.PAGE_TESTS))
        _btn(" Orders", icon_document(), lambda: self._navigate(self.PAGE_ORDERS))
        _btn(" SQL Console", icon_console(), lambda: self._navigate(self.PAGE_CONSOLE))
        tb.addSeparator()
        _btn(" Refresh (F5)", icon_refresh(), self._refresh_all)
        tb.addSeparator()
        _btn(" Log Off", icon_logout(), self._on_logout)

        self.addToolBar(tb)

    # ── Main UI Layout ───────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sb_l = QVBoxLayout(sidebar)
        sb_l.setSpacing(0)
        sb_l.setContentsMargins(0, 0, 0, 0)

        # Admin Header
        admin_hdr = QLabel(f" ADMINISTRATOR\n User: {self.username.upper()} (SuperAdmin)")
        admin_hdr.setFixedHeight(54)
        admin_hdr.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        admin_hdr.setStyleSheet(SIDEBAR_HEADER_STYLE)
        sb_l.addWidget(admin_hdr)

        # Nav tasks
        t_lbl = QLabel("  Administration Tasks")
        t_lbl.setFixedHeight(24)
        t_lbl.setStyleSheet(SUBHEADER_STYLE)
        sb_l.addWidget(t_lbl)

        nav_items = [
            ("Patients Manager", icon_users(), self.PAGE_PATIENTS),
            ("Blood Tests Log", icon_blood(), self.PAGE_BLOOD),
            ("Doctors Catalog", icon_doctor(), self.PAGE_DOCTORS),
            ("Tests Available", icon_tests(), self.PAGE_TESTS),
            ("Test Orders", icon_document(), self.PAGE_ORDERS),
            ("SQL Terminal", icon_console(), self.PAGE_CONSOLE),
        ]
        self._nav_buttons = []
        for label, ico, p_idx in nav_items:
            btn = QPushButton(f"  {label}")
            btn.setIcon(ico)
            btn.setIconSize(QSize(16, 16))
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_BUTTON_STYLE)
            btn.setFixedHeight(34)
            btn.clicked.connect(lambda ch, i=p_idx: self._navigate(i))
            sb_l.addWidget(btn)
            self._nav_buttons.append(btn)

        sb_l.addSpacing(10)

        # Quick Actions Section
        q_lbl = QLabel("  Quick Database Actions")
        q_lbl.setFixedHeight(24)
        q_lbl.setStyleSheet(SUBHEADER_STYLE)
        sb_l.addWidget(q_lbl)

        quick_btns = [
            ("  [+] Add Patient", self._on_add_patient),
            ("  [+] Add Doctor", self._on_add_doctor),
            ("  [+] Add Test", self._on_add_test),
            ("  [+] Record Blood Counts", self._on_add_blood),
            ("  [>] Open SQL Shell", lambda: self._navigate(self.PAGE_CONSOLE)),
        ]
        for txt, fn in quick_btns:
            qb = QPushButton(txt)
            qb.setStyleSheet(NAV_BUTTON_STYLE)
            qb.setFixedHeight(28)
            qb.clicked.connect(fn)
            sb_l.addWidget(qb)

        sb_l.addStretch()

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #ACA899;")
        sb_l.addWidget(sep)

        btn_logout = QPushButton("  Log Off Admin")
        btn_logout.setIcon(icon_logout())
        btn_logout.setFixedHeight(32)
        btn_logout.setStyleSheet(LOGOUT_BUTTON_STYLE)
        btn_logout.clicked.connect(self._on_logout)
        sb_l.addWidget(btn_logout)
        sb_l.addSpacing(4)

        root.addWidget(sidebar)

        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.VLine)
        v_sep.setStyleSheet("color: #716F64;")
        root.addWidget(v_sep)

        # ── Stacked Content Area ─────────────────────────────────────────────
        self.stack = QStackedWidget()

        # Page 0: Patients
        self.page_patients = self._build_patients_page()
        self.stack.addWidget(self.page_patients)

        # Page 1: Blood Records
        self.page_blood = self._build_blood_page()
        self.stack.addWidget(self.page_blood)

        # Page 2: Doctors
        self.page_doctors = self._build_doctors_page()
        self.stack.addWidget(self.page_doctors)

        # Page 3: Tests Catalog
        self.page_tests = self._build_tests_page()
        self.stack.addWidget(self.page_tests)

        # Page 4: Orders
        self.page_orders = self._build_orders_page()
        self.stack.addWidget(self.page_orders)

        # Page 5: SQL Console
        self.console_widget = SQLConsoleWidget()
        self.stack.addWidget(self.console_widget)

        root.addWidget(self.stack)

    # ── Status Bar ───────────────────────────────────────────────────────────

    def _build_statusbar(self):
        sb = self.statusBar()
        sb.setSizeGripEnabled(True)

        self.sb_user   = QLabel(f" Admin: {self.username} (SuperAdmin)")
        self.sb_db     = QLabel(" Database: medora_db @ localhost:3306")
        self.sb_perms  = QLabel(" Permissions: Full DDL / DML / SQL Control")
        self.sb_status = QLabel(" Status: Ready")

        for lbl in (self.sb_user, self.sb_db, self.sb_perms, self.sb_status):
            lbl.setStyleSheet("""
                QLabel {
                    border-top: 1px solid #ACA899;
                    border-left: 1px solid #ACA899;
                    border-right: 1px solid #FFFFFF;
                    border-bottom: 1px solid #FFFFFF;
                    background-color: #ECE9D8;
                    color: #000000;
                    padding: 1px 6px;
                    font-size: 8.5pt;
                }
            """)

        sb.addWidget(self.sb_user, 2)
        sb.addWidget(self.sb_db, 2)
        sb.addWidget(self.sb_perms, 2)
        sb.addWidget(self.sb_status, 1)

    # ── Page Builders ────────────────────────────────────────────────────────

    def _build_patients_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Patient Records Management (Add, Edit, Delete, Assign)")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        tb = QFrame()
        tb.setFixedHeight(38)
        tb.setStyleSheet(TOOLBAR_STYLE)
        tb_l = QHBoxLayout(tb)
        tb_l.setContentsMargins(6, 4, 6, 4)
        tb_l.setSpacing(4)

        btn_add = QPushButton(" Add Patient")
        btn_add.setIcon(icon_add())
        btn_add.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_add.clicked.connect(self._on_add_patient)

        self.btn_edit_pat = QPushButton(" Edit Patient")
        self.btn_edit_pat.setIcon(icon_edit())
        self.btn_edit_pat.setEnabled(False)
        self.btn_edit_pat.clicked.connect(self._on_edit_patient)

        self.btn_del_pat = QPushButton(" Delete Patient")
        self.btn_del_pat.setIcon(icon_delete())
        self.btn_del_pat.setEnabled(False)
        self.btn_del_pat.clicked.connect(self._on_delete_patient)

        self.btn_asgn_doc = QPushButton(" Assign Doctor")
        self.btn_asgn_doc.setIcon(icon_doctor())
        self.btn_asgn_doc.setEnabled(False)
        self.btn_asgn_doc.clicked.connect(self._on_assign_doc_patient)

        self.btn_asgn_test = QPushButton(" Order Test")
        self.btn_asgn_test.setIcon(icon_tests())
        self.btn_asgn_test.setEnabled(False)
        self.btn_asgn_test.clicked.connect(self._on_assign_test_patient)

        btn_ref = QPushButton(" Refresh")
        btn_ref.setIcon(icon_refresh())
        btn_ref.clicked.connect(self._load_patients)

        tb_l.addWidget(btn_add)
        tb_l.addWidget(self.btn_edit_pat)
        tb_l.addWidget(self.btn_del_pat)
        tb_l.addSpacing(10)
        tb_l.addWidget(self.btn_asgn_doc)
        tb_l.addWidget(self.btn_asgn_test)
        tb_l.addStretch()
        tb_l.addWidget(btn_ref)
        layout.addWidget(tb)

        # Table
        p_frame = QWidget()
        p_frame.setStyleSheet("background: #ECE9D8;")
        pfl = QVBoxLayout(p_frame)
        pfl.setContentsMargins(8, 8, 8, 8)

        self.tbl_patients = QTableWidget()
        p_cols = ["PatID", "Patient Name", "Mobile Number", "Address", "Age", "DOB", "Weight (kg)", "Login ID"]
        self.tbl_patients.setColumnCount(len(p_cols))
        self.tbl_patients.setHorizontalHeaderLabels(p_cols)
        self.tbl_patients.setAlternatingRowColors(True)
        self.tbl_patients.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_patients.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_patients.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_patients.verticalHeader().setVisible(False)
        self.tbl_patients.setShowGrid(True)
        self.tbl_patients.itemSelectionChanged.connect(self._on_patient_selection)

        hh = self.tbl_patients.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        pfl.addWidget(self.tbl_patients)
        layout.addWidget(p_frame)
        return w

    def _build_blood_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Blood Test Records & Visual Progression (All Patients)")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        tb = QFrame()
        tb.setFixedHeight(38)
        tb.setStyleSheet(TOOLBAR_STYLE)
        tb_l = QHBoxLayout(tb)
        tb_l.setContentsMargins(6, 4, 6, 4)
        tb_l.setSpacing(6)

        tb_l.addWidget(QLabel("Filter Patient:"))
        self.cb_blood_pat = QComboBox()
        self.cb_blood_pat.setFixedWidth(200)
        self.cb_blood_pat.currentIndexChanged.connect(self._load_blood_results)
        tb_l.addWidget(self.cb_blood_pat)

        btn_add = QPushButton(" Record Blood Test")
        btn_add.setIcon(icon_add())
        btn_add.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_add.clicked.connect(self._on_add_blood)

        self.btn_edit_blood = QPushButton(" Edit")
        self.btn_edit_blood.setIcon(icon_edit())
        self.btn_edit_blood.setEnabled(False)
        self.btn_edit_blood.clicked.connect(self._on_edit_blood)

        self.btn_del_blood = QPushButton(" Delete")
        self.btn_del_blood.setIcon(icon_delete())
        self.btn_del_blood.setEnabled(False)
        self.btn_del_blood.clicked.connect(self._on_delete_blood)

        btn_ref = QPushButton(" Refresh")
        btn_ref.setIcon(icon_refresh())
        btn_ref.clicked.connect(self._load_blood_results)

        tb_l.addWidget(btn_add)
        tb_l.addWidget(self.btn_edit_blood)
        tb_l.addWidget(self.btn_del_blood)
        tb_l.addStretch()
        tb_l.addWidget(btn_ref)
        layout.addWidget(tb)

        # Splitter: Table / Chart
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(5)

        # Table
        tf = QWidget()
        tf.setStyleSheet("background: #ECE9D8;")
        tfl = QVBoxLayout(tf)
        tfl.setContentsMargins(6, 6, 6, 3)

        self.tbl_blood = QTableWidget()
        b_cols = ["ResultID", "Patient Name", "Test Date"] + PARAMS
        self.tbl_blood.setColumnCount(len(b_cols))
        self.tbl_blood.setHorizontalHeaderLabels(b_cols)
        self.tbl_blood.setAlternatingRowColors(True)
        self.tbl_blood.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_blood.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_blood.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_blood.verticalHeader().setVisible(False)
        self.tbl_blood.setShowGrid(True)
        self.tbl_blood.itemSelectionChanged.connect(self._on_blood_selection)

        hh = self.tbl_blood.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        for c in range(3, len(b_cols)):
            hh.setSectionResizeMode(c, QHeaderView.ResizeToContents)

        tfl.addWidget(self.tbl_blood)
        splitter.addWidget(tf)

        # Chart
        gf = QWidget()
        gf.setStyleSheet("background: #ECE9D8;")
        gfl = QVBoxLayout(gf)
        gfl.setContentsMargins(6, 3, 6, 6)

        self.fig_admin = Figure(figsize=(10, 3.5), dpi=96, facecolor='#FAFAFA')
        self.canvas_admin = FigureCanvas(self.fig_admin)
        gfl.addWidget(self.canvas_admin)
        splitter.addWidget(gf)
        splitter.setSizes([220, 360])

        layout.addWidget(splitter)
        return w

    def _build_doctors_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Doctors Catalog & Clinical Specialists")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        tb = QFrame()
        tb.setFixedHeight(38)
        tb.setStyleSheet(TOOLBAR_STYLE)
        tb_l = QHBoxLayout(tb)
        tb_l.setContentsMargins(6, 4, 6, 4)
        tb_l.setSpacing(4)

        btn_add = QPushButton(" Add Doctor")
        btn_add.setIcon(icon_add())
        btn_add.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_add.clicked.connect(self._on_add_doctor)

        self.btn_edit_doc = QPushButton(" Edit Doctor")
        self.btn_edit_doc.setIcon(icon_edit())
        self.btn_edit_doc.setEnabled(False)
        self.btn_edit_doc.clicked.connect(self._on_edit_doctor)

        self.btn_del_doc = QPushButton(" Delete Doctor")
        self.btn_del_doc.setIcon(icon_delete())
        self.btn_del_doc.setEnabled(False)
        self.btn_del_doc.clicked.connect(self._on_delete_doctor)

        btn_asgn = QPushButton(" Assign Doctor to Patient")
        btn_asgn.setIcon(icon_doctor())
        btn_asgn.clicked.connect(lambda: AssignDoctorDialog(self).exec_() and self._load_doctors())

        btn_ref = QPushButton(" Refresh")
        btn_ref.setIcon(icon_refresh())
        btn_ref.clicked.connect(self._load_doctors)

        tb_l.addWidget(btn_add)
        tb_l.addWidget(self.btn_edit_doc)
        tb_l.addWidget(self.btn_del_doc)
        tb_l.addSpacing(10)
        tb_l.addWidget(btn_asgn)
        tb_l.addStretch()
        tb_l.addWidget(btn_ref)
        layout.addWidget(tb)

        df = QWidget()
        df.setStyleSheet("background: #ECE9D8;")
        dfl = QVBoxLayout(df)
        dfl.setContentsMargins(8, 8, 8, 8)

        self.tbl_doctors = QTableWidget()
        d_cols = ["DoctorID", "Doctor Name", "Speciality", "Experience", "Qualifications", "Contact Phone"]
        self.tbl_doctors.setColumnCount(len(d_cols))
        self.tbl_doctors.setHorizontalHeaderLabels(d_cols)
        self.tbl_doctors.setAlternatingRowColors(True)
        self.tbl_doctors.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_doctors.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_doctors.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_doctors.verticalHeader().setVisible(False)
        self.tbl_doctors.setShowGrid(True)
        self.tbl_doctors.itemSelectionChanged.connect(self._on_doctor_selection)

        hh = self.tbl_doctors.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.Stretch)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        dfl.addWidget(self.tbl_doctors)
        layout.addWidget(df)
        return w

    def _build_tests_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Available Diagnostic Tests Catalog")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        tb = QFrame()
        tb.setFixedHeight(38)
        tb.setStyleSheet(TOOLBAR_STYLE)
        tb_l = QHBoxLayout(tb)
        tb_l.setContentsMargins(6, 4, 6, 4)
        tb_l.setSpacing(4)

        btn_add = QPushButton(" Add New Test")
        btn_add.setIcon(icon_add())
        btn_add.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_add.clicked.connect(self._on_add_test)

        self.btn_edit_test = QPushButton(" Edit Test")
        self.btn_edit_test.setIcon(icon_edit())
        self.btn_edit_test.setEnabled(False)
        self.btn_edit_test.clicked.connect(self._on_edit_test)

        self.btn_del_test = QPushButton(" Delete Test")
        self.btn_del_test.setIcon(icon_delete())
        self.btn_del_test.setEnabled(False)
        self.btn_del_test.clicked.connect(self._on_delete_test)

        btn_asgn = QPushButton(" Prescribe Test for Patient")
        btn_asgn.setIcon(icon_tests())
        btn_asgn.clicked.connect(lambda: AssignTestDialog(self).exec_() and self._load_tests())

        btn_ref = QPushButton(" Refresh")
        btn_ref.setIcon(icon_refresh())
        btn_ref.clicked.connect(self._load_tests)

        tb_l.addWidget(btn_add)
        tb_l.addWidget(self.btn_edit_test)
        tb_l.addWidget(self.btn_del_test)
        tb_l.addSpacing(10)
        tb_l.addWidget(btn_asgn)
        tb_l.addStretch()
        tb_l.addWidget(btn_ref)
        layout.addWidget(tb)

        tf = QWidget()
        tf.setStyleSheet("background: #ECE9D8;")
        tfl = QVBoxLayout(tf)
        tfl.setContentsMargins(8, 8, 8, 8)

        self.tbl_tests = QTableWidget()
        t_cols = ["TestID", "Test Name", "Category / Department", "Price (INR)", "Description"]
        self.tbl_tests.setColumnCount(len(t_cols))
        self.tbl_tests.setHorizontalHeaderLabels(t_cols)
        self.tbl_tests.setAlternatingRowColors(True)
        self.tbl_tests.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_tests.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_tests.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_tests.verticalHeader().setVisible(False)
        self.tbl_tests.setShowGrid(True)
        self.tbl_tests.itemSelectionChanged.connect(self._on_test_selection)

        hh = self.tbl_tests.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.Stretch)

        tfl.addWidget(self.tbl_tests)
        layout.addWidget(tf)
        return w

    def _build_orders_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("  Diagnostic Test Orders & Workflow Tracking")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        tb = QFrame()
        tb.setFixedHeight(38)
        tb.setStyleSheet(TOOLBAR_STYLE)
        tb_l = QHBoxLayout(tb)
        tb_l.setContentsMargins(6, 4, 6, 4)
        tb_l.setSpacing(4)

        btn_new_order = QPushButton(" New Test Order")
        btn_new_order.setIcon(icon_add())
        btn_new_order.setStyleSheet(BLUE_BUTTON_STYLE)
        btn_new_order.clicked.connect(lambda: AssignTestDialog(self).exec_() and self._load_orders())

        self.btn_set_comp = QPushButton(" Mark Completed ")
        self.btn_set_comp.setEnabled(False)
        self.btn_set_comp.clicked.connect(lambda: self._update_order_status("Completed"))

        self.btn_set_canc = QPushButton(" Mark Cancelled ")
        self.btn_set_canc.setEnabled(False)
        self.btn_set_canc.clicked.connect(lambda: self._update_order_status("Cancelled"))

        self.btn_del_order = QPushButton(" Delete Order ")
        self.btn_del_order.setIcon(icon_delete())
        self.btn_del_order.setEnabled(False)
        self.btn_del_order.clicked.connect(self._on_delete_order)

        btn_ref = QPushButton(" Refresh")
        btn_ref.setIcon(icon_refresh())
        btn_ref.clicked.connect(self._load_orders)

        tb_l.addWidget(btn_new_order)
        tb_l.addSpacing(6)
        tb_l.addWidget(self.btn_set_comp)
        tb_l.addWidget(self.btn_set_canc)
        tb_l.addWidget(self.btn_del_order)
        tb_l.addStretch()
        tb_l.addWidget(btn_ref)
        layout.addWidget(tb)

        of = QWidget()
        of.setStyleSheet("background: #ECE9D8;")
        ofl = QVBoxLayout(of)
        ofl.setContentsMargins(8, 8, 8, 8)

        self.tbl_orders = QTableWidget()
        o_cols = ["AssignID", "Patient Name", "Test Name", "Category", "Price (INR)", "Order Date", "Status", "Clinical Notes"]
        self.tbl_orders.setColumnCount(len(o_cols))
        self.tbl_orders.setHorizontalHeaderLabels(o_cols)
        self.tbl_orders.setAlternatingRowColors(True)
        self.tbl_orders.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_orders.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_orders.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_orders.verticalHeader().setVisible(False)
        self.tbl_orders.setShowGrid(True)
        self.tbl_orders.itemSelectionChanged.connect(self._on_order_selection)

        hh = self.tbl_orders.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(7, QHeaderView.Stretch)

        ofl.addWidget(self.tbl_orders)
        layout.addWidget(of)
        return w

    # ── Navigation & Refresh ─────────────────────────────────────────────────

    def _navigate(self, page_idx: int):
        self.stack.setCurrentIndex(page_idx)
        for i, b in enumerate(self._nav_buttons):
            b.setChecked(i == page_idx)

        # Trigger data loading on visit
        if page_idx == self.PAGE_PATIENTS:
            self._load_patients()
        elif page_idx == self.PAGE_BLOOD:
            self._load_blood_patients_combo()
            self._load_blood_results()
        elif page_idx == self.PAGE_DOCTORS:
            self._load_doctors()
        elif page_idx == self.PAGE_TESTS:
            self._load_tests()
        elif page_idx == self.PAGE_ORDERS:
            self._load_orders()

    def _refresh_all(self):
        self._load_patients()
        self._load_blood_patients_combo()
        self._load_blood_results()
        self._load_doctors()
        self._load_tests()
        self._load_orders()
        self.sb_status.setText(" Status: All Tables Refreshed")

    # ── CRUD Logic: Patients ─────────────────────────────────────────────────

    def _load_patients(self):
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM patient_details ORDER BY PatID ASC")
            self._patients_cache = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Cannot load patients:\n{e}")
            self._patients_cache = []

        self.tbl_patients.setRowCount(len(self._patients_cache))
        BLACK  = QColor('#000000')
        WHITE  = QColor('#FFFFFF')
        ALT_BG = QColor('#F1F6FC')

        for r_idx, p in enumerate(self._patients_cache):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE

            def _itm(v, align=Qt.AlignLeft):
                it = QTableWidgetItem(str(v) if v is not None else "--")
                it.setTextAlignment(align | Qt.AlignVCenter)
                it.setForeground(QBrush(BLACK))
                it.setBackground(QBrush(bg))
                return it

            self.tbl_patients.setItem(r_idx, 0, _itm(f"PAT-{p['PatID']:04d}", Qt.AlignCenter))
            self.tbl_patients.setItem(r_idx, 1, _itm(p['PatName']))
            self.tbl_patients.setItem(r_idx, 2, _itm(p['MobileNumber'], Qt.AlignCenter))
            self.tbl_patients.setItem(r_idx, 3, _itm(p['Address']))
            self.tbl_patients.setItem(r_idx, 4, _itm(p['Age'], Qt.AlignCenter))
            self.tbl_patients.setItem(r_idx, 5, _itm(p['DOB'], Qt.AlignCenter))
            self.tbl_patients.setItem(r_idx, 6, _itm(p['Weight'], Qt.AlignCenter))
            self.tbl_patients.setItem(r_idx, 7, _itm(p['LoginID'], Qt.AlignCenter))
            self.tbl_patients.setRowHeight(r_idx, 23)

        self._on_patient_selection()

    def _on_patient_selection(self):
        has_sel = bool(self.tbl_patients.selectedItems())
        self.btn_edit_pat.setEnabled(has_sel)
        self.btn_del_pat.setEnabled(has_sel)
        self.btn_asgn_doc.setEnabled(has_sel)
        self.btn_asgn_test.setEnabled(has_sel)

    def _get_selected_patient(self):
        r = self.tbl_patients.currentRow()
        if r < 0 or r >= len(self._patients_cache):
            return None
        return self._patients_cache[r]

    def _on_add_patient(self):
        dlg = PatientEditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._load_patients()

    def _on_edit_patient(self):
        p = self._get_selected_patient()
        if not p:
            return
        dlg = PatientEditDialog(self, existing=p)
        if dlg.exec_() == QDialog.Accepted:
            self._load_patients()

    def _on_delete_patient(self):
        p = self._get_selected_patient()
        if not p:
            return
        ans = QMessageBox.question(
            self, "Confirm Patient Deletion",
            f"Are you sure you want to permanently delete patient:\n\n"
            f"'{p['PatName']}' (PAT-{p['PatID']:04d})?\n\n"
            f"WARNING: This will cascade and delete all their blood test results,\n"
            f"assigned tests, and doctor assignments!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM patient_details WHERE PatID = %s", (p['PatID'],))
                conn.commit()
                cur.close()
                conn.close()
                self._load_patients()
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete patient:\n{e}")

    def _on_assign_doc_patient(self):
        p = self._get_selected_patient()
        if p:
            dlg = AssignDoctorDialog(self, default_pat_id=p['PatID'])
            dlg.exec_()

    def _on_assign_test_patient(self):
        p = self._get_selected_patient()
        if p:
            dlg = AssignTestDialog(self, default_pat_id=p['PatID'])
            dlg.exec_()

    # ── CRUD Logic: Blood Records ────────────────────────────────────────────

    def _load_blood_patients_combo(self):
        self.cb_blood_pat.blockSignals(True)
        self.cb_blood_pat.clear()
        self.cb_blood_pat.addItem("All Patients", None)
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT PatID, PatName FROM patient_details ORDER BY PatName")
            for p in cur.fetchall():
                self.cb_blood_pat.addItem(f"{p['PatName']} (PAT-{p['PatID']:04d})", p['PatID'])
            cur.close()
            conn.close()
        except Exception:
            pass
        self.cb_blood_pat.blockSignals(False)

    def _load_blood_results(self):
        pat_id = self.cb_blood_pat.currentData()
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            if pat_id:
                cur.execute("""
                    SELECT b.*, p.PatName FROM blood_test_results b
                    JOIN patient_details p ON b.PatID = p.PatID
                    WHERE b.PatID = %s
                    ORDER BY b.TestDate ASC
                """, (pat_id,))
            else:
                cur.execute("""
                    SELECT b.*, p.PatName FROM blood_test_results b
                    JOIN patient_details p ON b.PatID = p.PatID
                    ORDER BY b.TestDate DESC
                """)
            self._blood_cache = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            self._blood_cache = []

        self.tbl_blood.setRowCount(len(self._blood_cache))
        BLACK  = QColor('#000000')
        WHITE  = QColor('#FFFFFF')
        ALT_BG = QColor('#F1F6FC')
        OOR_BG = QColor('#FFE8E8')
        OOR_FG = QColor('#AA0000')

        for r_idx, b in enumerate(self._blood_cache):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE

            it0 = QTableWidgetItem(str(b['ResultID']))
            it0.setTextAlignment(Qt.AlignCenter)
            it0.setForeground(QBrush(BLACK))
            it0.setBackground(QBrush(bg))
            self.tbl_blood.setItem(r_idx, 0, it0)

            it1 = QTableWidgetItem(f"{b['PatName']} (PAT-{b['PatID']:04d})")
            it1.setForeground(QBrush(QColor('#003399')))
            it1.setBackground(QBrush(bg))
            self.tbl_blood.setItem(r_idx, 1, it1)

            it2 = QTableWidgetItem(str(b['TestDate']))
            it2.setTextAlignment(Qt.AlignCenter)
            it2.setForeground(QBrush(BLACK))
            it2.setBackground(QBrush(bg))
            self.tbl_blood.setItem(r_idx, 2, it2)

            for c_idx, param in enumerate(PARAMS, start=3):
                val = b.get(param)
                val_str = f"{float(val):.2f}" if val is not None else "--"
                item = QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignCenter)

                lo, hi = NORMAL_RANGES[param]
                oor = False
                if val is not None and not (lo <= float(val) <= hi):
                    oor = True

                if oor:
                    item.setBackground(QBrush(OOR_BG))
                    item.setForeground(QBrush(OOR_FG))
                else:
                    item.setBackground(QBrush(bg))
                    item.setForeground(QBrush(BLACK))

                item.setToolTip(f"{param}: {val_str} (Normal Ref: {lo} - {hi})")
                self.tbl_blood.setItem(r_idx, c_idx, item)

            self.tbl_blood.setRowHeight(r_idx, 23)

        self._on_blood_selection()
        self._draw_admin_graph(pat_id)

    def _draw_admin_graph(self, pat_id):
        self.fig_admin.clear()
        if not pat_id or not self._blood_cache:
            ax = self.fig_admin.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Select a specific patient in the filter dropdown to view their blood history chart.",
                    ha='center', va='center', color='#707070', fontsize=10)
            self.canvas_admin.draw()
            return

        ax = self.fig_admin.add_subplot(111)
        ax.set_facecolor('#FFFFFF')

        dates = []
        for r in self._blood_cache:
            d = r['TestDate']
            if isinstance(d, str):
                d = datetime.strptime(d, '%Y-%m-%d').date()
            dates.append(d)

        for param in PARAMS:
            meta = PARAM_META[param]
            values = [float(r[param]) if r.get(param) is not None else None for r in self._blood_cache]
            p_dates = [d for d, v in zip(dates, values) if v is not None]
            p_vals  = [v for v in values if v is not None]
            if p_dates:
                ax.plot(p_dates, p_vals, color=meta['color'], marker='o', markersize=4,
                        linewidth=1.6, label=f"{param} ({meta['unit']})")

        pat_name = self.cb_blood_pat.currentText()
        ax.set_title(f"Clinical Blood Count Trends — {pat_name}", fontsize=10, fontweight='bold', color='#003399')
        ax.set_xlabel("Test Date", fontsize=8, color='#333333')
        ax.set_ylabel("Parameter Values", fontsize=8, color='#333333')
        ax.grid(True, linestyle='--', alpha=0.4, color='#C0C0C0')
        ax.tick_params(labelsize=8)

        if len(dates) > 1:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
            self.fig_admin.autofmt_xdate(rotation=25, ha='right')

        ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0), fontsize=7, frameon=True, edgecolor='#808080')
        self.fig_admin.subplots_adjust(right=0.74, bottom=0.20, top=0.88, left=0.08)
        self.canvas_admin.draw()

    def _on_blood_selection(self):
        has_sel = bool(self.tbl_blood.selectedItems())
        self.btn_edit_blood.setEnabled(has_sel)
        self.btn_del_blood.setEnabled(has_sel)

    def _get_selected_blood(self):
        r = self.tbl_blood.currentRow()
        if r < 0 or r >= len(self._blood_cache):
            return None
        return self._blood_cache[r]

    def _on_add_blood(self):
        # Pick patient
        pat_id = self.cb_blood_pat.currentData()
        if not pat_id:
            # Show patient selector dialog
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT PatID, PatName FROM patient_details ORDER BY PatName")
            pats = cur.fetchall()
            cur.close()
            conn.close()
            if not pats:
                QMessageBox.warning(self, "No Patients", "Please add a patient first.")
                return

            d = QDialog(self)
            d.setWindowTitle("Select Patient for Blood Test")
            d.setFixedSize(360, 140)
            d.setStyleSheet(XP_STYLE)
            dl = QVBoxLayout(d)
            cb = QComboBox()
            for p in pats:
                cb.addItem(f"{p['PatName']} (PAT-{p['PatID']:04d})", p['PatID'])
            dl.addWidget(QLabel("Select target patient:"))
            dl.addWidget(cb)
            btn_ok = QPushButton(" Proceed to Record Form ")
            btn_ok.setStyleSheet(BLUE_BUTTON_STYLE)
            btn_ok.clicked.connect(d.accept)
            dl.addWidget(btn_ok)
            if d.exec_() != QDialog.Accepted:
                return
            pat_id = cb.currentData()

        dlg = BloodEntryDialog(pat_id, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            self._load_blood_results()

    def _on_edit_blood(self):
        b = self._get_selected_blood()
        if not b:
            return
        dlg = BloodEntryDialog(b['PatID'], parent=self, existing=b)
        if dlg.exec_() == QDialog.Accepted:
            self._load_blood_results()

    def _on_delete_blood(self):
        b = self._get_selected_blood()
        if not b:
            return
        ans = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete blood record #{b['ResultID']} for {b['PatName']} dated {b['TestDate']}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM blood_test_results WHERE ResultID = %s", (b['ResultID'],))
            conn.commit()
            cur.close()
            conn.close()
            self._load_blood_results()

    # ── CRUD Logic: Doctors ──────────────────────────────────────────────────

    def _load_doctors(self):
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM doctor_catalog ORDER BY DoctorID ASC")
            self._doctors_cache = cur.fetchall()
            cur.close()
            conn.close()
        except Exception:
            self._doctors_cache = []

        self.tbl_doctors.setRowCount(len(self._doctors_cache))
        BLACK  = QColor('#000000')
        WHITE  = QColor('#FFFFFF')
        ALT_BG = QColor('#F1F6FC')

        for r_idx, d in enumerate(self._doctors_cache):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE

            def _itm(v, align=Qt.AlignLeft):
                it = QTableWidgetItem(str(v) if v is not None else "--")
                it.setTextAlignment(align | Qt.AlignVCenter)
                it.setForeground(QBrush(BLACK))
                it.setBackground(QBrush(bg))
                return it

            self.tbl_doctors.setItem(r_idx, 0, _itm(f"DOC-{d['DoctorID']:03d}", Qt.AlignCenter))
            self.tbl_doctors.setItem(r_idx, 1, _itm(d['DoctorName']))
            self.tbl_doctors.setItem(r_idx, 2, _itm(d['Speciality']))
            self.tbl_doctors.setItem(r_idx, 3, _itm(f"{d['YearsExperience']} yrs", Qt.AlignCenter))
            self.tbl_doctors.setItem(r_idx, 4, _itm(d['Qualification']))
            self.tbl_doctors.setItem(r_idx, 5, _itm(d['ContactNumber'], Qt.AlignCenter))
            self.tbl_doctors.setRowHeight(r_idx, 23)

        self._on_doctor_selection()

    def _on_doctor_selection(self):
        has_sel = bool(self.tbl_doctors.selectedItems())
        self.btn_edit_doc.setEnabled(has_sel)
        self.btn_del_doc.setEnabled(has_sel)

    def _get_selected_doctor(self):
        r = self.tbl_doctors.currentRow()
        if r < 0 or r >= len(self._doctors_cache):
            return None
        return self._doctors_cache[r]

    def _on_add_doctor(self):
        dlg = DoctorEditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._load_doctors()

    def _on_edit_doctor(self):
        d = self._get_selected_doctor()
        if not d:
            return
        dlg = DoctorEditDialog(self, existing=d)
        if dlg.exec_() == QDialog.Accepted:
            self._load_doctors()

    def _on_delete_doctor(self):
        d = self._get_selected_doctor()
        if not d:
            return
        ans = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete Doctor:\n'{d['DoctorName']}' ({d['Speciality']})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM doctor_catalog WHERE DoctorID = %s", (d['DoctorID'],))
            conn.commit()
            cur.close()
            conn.close()
            self._load_doctors()

    # ── CRUD Logic: Tests ────────────────────────────────────────────────────

    def _load_tests(self):
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM tests_catalog ORDER BY TestID ASC")
            self._tests_cache = cur.fetchall()
            cur.close()
            conn.close()
        except Exception:
            self._tests_cache = []

        self.tbl_tests.setRowCount(len(self._tests_cache))
        BLACK  = QColor('#000000')
        WHITE  = QColor('#FFFFFF')
        ALT_BG = QColor('#F1F6FC')

        for r_idx, t in enumerate(self._tests_cache):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE

            def _itm(v, align=Qt.AlignLeft):
                it = QTableWidgetItem(str(v) if v is not None else "--")
                it.setTextAlignment(align | Qt.AlignVCenter)
                it.setForeground(QBrush(BLACK))
                it.setBackground(QBrush(bg))
                return it

            self.tbl_tests.setItem(r_idx, 0, _itm(f"TEST-{t['TestID']:03d}", Qt.AlignCenter))
            self.tbl_tests.setItem(r_idx, 1, _itm(t['TestName']))
            self.tbl_tests.setItem(r_idx, 2, _itm(t['Category']))
            self.tbl_tests.setItem(r_idx, 3, _itm(f"INR {t['Price']:.2f}", Qt.AlignRight))
            self.tbl_tests.setItem(r_idx, 4, _itm(t['Description']))
            self.tbl_tests.setRowHeight(r_idx, 23)

        self._on_test_selection()

    def _on_test_selection(self):
        has_sel = bool(self.tbl_tests.selectedItems())
        self.btn_edit_test.setEnabled(has_sel)
        self.btn_del_test.setEnabled(has_sel)

    def _get_selected_test(self):
        r = self.tbl_tests.currentRow()
        if r < 0 or r >= len(self._tests_cache):
            return None
        return self._tests_cache[r]

    def _on_add_test(self):
        dlg = TestEditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._load_tests()

    def _on_edit_test(self):
        t = self._get_selected_test()
        if not t:
            return
        dlg = TestEditDialog(self, existing=t)
        if dlg.exec_() == QDialog.Accepted:
            self._load_tests()

    def _on_delete_test(self):
        t = self._get_selected_test()
        if not t:
            return
        ans = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete test '{t['TestName']}' from catalog?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM tests_catalog WHERE TestID = %s", (t['TestID'],))
            conn.commit()
            cur.close()
            conn.close()
            self._load_tests()

    # ── CRUD Logic: Orders / Assigned Tests ───────────────────────────────────

    def _load_orders(self):
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT ta.*, tc.TestName, tc.Category, tc.Price, p.PatName
                FROM tests_assigned ta
                JOIN tests_catalog tc ON ta.TestID = tc.TestID
                JOIN patient_details p ON ta.PatID = p.PatID
                ORDER BY ta.AssignDate DESC, ta.AssignID DESC
            """)
            self._orders_cache = cur.fetchall()
            cur.close()
            conn.close()
        except Exception:
            self._orders_cache = []

        self.tbl_orders.setRowCount(len(self._orders_cache))
        BLACK  = QColor('#000000')
        WHITE  = QColor('#FFFFFF')
        ALT_BG = QColor('#F1F6FC')

        for r_idx, o in enumerate(self._orders_cache):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE

            def _itm(v, align=Qt.AlignLeft):
                it = QTableWidgetItem(str(v) if v is not None else "--")
                it.setTextAlignment(align | Qt.AlignVCenter)
                it.setForeground(QBrush(BLACK))
                it.setBackground(QBrush(bg))
                return it

            self.tbl_orders.setItem(r_idx, 0, _itm(o['AssignID'], Qt.AlignCenter))
            self.tbl_orders.setItem(r_idx, 1, _itm(f"{o['PatName']} (PAT-{o['PatID']:04d})"))
            self.tbl_orders.setItem(r_idx, 2, _itm(o['TestName']))
            self.tbl_orders.setItem(r_idx, 3, _itm(o['Category']))
            self.tbl_orders.setItem(r_idx, 4, _itm(f"INR {o['Price']:.2f}", Qt.AlignRight))
            self.tbl_orders.setItem(r_idx, 5, _itm(o['AssignDate'], Qt.AlignCenter))

            stat = o['Status']
            it_stat = QTableWidgetItem(f" {stat} ")
            it_stat.setTextAlignment(Qt.AlignCenter)
            if stat == 'Completed':
                it_stat.setForeground(QBrush(QColor('#006600')))
                it_stat.setBackground(QBrush(QColor('#E2F4E2')))
            elif stat == 'Cancelled':
                it_stat.setForeground(QBrush(QColor('#880000')))
                it_stat.setBackground(QBrush(QColor('#FCE2E2')))
            else:
                it_stat.setForeground(QBrush(QColor('#7B5800')))
                it_stat.setBackground(QBrush(QColor('#FFF8D8')))
            f = QFont("Tahoma", 9)
            f.setBold(True)
            it_stat.setFont(f)
            self.tbl_orders.setItem(r_idx, 6, it_stat)

            self.tbl_orders.setItem(r_idx, 7, _itm(o['Notes']))
            self.tbl_orders.setRowHeight(r_idx, 23)

        self._on_order_selection()

    def _on_order_selection(self):
        has_sel = bool(self.tbl_orders.selectedItems())
        self.btn_set_comp.setEnabled(has_sel)
        self.btn_set_canc.setEnabled(has_sel)
        self.btn_del_order.setEnabled(has_sel)

    def _get_selected_order(self):
        r = self.tbl_orders.currentRow()
        if r < 0 or r >= len(self._orders_cache):
            return None
        return self._orders_cache[r]

    def _update_order_status(self, new_status: str):
        o = self._get_selected_order()
        if not o:
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE tests_assigned SET Status = %s WHERE AssignID = %s", (new_status, o['AssignID']))
            conn.commit()
            cur.close()
            conn.close()
            self._load_orders()
        except Exception as e:
            QMessageBox.critical(self, "Status Error", f"Could not update status:\n{e}")

    def _on_delete_order(self):
        o = self._get_selected_order()
        if not o:
            return
        ans = QMessageBox.question(
            self, "Confirm Delete Order",
            f"Delete test order #{o['AssignID']} ({o['TestName']} for {o['PatName']})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM tests_assigned WHERE AssignID = %s", (o['AssignID'],))
            conn.commit()
            cur.close()
            conn.close()
            self._load_orders()

    # ── System / Logout ───────────────────────────────────────────────────────

    def _on_logout(self):
        ans = QMessageBox.question(
            self, "Log Off Administrator",
            "Are you sure you want to log off from the MEDORA Administration Console?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            self.close()
            self.login_window.login_id_field.clear()
            self.login_window.password_field.clear()
            self.login_window.login_status.setText("")
            self.login_window.status_bar.showMessage("Logged off from Administrator mode.")
            self.login_window.show()

    def _show_about(self):
        QMessageBox.about(
            self, "About MEDORA Administrator Console",
            "<b>Project MEDORA — System Administration Console</b><br>"
            "Windows XP Server &amp; Clinic Master Management Edition<br><br>"
            "<b>Privilege Level:</b> SuperAdmin (Full DDL / DML / SQL Access)<br>"
            "<b>Features:</b><br>"
            "• Patient records lifecycle management (Add, Edit, Delete, Vitals)<br>"
            "• Complete Blood Test history management &amp; multi-line trend charts<br>"
            "• Doctors Catalog &amp; Patient Assignment Management<br>"
            "• Tests Available Catalog &amp; Order Scheduling<br>"
            "• Integrated Interactive SQL Shell / Terminal with direct query engine<br><br>"
            "<i>Built with PyQt5, mysql-connector-python, Matplotlib</i>"
        )
