# dashboard.py - Dashboard widget for Project MEDORA (Windows XP style)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from db_setup import get_connection
from styles import SECTION_HEADER_STYLE, SUBHEADER_STYLE
from xp_icons import icon_blood, icon_doctor, icon_tests, icon_document

NORMAL_RANGES = {
    'RBC':         (4.5, 5.9),
    'WBC':         (4.5, 11.0),
    'Haemoglobin': (12.0, 17.0),
}


class SummaryCard(QFrame):
    """Windows XP style raised-border vitals summary card."""

    def __init__(self, title: str, value: str, unit: str,
                 status: str = 'normal', parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.setFixedSize(185, 115)
        self.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border-top: 1px solid #FFFFFF;
                border-left: 1px solid #FFFFFF;
                border-right: 2px solid #808080;
                border-bottom: 2px solid #808080;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(10, 8, 10, 8)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            color: #003399;
            font-weight: bold;
            font-size: 8.5pt;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        layout.addWidget(title_lbl)

        # Value
        val_color = '#CC0000' if status == 'abnormal' else '#007000'
        if status == 'nodata':
            val_color = '#808080'
        val_lbl = QLabel(value)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet(f"""
            color: {val_color};
            font-weight: bold;
            font-size: 19pt;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        layout.addWidget(val_lbl)

        # Unit
        unit_lbl = QLabel(unit)
        unit_lbl.setAlignment(Qt.AlignCenter)
        unit_lbl.setStyleSheet("""
            color: #444444;
            font-size: 8pt;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        layout.addWidget(unit_lbl)

        # Status text
        status_text = "[ NORMAL ]" if status == 'normal' else ("[ ABNORMAL ]" if status == 'abnormal' else "[ NO RECORD ]")
        status_color = "#008000" if status == 'normal' else ("#CC0000" if status == 'abnormal' else "#808080")
        badge = QLabel(status_text)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            color: {status_color};
            font-size: 7.5pt;
            font-weight: bold;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        layout.addWidget(badge)


class CountCard(QFrame):
    """Windows XP summary count card."""

    def __init__(self, title: str, value: str, subtext: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.setFixedSize(185, 115)
        self.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border-top: 1px solid #FFFFFF;
                border-left: 1px solid #FFFFFF;
                border-right: 2px solid #808080;
                border-bottom: 2px solid #808080;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(10, 8, 10, 8)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            color: #003399;
            font-weight: bold;
            font-size: 8.5pt;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        layout.addWidget(title_lbl)

        val_lbl = QLabel(value)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet("""
            color: #003399;
            font-weight: bold;
            font-size: 22pt;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        layout.addWidget(val_lbl)

        sub_lbl = QLabel(subtext)
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet("""
            color: #555555;
            font-size: 8pt;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        layout.addWidget(sub_lbl)


class DashboardWidget(QWidget):
    """Main patient dashboard."""

    def __init__(self, patient: dict, parent=None):
        super().__init__(parent)
        self.patient = patient
        self.pat_id  = patient.get('PatID')
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        hdr = QLabel("  Patient Health Dashboard")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setStyleSheet("background: #ECE9D8;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(16)
        self.content_layout.setContentsMargins(16, 16, 16, 16)

        # Welcome panel
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EDF3FC, stop:1 #D7E5F9);
                border-top: 1px solid #FFFFFF;
                border-left: 1px solid #FFFFFF;
                border-right: 1px solid #999587;
                border-bottom: 1px solid #999587;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setContentsMargins(14, 10, 14, 10)

        welcome_lbl = QLabel(f"Welcome, {self.patient.get('PatName', 'Patient')}!")
        welcome_lbl.setStyleSheet("""
            color: #003399;
            font-size: 15pt;
            font-weight: bold;
            font-family: Tahoma, Arial;
            background: transparent;
        """)

        sub_lbl = QLabel(
            f"Patient ID: PAT-{self.pat_id:04d}   |   "
            f"Age: {self.patient.get('Age', 'N/A')} yrs   |   "
            f"Weight: {self.patient.get('Weight', 'N/A')} kg   |   "
            f"DOB: {self.patient.get('DOB', 'N/A')}"
        )
        sub_lbl.setStyleSheet(
            "color: #333333; font-family: Tahoma, Arial; font-size: 9pt; background: transparent;"
        )

        welcome_layout.addWidget(welcome_lbl)
        welcome_layout.addWidget(sub_lbl)
        self.content_layout.addWidget(welcome_frame)

        # Section: Latest Blood Test Results
        blood_hdr = QLabel("  Latest Blood Test Vitals")
        blood_hdr.setFixedHeight(22)
        blood_hdr.setStyleSheet(SUBHEADER_STYLE)
        self.content_layout.addWidget(blood_hdr)

        self.blood_row = QHBoxLayout()
        self.blood_row.setSpacing(12)
        self.blood_row.setAlignment(Qt.AlignLeft)
        self.content_layout.addLayout(self.blood_row)

        # Section: Clinical Overview
        act_hdr = QLabel("  Clinical Overview & Activity")
        act_hdr.setFixedHeight(22)
        act_hdr.setStyleSheet(SUBHEADER_STYLE)
        self.content_layout.addWidget(act_hdr)

        self.act_row = QHBoxLayout()
        self.act_row.setSpacing(12)
        self.act_row.setAlignment(Qt.AlignLeft)
        self.content_layout.addLayout(self.act_row)

        # System Note Box
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            QFrame {
                background: #FFFFE1;
                border: 1px solid #ACA899;
            }
        """)
        note_layout = QVBoxLayout(note_frame)
        note_layout.setContentsMargins(12, 8, 12, 8)
        note_lbl = QLabel(
            "System Notice: Blood test counts can be added and edited from the "
            "Blood Results section. The blood history graph updates automatically in real-time."
        )
        note_lbl.setStyleSheet("color: #333333; font-size: 8.5pt; font-family: Tahoma, Arial; background: transparent;")
        note_layout.addWidget(note_lbl)
        self.content_layout.addWidget(note_frame)

        self.content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def refresh(self):
        """Update dashboard vitals cards and activity counts."""
        # 1. Clear previous cards in blood_row
        while self.blood_row.count():
            item = self.blood_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 2. Re-fetch latest blood record
        latest = self._fetch_latest_blood()
        if latest:
            for param, lo, hi, unit in [
                ('RBC',         4.5, 5.9,  'M/mcL'),
                ('WBC',         4.5, 11.0, 'K/mcL'),
                ('Haemoglobin', 12.0,17.0, 'g/dL'),
            ]:
                val = latest.get(param)
                if val is not None:
                    fval   = float(val)
                    status = 'normal' if lo <= fval <= hi else 'abnormal'
                    card   = SummaryCard(f"{param} Level", f"{fval:.2f}", unit, status)
                    card.setToolTip(
                        f"Parameter: {param}\n"
                        f"Recorded Value: {fval:.2f} {unit}\n"
                        f"Clinical Status: {'NORMAL (In Range)' if status == 'normal' else 'ABNORMAL (Out of Range)'}\n"
                        f"Standard Reference Range: {lo:.1f} – {hi:.1f} {unit}"
                    )
                else:
                    card = SummaryCard(f"{param} Level", "--", unit, 'nodata')
                    card.setToolTip(
                        f"Parameter: {param}\n"
                        f"No reading recorded\n"
                        f"Standard Reference Range: {lo:.1f} – {hi:.1f} {unit}"
                    )
                self.blood_row.addWidget(card)

            date_lbl = QLabel(f"Record Date: {latest.get('TestDate', 'N/A')}")
            date_lbl.setStyleSheet(
                "color: #444444; font-family: Tahoma, Arial; font-size: 8.5pt; background: transparent;"
            )
            self.blood_row.addWidget(date_lbl, alignment=Qt.AlignBottom)
        else:
            no_blood = QLabel("No blood test records on file. Use the Blood Results page to add counts.")
            no_blood.setStyleSheet(
                "color: #666666; font-family: Tahoma, Arial; font-size: 9pt; background: transparent;"
            )
            self.blood_row.addWidget(no_blood)

        # 3. Clear previous cards in act_row
        while self.act_row.count():
            item = self.act_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pending_count, doc_count, test_count = self._fetch_counts()
        self.act_row.addWidget(CountCard("Pending Tests", str(pending_count), "awaiting completion"))
        self.act_row.addWidget(CountCard("Assigned Doctors", str(doc_count), "specialists on file"))
        self.act_row.addWidget(CountCard("Total Tests Assigned", str(test_count), "catalog entries"))

    def _fetch_latest_blood(self):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM blood_test_results
                WHERE PatID = %s
                ORDER BY TestDate DESC, ResultID DESC
                LIMIT 1
            """, (self.pat_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row
        except Exception:
            return None

    def _fetch_counts(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM tests_assigned WHERE PatID=%s AND Status='Pending'",
                (self.pat_id,)
            )
            pending = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM patient_doctor_assignment WHERE PatID=%s",
                (self.pat_id,)
            )
            docs = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM tests_assigned WHERE PatID=%s",
                (self.pat_id,)
            )
            total = cursor.fetchone()[0]

            cursor.close()
            conn.close()
            return pending, docs, total
        except Exception:
            return 0, 0, 0
