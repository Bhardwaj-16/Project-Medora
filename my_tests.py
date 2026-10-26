# my_tests.py - Assigned tests widget for Project MEDORA (Windows XP style)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QHBoxLayout, QPushButton, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QBrush

from db_setup import get_connection
from styles import SECTION_HEADER_STYLE, TOOLBAR_STYLE, SUBHEADER_STYLE
from xp_icons import icon_tests, icon_refresh

STATUS_COLORS = {
    'Pending':   (QColor('#7B5800'), QColor('#FFF8D8')),
    'Completed': (QColor('#006000'), QColor('#E2F4E2')),
    'Cancelled': (QColor('#880000'), QColor('#FCE2E2')),
}

STATUS_DESCS = {
    'Pending':   'Awaiting clinical sample collection or lab processing',
    'Completed': 'Laboratory test performed and results finalized',
    'Cancelled': 'Order discontinued by attending physician',
}


class MyTestsWidget(QWidget):
    """Shows lab & diagnostics tests assigned to the current patient."""

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
        hdr = QLabel("  Assigned Diagnostic & Clinical Tests")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(36)
        toolbar.setStyleSheet(TOOLBAR_STYLE)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 3, 8, 3)

        self.count_lbl = QLabel("Loading tests...")
        self.count_lbl.setStyleSheet(
            "font-family: Tahoma, Arial; font-size: 8.5pt; color: #333333;"
        )
        tb_layout.addWidget(self.count_lbl)
        tb_layout.addStretch()

        btn_refresh = QPushButton(" Refresh")
        btn_refresh.setIcon(icon_refresh())
        btn_refresh.setToolTip("Reload assigned tests from database")
        btn_refresh.clicked.connect(self.refresh)
        tb_layout.addWidget(btn_refresh)
        layout.addWidget(toolbar)

        # Table panel
        table_panel = QWidget()
        table_panel.setStyleSheet("background: #ECE9D8;")
        tpl = QVBoxLayout(table_panel)
        tpl.setContentsMargins(8, 8, 8, 8)
        tpl.setSpacing(4)

        tbl_hdr = QLabel("  Diagnostic Test Schedule & Status  (Hover over any test to view lab order details)")
        tbl_hdr.setFixedHeight(22)
        tbl_hdr.setStyleSheet(SUBHEADER_STYLE)
        tpl.addWidget(tbl_hdr)

        self.table = QTableWidget()
        cols = ["Item #", "Test Name", "Department / Category", "Fee (INR)", "Order Date", "Status", "Clinical Notes"]
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
            "Order line sequence number",
            "Name of diagnostic laboratory examination",
            "Pathology or clinical diagnostic department",
            "Standard clinical tariff in Indian Rupees",
            "Date when physician prescribed this test",
            "Current workflow processing status",
            "Specific physician instructions for sample or fasting",
        ]
        for col_i, tip in enumerate(header_tips):
            hi = self.table.horizontalHeaderItem(col_i)
            if hi:
                hi.setToolTip(tip)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.Stretch)

        tpl.addWidget(self.table)
        layout.addWidget(table_panel)

        # Bottom info note
        info = QLabel(
            "  Notice: For lab sample collections or appointment queries, present your Patient ID at the registration desk."
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
        """Fetch and display assigned tests for this patient."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    ta.AssignID,
                    tc.TestName,
                    tc.Category,
                    tc.Price,
                    tc.Description,
                    ta.AssignDate,
                    ta.Status,
                    ta.Notes
                FROM tests_assigned ta
                JOIN tests_catalog tc ON ta.TestID = tc.TestID
                WHERE ta.PatID = %s
                ORDER BY ta.AssignDate DESC
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
            self.table.setRowCount(1)
            msg = QTableWidgetItem("No tests have been assigned on this record.")
            msg.setForeground(QBrush(QColor('#666666')))
            msg.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, msg)
            self.table.setSpan(0, 0, 1, 7)
            self.count_lbl.setText("Total Orders: 0")
            return

        pending   = sum(1 for r in rows if r['Status'] == 'Pending')
        completed = sum(1 for r in rows if r['Status'] == 'Completed')
        cancelled = sum(1 for r in rows if r['Status'] == 'Cancelled')
        self.count_lbl.setText(
            f"Total Orders: {len(rows)}  |  Pending: {pending}  |  Completed: {completed}  |  Cancelled: {cancelled}"
        )

        self.table.setRowCount(len(rows))
        BLACK  = QColor('#000000')
        WHITE  = QColor('#FFFFFF')
        ALT_BG = QColor('#F1F6FC')

        for r_idx, row in enumerate(rows):
            alt = (r_idx % 2 == 1)
            bg = ALT_BG if alt else WHITE
            status = row.get('Status', 'Pending') or 'Pending'

            fg_stat, bg_stat = STATUS_COLORS.get(status, (BLACK, bg))

            def _make_item(text, align=Qt.AlignLeft, color=BLACK, bold=False, cell_bg=bg, tip=""):
                itm = QTableWidgetItem(str(text) if text is not None else "--")
                itm.setTextAlignment(align | Qt.AlignVCenter)
                itm.setForeground(QBrush(color))
                itm.setBackground(QBrush(cell_bg))
                if bold:
                    f = QFont("Tahoma", 9)
                    f.setBold(True)
                    itm.setFont(f)
                if tip:
                    itm.setToolTip(tip)
                return itm

            price_str = f"{float(row['Price']):.2f}" if row.get('Price') is not None else "--"
            date_str  = str(row['AssignDate']) if row.get('AssignDate') else "--"
            notes_str = row['Notes'] if row.get('Notes') else "Standard procedure"
            desc_str  = row.get('Description', 'Diagnostic lab panel')
            stat_desc = STATUS_DESCS.get(status, '')

            test_tip = (
                f"Test: {row['TestName']}\n"
                f"Department: {row['Category']}\n"
                f"Clinical Purpose: {desc_str}\n"
                f"Standard Fee: INR {price_str}\n"
                f"Order Date: {date_str}\n"
                f"Current Status: {status} ({stat_desc})"
            )

            self.table.setItem(r_idx, 0, _make_item(r_idx + 1, Qt.AlignCenter, tip=f"Order Line #{r_idx+1}"))
            self.table.setItem(r_idx, 1, _make_item(row['TestName'], Qt.AlignLeft, QColor('#003399'), bold=True, tip=test_tip))
            self.table.setItem(r_idx, 2, _make_item(row['Category'], Qt.AlignLeft, tip=f"Department: {row['Category']}"))
            self.table.setItem(r_idx, 3, _make_item(price_str, Qt.AlignRight, tip=f"Tariff: INR {price_str}"))
            self.table.setItem(r_idx, 4, _make_item(date_str, Qt.AlignCenter, tip=f"Prescribed on: {date_str}"))
            self.table.setItem(r_idx, 5, _make_item(f" {status} ", Qt.AlignCenter, fg_stat, bold=True, cell_bg=bg_stat, tip=f"Status: {status}\n{stat_desc}"))
            self.table.setItem(r_idx, 6, _make_item(notes_str, Qt.AlignLeft, tip=f"Instructions: {notes_str}"))
            self.table.setRowHeight(r_idx, 23)
