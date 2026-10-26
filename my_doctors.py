# my_doctors.py - Assigned doctors widget for Project MEDORA (Windows XP style)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QHBoxLayout, QPushButton, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QBrush

from db_setup import get_connection
from styles import SECTION_HEADER_STYLE, TOOLBAR_STYLE, SUBHEADER_STYLE
from xp_icons import icon_doctor, icon_refresh


class MyDoctorsWidget(QWidget):
    """Shows doctors assigned to the current patient."""

    def __init__(self, pat_id: int, parent=None):
        super().__init__(parent)
        self.pat_id = pat_id
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Section header
        hdr = QLabel("  Assigned Doctors Catalog")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(36)
        toolbar.setStyleSheet(TOOLBAR_STYLE)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 3, 8, 3)

        self.count_lbl = QLabel("Loading assigned medical staff...")
        self.count_lbl.setStyleSheet(
            "font-family: Tahoma, Arial; font-size: 8.5pt; color: #333333;"
        )
        tb_layout.addWidget(self.count_lbl)
        tb_layout.addStretch()

        btn_refresh = QPushButton(" Refresh")
        btn_refresh.setIcon(icon_refresh())
        btn_refresh.setToolTip("Reload assigned doctors from database")
        btn_refresh.clicked.connect(self.refresh)
        tb_layout.addWidget(btn_refresh)
        layout.addWidget(toolbar)

        # Table panel
        table_panel = QWidget()
        table_panel.setStyleSheet("background: #ECE9D8;")
        tpl = QVBoxLayout(table_panel)
        tpl.setContentsMargins(8, 8, 8, 8)
        tpl.setSpacing(4)

        tbl_hdr = QLabel("  Consulting Physicians and Specialists  (Hover over any doctor to see clinical details)")
        tbl_hdr.setFixedHeight(22)
        tbl_hdr.setStyleSheet(SUBHEADER_STYLE)
        tpl.addWidget(tbl_hdr)

        self.table = QTableWidget()
        cols = ["Doctor Name", "Speciality", "Experience", "Qualification", "Contact Number", "Assigned Date"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSortingEnabled(False)

        # Header tooltips
        header_tips = [
            "Name of attending medical doctor or surgeon",
            "Medical field / clinical specialty",
            "Total verified clinical practice experience",
            "Medical academic degrees & certifications",
            "Clinic department direct contact line",
            "Date when physician was assigned to your case",
        ]
        for col_i, tip in enumerate(header_tips):
            hi = self.table.horizontalHeaderItem(col_i)
            if hi:
                hi.setToolTip(tip)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        tpl.addWidget(self.table)
        layout.addWidget(table_panel)

        # Status note bar
        info = QLabel(
            "  Notice: Medical consultations and referrals are managed through the central clinic administration."
        )
        info.setFixedHeight(26)
        info.setStyleSheet("""
            background: #F0EDE0;
            border-top: 1px solid #ACA899;
            font-family: Tahoma, Arial;
            font-size: 8.5pt;
            color: #444444;
        """)
        layout.addWidget(info)

    def refresh(self):
        """Fetch and display assigned doctors."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    dc.DoctorName,
                    dc.Speciality,
                    dc.YearsExperience,
                    dc.Qualification,
                    dc.ContactNumber,
                    pda.AssignDate,
                    pda.Notes
                FROM patient_doctor_assignment pda
                JOIN doctor_catalog dc ON pda.DoctorID = dc.DoctorID
                WHERE pda.PatID = %s
                ORDER BY pda.AssignDate DESC
            """, (self.pat_id,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            self.count_lbl.setText(f"Error loading records: {e}")
            return

        self.table.clearContents()
        self.table.setRowCount(0)

        if not rows:
            self.count_lbl.setText("No doctors assigned at this time.")
            self.table.setRowCount(1)
            msg = QTableWidgetItem("No consulting doctors currently assigned.")
            msg.setForeground(QBrush(QColor('#666666')))
            msg.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, msg)
            self.table.setSpan(0, 0, 1, 6)
            return

        self.count_lbl.setText(f"Total Assigned Specialists: {len(rows)}")
        self.table.setRowCount(len(rows))

        BLACK   = QColor('#000000')
        DOC_CLR = QColor('#003399')
        WHITE   = QColor('#FFFFFF')
        ALT_BG  = QColor('#F1F6FC')

        for r_idx, row in enumerate(rows):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE

            def _make_item(text, align=Qt.AlignLeft, color=BLACK, bold=False, tip=""):
                itm = QTableWidgetItem(str(text) if text is not None else "--")
                itm.setTextAlignment(align | Qt.AlignVCenter)
                itm.setForeground(QBrush(color))
                itm.setBackground(QBrush(bg))
                if bold:
                    f = QFont("Tahoma", 9)
                    f.setBold(True)
                    itm.setFont(f)
                if tip:
                    itm.setToolTip(tip)
                return itm

            exp_str  = f"{row['YearsExperience']} yrs" if row.get('YearsExperience') else "--"
            date_str = str(row['AssignDate']) if row.get('AssignDate') else "--"

            doc_tip = (
                f"Physician: {row['DoctorName']}\n"
                f"Specialization: {row['Speciality']}\n"
                f"Clinical Practice: {exp_str}\n"
                f"Qualifications: {row['Qualification']}\n"
                f"Assigned Date: {date_str}"
            )

            self.table.setItem(r_idx, 0, _make_item(row['DoctorName'], Qt.AlignLeft, DOC_CLR, bold=True, tip=doc_tip))
            self.table.setItem(r_idx, 1, _make_item(row['Speciality'], Qt.AlignLeft, tip=f"Department: {row['Speciality']}"))
            self.table.setItem(r_idx, 2, _make_item(exp_str, Qt.AlignCenter, tip=f"Total Clinical Practice: {exp_str}"))
            self.table.setItem(r_idx, 3, _make_item(row['Qualification'], Qt.AlignLeft, tip=f"Degrees: {row['Qualification']}"))
            self.table.setItem(r_idx, 4, _make_item(row['ContactNumber'], Qt.AlignCenter, tip=f"Direct Contact: {row['ContactNumber']}"))
            self.table.setItem(r_idx, 5, _make_item(date_str, Qt.AlignCenter, tip=f"Assigned on: {date_str}"))
            self.table.setRowHeight(r_idx, 23)
