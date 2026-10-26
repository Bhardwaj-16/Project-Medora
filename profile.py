# profile.py - Patient profile view widget for Project MEDORA (Windows XP style)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from styles import SECTION_HEADER_STYLE, SUBHEADER_STYLE


class ProfileWidget(QWidget):
    """Read-only view of the logged-in patient's record."""

    def __init__(self, patient: dict, parent=None):
        super().__init__(parent)
        self.patient = patient
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        hdr = QLabel("  Patient Master Profile & Registration Details")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setStyleSheet("background: #ECE9D8;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(14)
        content_layout.setContentsMargins(18, 16, 18, 18)

        # Patient Header Banner
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EDF3FC, stop:1 #D7E5F9);
                border-top: 1px solid #FFFFFF;
                border-left: 1px solid #FFFFFF;
                border-right: 1px solid #999587;
                border-bottom: 1px solid #999587;
            }
        """)
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(14, 10, 14, 10)

        name_lbl = QLabel(self.patient.get('PatName', 'Patient Record'))
        name_lbl.setStyleSheet("""
            color: #003399;
            font-size: 15pt;
            font-weight: bold;
            font-family: Tahoma, Arial;
            background: transparent;
        """)
        b_layout.addWidget(name_lbl)

        pat_id = self.patient.get('PatID', 'N/A')
        id_str = f"PAT-{pat_id:04d}" if isinstance(pat_id, int) else str(pat_id)
        id_lbl = QLabel(f"Registration Record ID: {id_str}   |   Status: Active Patient")
        id_lbl.setStyleSheet("color: #444444; font-family: Tahoma, Arial; font-size: 9pt; background: transparent;")
        b_layout.addWidget(id_lbl)

        content_layout.addWidget(banner)

        # Personal Information
        personal_group = self._make_group("Personal Demographics", [
            ("Legal Full Name",   self.patient.get('PatName', 'N/A')),
            ("Age",               f"{self.patient.get('Age', 'N/A')} Years" if self.patient.get('Age') else 'N/A'),
            ("Date of Birth",     str(self.patient.get('DOB', 'N/A'))),
            ("Registered Weight", f"{self.patient.get('Weight', 'N/A')} kg" if self.patient.get('Weight') else 'N/A'),
        ])
        content_layout.addWidget(personal_group)

        # Contact & Residence
        contact_group = self._make_group("Contact & Residence Details", [
            ("Mobile Contact",    self.patient.get('MobileNumber', 'N/A')),
            ("Residential Address", self.patient.get('Address', 'N/A')),
        ])
        content_layout.addWidget(contact_group)

        # Account Credentials
        account_group = self._make_group("Access & Security Information", [
            ("Portal Login ID",   self.patient.get('LoginID', 'N/A')),
            ("Password Status",   "Encrypted (SHA-256 Digest Active)"),
            ("Access Level",      "Patient Portal / Read-Write Blood Log"),
        ])
        content_layout.addWidget(account_group)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _make_group(self, title: str, fields: list) -> QGroupBox:
        group = QGroupBox(f"  {title}  ")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #999587;
                margin-top: 10px;
                font-family: Tahoma, Arial;
                font-size: 9pt;
                font-weight: bold;
                background-color: #FFFFFF;
                color: #003399;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: -2px;
                padding: 0 4px;
                background-color: #FFFFFF;
                color: #003399;
            }
        """)
        grid = QGridLayout(group)
        grid.setSpacing(8)
        grid.setContentsMargins(14, 14, 14, 12)
        grid.setColumnStretch(1, 1)

        for row, (label, value) in enumerate(fields):
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(
                "font-weight: bold; font-family: Tahoma, Arial; "
                "font-size: 9pt; color: #444444; background: transparent;"
            )
            lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)

            val = QLabel(str(value))
            val.setWordWrap(True)
            val.setStyleSheet(
                "font-family: Tahoma, Arial; font-size: 9pt; "
                "color: #000000; background: transparent;"
            )
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)

            grid.addWidget(lbl, row, 0)
            grid.addWidget(val, row, 1)

        return group
