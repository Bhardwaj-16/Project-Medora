# main_window.py - Main application window for Project MEDORA (Windows XP Style)

from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QStatusBar, QAction, QMenuBar, QMessageBox,
    QSizePolicy, QScrollArea, QToolBar, QToolButton
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor

from styles import (
    XP_STYLE, SIDEBAR_STYLE, SIDEBAR_HEADER_STYLE,
    NAV_BUTTON_STYLE, LOGOUT_BUTTON_STYLE, SUBHEADER_STYLE
)
from xp_icons import (
    icon_dashboard, icon_blood, icon_doctor, icon_tests,
    icon_profile, icon_logout, icon_graph, icon_refresh,
    icon_folder, icon_folder_open, icon_document, icon_medora
)

from dashboard      import DashboardWidget
from blood_results  import BloodResultsWidget
from my_doctors     import MyDoctorsWidget
from my_tests       import MyTestsWidget
from profile        import ProfileWidget


class MainWindow(QMainWindow):
    """Primary application window shown after successful login."""

    PAGE_DASHBOARD = 0
    PAGE_BLOOD     = 1
    PAGE_DOCTORS   = 2
    PAGE_TESTS     = 3
    PAGE_PROFILE   = 4

    def __init__(self, patient: dict, login_window, parent=None):
        super().__init__(parent)
        self.patient      = patient
        self.login_window = login_window
        self.pat_id       = patient.get('PatID')
        self.pat_name     = patient.get('PatName', 'Patient')
        self._login_time  = datetime.now().strftime('%d-%b-%Y %H:%M')

        self.setWindowTitle(
            f"MEDORA - Medical Electronic Data & Online Records Analysis - [{self.pat_name}]"
        )
        self.setWindowIcon(icon_medora())
        self.setMinimumSize(1150, 750)
        self.setStyleSheet(XP_STYLE)

        self._build_menubar()
        self._build_toolbar()
        self._build_ui()
        self._build_statusbar()
        self._navigate(self.PAGE_DASHBOARD)

    # ── Menu Bar ─────────────────────────────────────────────────────────────

    def _build_menubar(self):
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu("&File")
        act_logout = QAction(icon_logout(), "&Log Off", self)
        act_logout.setShortcut("Ctrl+L")
        act_logout.triggered.connect(self._on_logout)

        act_exit = QAction("E&xit", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)

        file_menu.addAction(act_logout)
        file_menu.addSeparator()
        file_menu.addAction(act_exit)

        # Edit
        edit_menu = menubar.addMenu("&Edit")
        act_add_blood = QAction(icon_blood(), "Add Blood Record...", self)
        act_add_blood.triggered.connect(lambda: self._trigger_add_blood())
        edit_menu.addAction(act_add_blood)

        # View
        view_menu = menubar.addMenu("&View")
        nav_entries = [
            ("Dashboard", icon_dashboard(), self.PAGE_DASHBOARD),
            ("Blood Results & Graph", icon_blood(), self.PAGE_BLOOD),
            ("Assigned Doctors", icon_doctor(), self.PAGE_DOCTORS),
            ("Assigned Tests", icon_tests(), self.PAGE_TESTS),
            ("Patient Profile", icon_profile(), self.PAGE_PROFILE),
        ]
        for name, ico, idx in nav_entries:
            act = QAction(ico, name, self)
            act.triggered.connect(lambda checked, i=idx: self._navigate(i))
            view_menu.addAction(act)

        # Reports
        reports_menu = menubar.addMenu("&Reports")
        act_export = QAction(icon_graph(), "Export Blood Chart (PNG)...", self)
        act_export.triggered.connect(self._export_graph)
        reports_menu.addAction(act_export)

        # Tools
        tools_menu = menubar.addMenu("&Tools")
        act_refresh = QAction(icon_refresh(), "Refresh All Records", self)
        act_refresh.setShortcut("F5")
        act_refresh.triggered.connect(self._refresh_active_page)
        tools_menu.addAction(act_refresh)

        # Help
        help_menu = menubar.addMenu("&Help")
        act_about = QAction(icon_medora(), "&About MEDORA", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    # ── Classic Windows XP Toolbar ───────────────────────────────────────────

    def _build_toolbar(self):
        tb = QToolBar("Main Operations", self)
        tb.setIconSize(QSize(16, 16))
        tb.setMovable(False)
        tb.setFloatable(False)

        def _add_btn(text, icon, callback):
            btn = QToolButton(self)
            btn.setText(text)
            btn.setIcon(icon)
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            tb.addWidget(btn)
            return btn

        _add_btn(" Dashboard", icon_dashboard(), lambda: self._navigate(self.PAGE_DASHBOARD))
        _add_btn(" Blood Results", icon_blood(), lambda: self._navigate(self.PAGE_BLOOD))
        _add_btn(" Doctors", icon_doctor(), lambda: self._navigate(self.PAGE_DOCTORS))
        _add_btn(" Tests", icon_tests(), lambda: self._navigate(self.PAGE_TESTS))
        _add_btn(" Profile", icon_profile(), lambda: self._navigate(self.PAGE_PROFILE))
        tb.addSeparator()
        _add_btn(" Export Chart", icon_graph(), self._export_graph)
        _add_btn(" Refresh (F5)", icon_refresh(), self._refresh_active_page)
        tb.addSeparator()
        _add_btn(" Log Off", icon_logout(), self._on_logout)

        self.addToolBar(tb)

    # ── Main UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Left Sidebar (Windows XP Clinic Master Style) ───────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Patient banner header
        pat_header = QLabel(
            f" Patient: {self.pat_name}\n ID: PAT-{self.pat_id:04d}"
        )
        pat_header.setFixedHeight(54)
        pat_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        pat_header.setWordWrap(True)
        pat_header.setStyleSheet(SIDEBAR_HEADER_STYLE)
        sidebar_layout.addWidget(pat_header)

        # Navigation section header
        nav_section_lbl = QLabel("  Explorer Tasks")
        nav_section_lbl.setFixedHeight(24)
        nav_section_lbl.setStyleSheet(SUBHEADER_STYLE)
        sidebar_layout.addWidget(nav_section_lbl)

        # Navigation buttons with XP pixel icons
        nav_items = [
            ("Dashboard",      icon_dashboard(), self.PAGE_DASHBOARD),
            ("Blood Results",  icon_blood(),     self.PAGE_BLOOD),
            ("My Doctors",     icon_doctor(),    self.PAGE_DOCTORS),
            ("My Tests",       icon_tests(),     self.PAGE_TESTS),
            ("My Profile",     icon_profile(),   self.PAGE_PROFILE),
        ]
        self._nav_buttons = []
        for label, icon, page_idx in nav_items:
            btn = QPushButton(f"  {label}")
            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_BUTTON_STYLE)
            btn.setFixedHeight(34)
            btn.clicked.connect(lambda checked, i=page_idx: self._navigate(i))
            sidebar_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        sidebar_layout.addSpacing(10)

        # Secondary section (Folders / Reports)
        rep_lbl = QLabel("  Reports & Tools")
        rep_lbl.setFixedHeight(24)
        rep_lbl.setStyleSheet(SUBHEADER_STYLE)
        sidebar_layout.addWidget(rep_lbl)

        btn_graph_export = QPushButton("  Save Chart (PNG)")
        btn_graph_export.setIcon(icon_graph())
        btn_graph_export.setIconSize(QSize(16, 16))
        btn_graph_export.setStyleSheet(NAV_BUTTON_STYLE)
        btn_graph_export.setFixedHeight(30)
        btn_graph_export.clicked.connect(self._export_graph)
        sidebar_layout.addWidget(btn_graph_export)

        btn_refresh = QPushButton("  Refresh Records")
        btn_refresh.setIcon(icon_refresh())
        btn_refresh.setIconSize(QSize(16, 16))
        btn_refresh.setStyleSheet(NAV_BUTTON_STYLE)
        btn_refresh.setFixedHeight(30)
        btn_refresh.clicked.connect(self._refresh_active_page)
        sidebar_layout.addWidget(btn_refresh)

        sidebar_layout.addStretch()

        # Logout button at bottom
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #ACA899;")
        sidebar_layout.addWidget(sep)

        btn_logout = QPushButton("  Log Off Patient")
        btn_logout.setIcon(icon_logout())
        btn_logout.setFixedHeight(32)
        btn_logout.setStyleSheet(LOGOUT_BUTTON_STYLE)
        btn_logout.clicked.connect(self._on_logout)
        sidebar_layout.addWidget(btn_logout)
        sidebar_layout.addSpacing(4)

        root.addWidget(sidebar)

        # Vertical separator
        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.VLine)
        v_sep.setStyleSheet("color: #716F64;")
        root.addWidget(v_sep)

        # ── Stacked content area ─────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.dash_widget   = DashboardWidget(self.patient)
        self.blood_widget  = BloodResultsWidget(self.pat_id, self.pat_name)
        self.doc_widget    = MyDoctorsWidget(self.pat_id)
        self.test_widget   = MyTestsWidget(self.pat_id)
        self.prof_widget   = ProfileWidget(self.patient)

        self.stack.addWidget(self.dash_widget)    # 0
        self.stack.addWidget(self.blood_widget)   # 1
        self.stack.addWidget(self.doc_widget)     # 2
        self.stack.addWidget(self.test_widget)    # 3
        self.stack.addWidget(self.prof_widget)    # 4
        root.addWidget(self.stack)

    # ── Status Bar with Classic Sunken Panels ────────────────────────────────

    def _build_statusbar(self):
        sb = self.statusBar()
        sb.setSizeGripEnabled(True)

        self.lbl_sb_user   = QLabel(f" User: {self.pat_name} (PAT-{self.pat_id:04d})")
        self.lbl_sb_server = QLabel(" Server: MySQL (medora_db)")
        self.lbl_sb_time   = QLabel(f" Login: {self._login_time}")
        self.lbl_sb_status = QLabel(" Status: Ready")

        for lbl in (self.lbl_sb_user, self.lbl_sb_server, self.lbl_sb_time, self.lbl_sb_status):
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

        sb.addWidget(self.lbl_sb_user, 3)
        sb.addWidget(self.lbl_sb_server, 2)
        sb.addWidget(self.lbl_sb_time, 2)
        sb.addWidget(self.lbl_sb_status, 1)

    # ── Navigation ───────────────────────────────────────────────────────────

    def _navigate(self, page_idx: int):
        self.stack.setCurrentIndex(page_idx)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == page_idx)

    def _trigger_add_blood(self):
        self._navigate(self.PAGE_BLOOD)
        self.blood_widget._on_add()

    def _refresh_active_page(self):
        curr = self.stack.currentWidget()
        if hasattr(curr, 'refresh'):
            curr.refresh()
        elif hasattr(curr, '_load_data'):
            curr._load_data()
        self.lbl_sb_status.setText(" Status: Refreshed")

    # ── Slots ────────────────────────────────────────────────────────────────

    def _on_logout(self):
        reply = QMessageBox.question(
            self, "Windows XP - Log Off",
            f"Are you sure you want to log off?\n\nPatient: {self.pat_name}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
            self.login_window.login_id_field.clear()
            self.login_window.password_field.clear()
            self.login_window.login_status.setText("")
            self.login_window.status_bar.showMessage(
                "MEDORA Health Management System | Logged off successfully."
            )
            self.login_window.show()

    def _export_graph(self):
        from PyQt5.QtWidgets import QFileDialog
        if not hasattr(self.blood_widget, 'fig'):
            QMessageBox.information(
                self, "Export Graph",
                "Navigate to Blood Results first to view the chart."
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Blood Count History Chart",
            f"MEDORA_{self.pat_name.replace(' ', '_')}_blood_graph.png",
            "PNG Image (*.png);;Bitmap Image (*.bmp);;All Files (*)"
        )
        if path:
            self.blood_widget.fig.savefig(path, dpi=150, bbox_inches='tight')
            QMessageBox.information(
                self, "Chart Exported",
                f"The blood count graph has been saved to:\n\n{path}"
            )

    def _show_about(self):
        QMessageBox.about(
            self, "About MEDORA",
            "<b>Project MEDORA</b><br>"
            "Medical Electronic Data &amp; Online Records Analysis<br><br>"
            "Windows XP Clinic Master Edition<br>"
            "Version 1.1<br><br>"
            "Full patient health management system with real-time Matplotlib charts,<br>"
            "MySQL backend, and complete records tracking.<br><br>"
            "<i>Built with PyQt5, mysql-connector-python, Matplotlib</i>"
        )
