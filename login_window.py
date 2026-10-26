# login_window.py - Login & Registration window for Project MEDORA (Windows XP style)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStatusBar, QFrame, QDialog, QFormLayout,
    QScrollArea, QMessageBox, QApplication, QMainWindow
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from styles import (
    XP_STYLE, LOGIN_BANNER_STYLE, LOGIN_PANEL_STYLE,
    LOGIN_TITLE_STYLE, LOGIN_SUBTITLE_STYLE, LOGIN_HEADER_STYLE,
    BLUE_BUTTON_STYLE
)
from xp_icons import icon_eye, icon_medora, icon_profile, icon_save, icon_delete
import auth


# ─────────────────────────────────────────────────────────────────────────────
#  Registration Dialog
# ─────────────────────────────────────────────────────────────────────────────

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MEDORA - New Patient Registration")
        self.setWindowIcon(icon_medora())
        self.setFixedSize(560, 680)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header banner
        banner = QLabel("  New Patient Registration Wizard")
        banner.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0A246A, stop:0.5 #003399, stop:1 #0050A0);
            color: white;
            font-weight: bold;
            font-size: 11pt;
            font-family: Tahoma, Arial;
            padding: 8px 12px;
            border-bottom: 2px solid #001166;
        """)
        banner.setFixedHeight(40)
        main_layout.addWidget(banner)

        # Scrollable form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        form_widget = QWidget()
        form_widget.setStyleSheet("background: #ECE9D8;")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(24, 20, 24, 20)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        def _field(placeholder='', echo=QLineEdit.Normal):
            le = QLineEdit()
            le.setPlaceholderText(placeholder)
            le.setEchoMode(echo)
            le.setMinimumHeight(26)
            le.setStyleSheet("""
                background-color: #FFFFFF;
                border: 1px solid #7F9DB9;
                font-family: Tahoma, Arial;
                font-size: 9pt;
                padding: 2px 4px;
                color: #000000;
            """)
            return le

        def _lbl(text):
            lb = QLabel(text)
            lb.setStyleSheet(
                "font-family: Tahoma, Arial; font-size: 9pt; font-weight: bold; color: #333333;"
            )
            return lb

        self.f_name    = _field("Full legal name")
        self.f_mobile  = _field("10-digit mobile phone number")
        self.f_address = _field("Permanent residential address")
        self.f_age     = _field("Age in years")
        self.f_dob     = _field("YYYY-MM-DD")
        self.f_weight  = _field("Weight in kilograms (e.g. 68.5)")
        self.f_loginid = _field("Unique username for portal login")
        self.f_pass    = _field("Minimum 6 characters", QLineEdit.Password)
        self.f_cpass   = _field("Repeat password", QLineEdit.Password)

        form_layout.addRow(_lbl("Full Name *:"),    self.f_name)
        form_layout.addRow(_lbl("Mobile Number:"),  self.f_mobile)
        form_layout.addRow(_lbl("Address:"),        self.f_address)
        form_layout.addRow(_lbl("Age:"),            self.f_age)
        form_layout.addRow(_lbl("Date of Birth:"),  self.f_dob)
        form_layout.addRow(_lbl("Weight (kg):"),    self.f_weight)
        form_layout.addRow(_lbl("Login ID *:"),     self.f_loginid)
        form_layout.addRow(_lbl("Password *:"),     self.f_pass)
        form_layout.addRow(_lbl("Confirm Pwd *:"),  self.f_cpass)

        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)

        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #CC0000; font-family: Tahoma, Arial; font-size: 8.5pt; font-weight: bold;"
        )
        self.status_label.setFixedHeight(22)
        main_layout.addWidget(self.status_label)

        # Buttons row
        btn_frame = QFrame()
        btn_frame.setStyleSheet(
            "background: #D4D0C8; border-top: 1px solid #ACA899;"
        )
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(12, 8, 12, 8)
        btn_layout.addStretch()

        self.btn_register = QPushButton(" Register ")
        self.btn_register.setIcon(icon_save())
        self.btn_register.setStyleSheet(BLUE_BUTTON_STYLE)
        self.btn_register.setDefault(True)
        self.btn_register.clicked.connect(self._on_register)

        btn_cancel = QPushButton(" Cancel ")
        btn_cancel.setIcon(icon_delete())
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_register)
        btn_layout.addSpacing(8)
        btn_layout.addWidget(btn_cancel)
        main_layout.addWidget(btn_frame)

    def _on_register(self):
        self.status_label.setText("")

        name     = self.f_name.text().strip()
        mobile   = self.f_mobile.text().strip()
        address  = self.f_address.text().strip()
        age_txt  = self.f_age.text().strip()
        dob      = self.f_dob.text().strip()
        wt_txt   = self.f_weight.text().strip()
        login_id = self.f_loginid.text().strip()
        pwd      = self.f_pass.text()
        cpwd     = self.f_cpass.text()

        if not name:
            self.status_label.setText("Error: Full name is required.")
            self.f_name.setFocus()
            return
        if not login_id:
            self.status_label.setText("Error: Login ID is required.")
            self.f_loginid.setFocus()
            return
        if not pwd:
            self.status_label.setText("Error: Password is required.")
            self.f_pass.setFocus()
            return
        if pwd != cpwd:
            self.status_label.setText("Error: Passwords do not match.")
            self.f_cpass.setFocus()
            return
        if len(pwd) < 6:
            self.status_label.setText("Error: Password must be at least 6 characters.")
            self.f_pass.setFocus()
            return

        age = None
        if age_txt:
            try:
                age = int(age_txt)
            except ValueError:
                self.status_label.setText("Error: Age must be an integer.")
                return

        weight = None
        if wt_txt:
            try:
                weight = float(wt_txt)
            except ValueError:
                self.status_label.setText("Error: Weight must be a valid number (e.g. 68.5).")
                return

        try:
            ok, msg = auth.register(name, mobile, address, age,
                                    dob or None, weight, login_id, pwd)
        except RuntimeError as e:
            ok, msg = False, str(e)

        if ok:
            QMessageBox.information(
                self, "Registration Successful",
                f"Patient '{name}' registered successfully!\n\n"
                f"You can now login using:\nLogin ID: {login_id}"
            )
            self.accept()
        else:
            self.status_label.setText(f"Error: {msg}")


# ─────────────────────────────────────────────────────────────────────────────
#  Login Window
# ─────────────────────────────────────────────────────────────────────────────

class LoginWindow(QMainWindow):
    """Main login screen displayed at application startup."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MEDORA - Patient Authentication")
        self.setWindowIcon(icon_medora())
        self.setFixedSize(800, 500)
        self.setStyleSheet(XP_STYLE)
        self._patient_data = None
        self._build_ui()

    @property
    def patient_data(self):
        return self._patient_data

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Top banner
        banner = QFrame()
        banner.setFixedHeight(120)
        banner.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #0A246A, stop:0.45 #184CA0, stop:1 #0050A0);"
        )
        banner_layout = QVBoxLayout(banner)
        banner_layout.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel("Project MEDORA")
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(LOGIN_TITLE_STYLE)

        sub_lbl = QLabel(
            "Medical Electronic Data & Online Records Analysis"
        )
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(LOGIN_SUBTITLE_STYLE)

        banner_layout.addWidget(title_lbl)
        banner_layout.addWidget(sub_lbl)
        root.addWidget(banner)

        # Middle area: decorative side strips + login panel
        middle = QHBoxLayout()
        middle.setSpacing(0)

        left_strip = QFrame()
        left_strip.setFixedWidth(28)
        left_strip.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #003399, stop:1 #ECE9D8);"
        )
        middle.addWidget(left_strip)

        card_wrapper = QHBoxLayout()
        card_wrapper.setAlignment(Qt.AlignCenter)

        login_card = QFrame()
        login_card.setFixedSize(390, 310)
        login_card.setStyleSheet(LOGIN_PANEL_STYLE)
        card_layout = QVBoxLayout(login_card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(28, 18, 28, 18)

        # Header
        hdr = QLabel("Patient Account Login")
        hdr.setAlignment(Qt.AlignCenter)
        hdr.setStyleSheet(LOGIN_HEADER_STYLE)
        card_layout.addWidget(hdr)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: #ACA899;")
        card_layout.addWidget(div)

        # Login ID field
        lbl_id = QLabel("Login ID / Username:")
        lbl_id.setStyleSheet("font-family: Tahoma, Arial; font-size: 8.5pt; font-weight: bold; color: #333333;")
        self.login_id_field = QLineEdit()
        self.login_id_field.setPlaceholderText("Enter your assigned login ID")
        self.login_id_field.setMinimumHeight(26)

        # Password row
        lbl_pw = QLabel("Account Password:")
        lbl_pw.setStyleSheet("font-family: Tahoma, Arial; font-size: 8.5pt; font-weight: bold; color: #333333;")
        pw_row = QHBoxLayout()
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Enter password")
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setMinimumHeight(26)
        self.password_field.returnPressed.connect(self._on_login)

        self.eye_btn = QPushButton("Show")
        self.eye_btn.setIcon(icon_eye())
        self.eye_btn.setFixedSize(58, 26)
        self.eye_btn.setToolTip("Show / hide password text")
        self.eye_btn.setCheckable(True)
        self.eye_btn.toggled.connect(self._toggle_pw_visibility)

        pw_row.addWidget(self.password_field)
        pw_row.addWidget(self.eye_btn)

        card_layout.addWidget(lbl_id)
        card_layout.addWidget(self.login_id_field)
        card_layout.addWidget(lbl_pw)
        card_layout.addLayout(pw_row)

        # Status text
        self.login_status = QLabel("")
        self.login_status.setAlignment(Qt.AlignCenter)
        self.login_status.setStyleSheet(
            "color: #CC0000; font-family: Tahoma, Arial; font-size: 8.5pt; font-weight: bold;"
        )
        self.login_status.setFixedHeight(18)
        card_layout.addWidget(self.login_status)

        # Action Buttons
        btn_row = QHBoxLayout()
        self.btn_login = QPushButton(" Login ")
        self.btn_login.setStyleSheet(BLUE_BUTTON_STYLE)
        self.btn_login.setDefault(True)
        self.btn_login.clicked.connect(self._on_login)

        btn_register = QPushButton(" Register New ")
        btn_register.setIcon(icon_profile())
        btn_register.clicked.connect(self._on_register)

        btn_row.addWidget(self.btn_login)
        btn_row.addSpacing(6)
        btn_row.addWidget(btn_register)
        card_layout.addLayout(btn_row)

        card_wrapper.addWidget(login_card)
        middle.addLayout(card_wrapper)

        right_strip = QFrame()
        right_strip.setFixedWidth(28)
        right_strip.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #ECE9D8, stop:1 #003399);"
        )
        middle.addWidget(right_strip)
        root.addLayout(middle)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(
            "Project MEDORA Windows XP Edition | Please enter your credentials."
        )

    def _toggle_pw_visibility(self, checked):
        if checked:
            self.password_field.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("Hide")
        else:
            self.password_field.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("Show")

    def _on_login(self):
        self.login_status.setText("")
        login_id = self.login_id_field.text().strip()
        password = self.password_field.text()

        if not login_id:
            self.login_status.setText("Please enter your Login ID.")
            self.login_id_field.setFocus()
            return
        if not password:
            self.login_status.setText("Please enter your Password.")
            self.password_field.setFocus()
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("Authenticating...")
        QApplication.processEvents()

        try:
            patient = auth.login(login_id, password)
        except (RuntimeError, Exception) as e:
            self.login_status.setText(f"{e}")
            self.btn_login.setEnabled(True)
            self.btn_login.setText(" Login ")
            return

        self.btn_login.setEnabled(True)
        self.btn_login.setText(" Login ")

        if patient:
            self._patient_data = patient
            self.status_bar.showMessage("Authentication successful. Launching workspace...")
            self.hide()
            self._open_main_window()
        else:
            self.login_status.setText("Invalid Login ID or Password.")
            self.password_field.clear()
            self.password_field.setFocus()

    def _on_register(self):
        dlg = RegisterDialog(self)
        dlg.exec_()

    def _open_main_window(self):
        if self._patient_data and self._patient_data.get('is_admin'):
            from admin_window import AdminMainWindow
            self._admin_win = AdminMainWindow(self._patient_data, self)
            self._admin_win.show()
        else:
            from main_window import MainWindow
            self._main_win = MainWindow(self._patient_data, self)
            self._main_win.show()
