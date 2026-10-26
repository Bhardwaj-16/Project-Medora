# blood_results.py - Blood results table + Add/Edit dialog + real-time graph

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QSplitter, QSizePolicy,
    QPushButton, QDialog, QFormLayout, QDoubleSpinBox, QDateEdit,
    QDialogButtonBox, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont, QBrush

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

from db_setup import get_connection
from styles import SECTION_HEADER_STYLE, TOOLBAR_STYLE, SUBHEADER_STYLE, BLUE_BUTTON_STYLE
from xp_icons import icon_add, icon_edit, icon_delete, icon_refresh, icon_save, icon_graph

# ── Parameter metadata, units & descriptions ─────────────────────────────────
PARAM_META = {
    'RBC': {
        'name': 'Red Blood Cell Count',
        'unit': 'M/mcL',
        'range': (4.50, 5.90),
        'color': '#CC0000',
        'desc': 'Transports oxygen to tissues throughout the body.',
    },
    'WBC': {
        'name': 'White Blood Cell Count',
        'unit': 'K/mcL',
        'range': (4.50, 11.00),
        'color': '#0000CC',
        'desc': 'Primary defense cells combating microbial infection.',
    },
    'Haemoglobin': {
        'name': 'Haemoglobin (Hb)',
        'unit': 'g/dL',
        'range': (12.00, 17.00),
        'color': '#006600',
        'desc': 'Iron-containing oxygen-transport metalloprotein in RBCs.',
    },
    'Platelets': {
        'name': 'Platelet Count',
        'unit': 'K/mcL',
        'range': (150.0, 400.0),
        'color': '#660099',
        'desc': 'Platelets (thrombocytes) essential for hemostasis & clotting.',
    },
    'TLC': {
        'name': 'Total Leukocyte Count',
        'unit': 'K/mcL',
        'range': (4.50, 11.00),
        'color': '#FF8800',
        'desc': 'Total number of circulating leukocytes per volume of blood.',
    },
    'Neutrophils': {
        'name': 'Neutrophil Percentage',
        'unit': '%',
        'range': (50.0, 70.0),
        'color': '#8B4513',
        'desc': 'Predominant granulocytes responding to bacterial infections.',
    },
    'Lymphocytes': {
        'name': 'Lymphocyte Percentage',
        'unit': '%',
        'range': (20.0, 40.0),
        'color': '#008B8B',
        'desc': 'Key immune cells regulating viral immunity and antibodies.',
    },
    'Eosinophils': {
        'name': 'Eosinophil Percentage',
        'unit': '%',
        'range': (1.0, 6.0),
        'color': '#FF1493',
        'desc': 'Elevated in parasitic conditions and allergic responses.',
    },
    'Basophils': {
        'name': 'Basophil Percentage',
        'unit': '%',
        'range': (0.0, 1.0),
        'color': '#555555',
        'desc': 'Releases histamine and heparin in inflammatory processes.',
    },
    'Monocytes': {
        'name': 'Monocyte Percentage',
        'unit': '%',
        'range': (2.0, 8.0),
        'color': '#B8860B',
        'desc': 'Mononuclear phagocytes that clear cell debris & pathogens.',
    },
}

NORMAL_RANGES = {p: PARAM_META[p]['range'] for p in PARAM_META}
PARAMS = list(PARAM_META.keys())
COLUMNS = ['Date'] + PARAMS


# ── Add/Edit Dialog ───────────────────────────────────────────────────────────

class BloodEntryDialog(QDialog):
    """Dialog for adding a new blood test entry or editing an existing one."""

    def __init__(self, pat_id: int, parent=None, existing: dict = None):
        super().__init__(parent)
        self.pat_id   = pat_id
        self.existing = existing
        self.result_id = existing.get('ResultID') if existing else None

        title = "Edit Blood Test Record" if existing else "Add New Blood Test Record"
        self.setWindowTitle(title)
        self.setFixedSize(540, 580)
        self.setModal(True)

        from styles import XP_STYLE
        self.setStyleSheet(XP_STYLE)

        self._build_ui()
        if existing:
            self._populate(existing)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header bar
        hdr = QLabel("  Blood Test Record Entry Form")
        hdr.setFixedHeight(34)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("background: #ECE9D8;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(18, 12, 18, 8)
        form_layout.setSpacing(4)

        form = QFormLayout()
        form.setSpacing(6)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        self.date_edit.setToolTip("Select the date when the blood sample was collected")
        form.addRow("Test Date:", self.date_edit)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #ACA899; margin: 4px 0;")
        form_layout.addLayout(form)
        form_layout.addWidget(sep)

        # Parameters form
        param_form = QFormLayout()
        param_form.setSpacing(5)
        param_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.spins = {}
        ranges_cfg = {
            'RBC':         (0.0, 20.0,   2, 0.1),
            'WBC':         (0.0, 50.0,   2, 0.1),
            'Haemoglobin': (0.0, 25.0,   1, 0.1),
            'Platelets':   (0.0, 1000.0, 1, 1.0),
            'TLC':         (0.0, 50.0,   2, 0.1),
            'Neutrophils': (0.0, 100.0,  1, 0.5),
            'Lymphocytes': (0.0, 100.0,  1, 0.5),
            'Eosinophils': (0.0, 50.0,   1, 0.1),
            'Basophils':   (0.0, 10.0,   2, 0.1),
            'Monocytes':   (0.0, 30.0,   1, 0.5),
        }

        for param in PARAMS:
            meta = PARAM_META[param]
            lo, hi = meta['range']
            min_v, max_v, dec, step = ranges_cfg[param]
            unit = meta['unit']
            ref_text = f"Ref: {lo:.1f} – {hi:.1f} {unit}"

            spin = QDoubleSpinBox()
            spin.setRange(min_v, max_v)
            spin.setDecimals(dec)
            spin.setSingleStep(step)
            spin.setValue(0.0)
            spin.setFixedWidth(110)

            tooltip_text = (
                f"{meta['name']}\n"
                f"Normal Reference Range: {lo:.2f} – {hi:.2f} {unit}\n"
                f"{meta['desc']}"
            )
            spin.setToolTip(tooltip_text)

            row_box = QHBoxLayout()
            row_box.setSpacing(10)
            row_box.addWidget(spin)

            ref_lbl = QLabel(ref_text)
            ref_lbl.setStyleSheet("""
                color: #2B579A;
                font-size: 8.5pt;
                font-family: Tahoma, Arial;
                font-weight: bold;
                background: transparent;
            """)
            ref_lbl.setToolTip(tooltip_text)
            row_box.addWidget(ref_lbl)
            row_box.addStretch()

            lbl = QLabel(f"{param}:")
            lbl.setToolTip(tooltip_text)
            param_form.addRow(lbl, row_box)

            self.spins[param] = spin

        form_layout.addLayout(param_form)

        # Help note
        note = QLabel("Tip: Normal clinical reference ranges are shown beside each field and on hover.")
        note.setStyleSheet(
            "color: #444444; font-size: 8pt; font-family: Tahoma, Arial; "
            "background: transparent; padding: 4px 0;"
        )
        form_layout.addWidget(note)
        layout.addWidget(form_container)

        # Button bar
        btn_bar = QWidget()
        btn_bar.setFixedHeight(44)
        btn_bar.setStyleSheet(TOOLBAR_STYLE)
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(10, 6, 10, 6)
        btn_layout.setSpacing(8)
        btn_layout.addStretch()

        self.btn_save = QPushButton("  Save Record")
        self.btn_save.setIcon(icon_save())
        self.btn_save.setStyleSheet(BLUE_BUTTON_STYLE)
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._on_save)

        btn_cancel = QPushButton("  Cancel")
        btn_cancel.setIcon(icon_delete())
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addWidget(btn_bar)

    def _populate(self, data: dict):
        if data.get('TestDate'):
            d = data['TestDate']
            if isinstance(d, str):
                d = datetime.strptime(d, '%Y-%m-%d').date()
            self.date_edit.setDate(QDate(d.year, d.month, d.day))
        for param in PARAMS:
            val = data.get(param)
            if val is not None:
                self.spins[param].setValue(float(val))

    def _on_save(self):
        qdate = self.date_edit.date()
        test_date = f"{qdate.year():04d}-{qdate.month():02d}-{qdate.day():02d}"
        values = {p: self.spins[p].value() for p in PARAMS}

        try:
            conn = get_connection()
            cursor = conn.cursor()
            if self.result_id:
                cursor.execute("""
                    UPDATE blood_test_results SET
                        TestDate=%s, RBC=%s, WBC=%s, Haemoglobin=%s,
                        Platelets=%s, TLC=%s, Neutrophils=%s,
                        Lymphocytes=%s, Eosinophils=%s, Basophils=%s, Monocytes=%s
                    WHERE ResultID=%s AND PatID=%s
                """, (
                    test_date,
                    values['RBC'], values['WBC'], values['Haemoglobin'],
                    values['Platelets'], values['TLC'], values['Neutrophils'],
                    values['Lymphocytes'], values['Eosinophils'],
                    values['Basophils'], values['Monocytes'],
                    self.result_id, self.pat_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO blood_test_results
                        (PatID, TestDate, RBC, WBC, Haemoglobin, Platelets,
                         TLC, Neutrophils, Lymphocytes, Eosinophils, Basophils, Monocytes)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    self.pat_id, test_date,
                    values['RBC'], values['WBC'], values['Haemoglobin'],
                    values['Platelets'], values['TLC'], values['Neutrophils'],
                    values['Lymphocytes'], values['Eosinophils'],
                    values['Basophils'], values['Monocytes'],
                ))
            conn.commit()
            cursor.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save record:\n\n{e}")


# ── Main Blood Results Widget ─────────────────────────────────────────────────

class BloodResultsWidget(QWidget):
    """Displays blood test history table, Add/Edit/Delete toolbar, and graph."""

    def __init__(self, pat_id: int, pat_name: str, parent=None):
        super().__init__(parent)
        self.pat_id   = pat_id
        self.pat_name = pat_name
        self._rows    = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Section header
        hdr = QLabel("  Blood Test History & Laboratory Analysis")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(SECTION_HEADER_STYLE)
        layout.addWidget(hdr)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(38)
        toolbar.setStyleSheet(TOOLBAR_STYLE)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(6, 4, 6, 4)
        tb.setSpacing(4)

        self.btn_add = QPushButton(" Add Record")
        self.btn_add.setIcon(icon_add())
        self.btn_add.setStyleSheet(BLUE_BUTTON_STYLE)
        self.btn_add.setToolTip("Record a new set of blood test results into database")
        self.btn_add.clicked.connect(self._on_add)

        self.btn_edit = QPushButton(" Edit")
        self.btn_edit.setIcon(icon_edit())
        self.btn_edit.setEnabled(False)
        self.btn_edit.setToolTip("Edit the values of the currently selected record")
        self.btn_edit.clicked.connect(self._on_edit)

        self.btn_del = QPushButton(" Delete")
        self.btn_del.setIcon(icon_delete())
        self.btn_del.setEnabled(False)
        self.btn_del.setToolTip("Delete the selected record permanently from database")
        self.btn_del.clicked.connect(self._on_delete)

        btn_refresh = QPushButton(" Refresh")
        btn_refresh.setIcon(icon_refresh())
        btn_refresh.setToolTip("Reload blood test data and recalculate chart")
        btn_refresh.clicked.connect(self.refresh)

        tb.addWidget(self.btn_add)
        tb.addWidget(self.btn_edit)
        tb.addWidget(self.btn_del)
        tb.addStretch()
        tb.addWidget(btn_refresh)
        layout.addWidget(toolbar)

        # Splitter: table top / graph bottom
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(5)

        # Table panel
        table_frame = QWidget()
        table_frame.setStyleSheet("background: #ECE9D8;")
        tfl = QVBoxLayout(table_frame)
        tfl.setContentsMargins(6, 6, 6, 3)
        tfl.setSpacing(3)

        tbl_hdr = QLabel("  Blood Count Records  (Hover over any column or cell to view clinical reference ranges)")
        tbl_hdr.setFixedHeight(22)
        tbl_hdr.setStyleSheet(SUBHEADER_STYLE)
        tfl.addWidget(tbl_hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSortingEnabled(False)

        # Set helpful reference tooltips on column headers
        header_date = self.table.horizontalHeaderItem(0)
        if header_date:
            header_date.setToolTip("Collection Date when the sample was drawn and analyzed")

        for idx, param in enumerate(PARAMS, start=1):
            h_item = self.table.horizontalHeaderItem(idx)
            if h_item:
                meta = PARAM_META[param]
                lo, hi = meta['range']
                unit = meta['unit']
                h_item.setToolTip(
                    f"Parameter: {meta['name']}\n"
                    f"Normal Clinical Reference: {lo:.2f} – {hi:.2f} {unit}\n"
                    f"{meta['desc']}"
                )

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, len(COLUMNS)):
            hh.setSectionResizeMode(i, QHeaderView.Stretch)

        self.table.setMinimumHeight(140)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        tfl.addWidget(self.table)

        self.no_data_lbl = QLabel("No blood test records found. Click 'Add Record' to add your first entry.")
        self.no_data_lbl.setAlignment(Qt.AlignCenter)
        self.no_data_lbl.setStyleSheet(
            "color: #666666; font-family: Tahoma, Arial; font-size: 9pt; background: transparent;"
        )
        self.no_data_lbl.hide()
        tfl.addWidget(self.no_data_lbl)

        splitter.addWidget(table_frame)

        # Graph panel
        graph_frame = QWidget()
        graph_frame.setStyleSheet("background: #ECE9D8;")
        gfl = QVBoxLayout(graph_frame)
        gfl.setContentsMargins(6, 3, 6, 6)
        gfl.setSpacing(3)

        graph_hdr = QLabel("  All-Time Blood Count Progress Chart")
        graph_hdr.setFixedHeight(22)
        graph_hdr.setStyleSheet(SUBHEADER_STYLE)
        gfl.addWidget(graph_hdr)

        self.fig = Figure(figsize=(10, 4), dpi=96, facecolor='#FAFAFA')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gfl.addWidget(self.canvas)

        self.no_graph_lbl = QLabel("No data available to plot.")
        self.no_graph_lbl.setAlignment(Qt.AlignCenter)
        self.no_graph_lbl.setStyleSheet(
            "color: #666666; font-family: Tahoma, Arial; font-size: 9pt; background: transparent;"
        )
        self.no_graph_lbl.hide()
        gfl.addWidget(self.no_graph_lbl)

        splitter.addWidget(graph_frame)
        splitter.setSizes([220, 380])
        layout.addWidget(splitter)

    # ── Data Load / Refresh ───────────────────────────────────────────────────

    def refresh(self):
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM blood_test_results WHERE PatID=%s ORDER BY TestDate ASC",
                (self.pat_id,)
            )
            self._rows = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Could not load records:\n{e}")
            self._rows = []

        self._populate_table()
        self._draw_graph()
        self._on_selection_changed()

    def _populate_table(self):
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(0)

        if not self._rows:
            self.table.hide()
            self.no_data_lbl.show()
            return

        self.no_data_lbl.hide()
        self.table.show()
        self.table.setRowCount(len(self._rows))

        BLACK   = QColor('#000000')
        ALT_BG  = QColor('#EDF3FB')
        WHITE   = QColor('#FFFFFF')
        OOR_BG  = QColor('#FFE8E8')
        OOR_FG  = QColor('#AA0000')

        for r_idx, row in enumerate(self._rows):
            alt = (r_idx % 2 == 1)
            row_bg = ALT_BG if alt else WHITE
            t_date = str(row['TestDate'])

            # Date cell with tooltip
            date_item = QTableWidgetItem(t_date)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setForeground(QBrush(BLACK))
            date_item.setBackground(QBrush(row_bg))
            date_item.setData(Qt.UserRole, row.get('ResultID'))
            date_item.setToolTip(f"Sample Collection Date: {t_date}\nClick this row to select, edit or delete.")
            self.table.setItem(r_idx, 0, date_item)

            for c_idx, param in enumerate(PARAMS, start=1):
                val = row.get(param)
                meta = PARAM_META[param]
                lo, hi = meta['range']
                unit = meta['unit']

                val_str = f"{float(val):.2f}" if val is not None else "—"
                item = QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignCenter)

                oor = False
                if val is not None:
                    fval = float(val)
                    if fval < lo or fval > hi:
                        oor = True

                    if fval < lo:
                        eval_text = f"ABNORMAL (LOW) - Below clinical minimum {lo:.2f} {unit}"
                    elif fval > hi:
                        eval_text = f"ABNORMAL (HIGH) - Exceeds clinical maximum {hi:.2f} {unit}"
                    else:
                        eval_text = "NORMAL - Within standard clinical range"

                    cell_tooltip = (
                        f"Parameter: {meta['name']}\n"
                        f"Sample Date: {t_date}\n"
                        f"Recorded Value: {fval:.2f} {unit}\n"
                        f"Clinical Status: {eval_text}\n"
                        f"Reference Range: {lo:.2f} – {hi:.2f} {unit}\n"
                        f"Function: {meta['desc']}"
                    )
                else:
                    cell_tooltip = (
                        f"Parameter: {meta['name']}\n"
                        f"No reading recorded for {t_date}\n"
                        f"Reference Range: {lo:.2f} – {hi:.2f} {unit}"
                    )

                item.setToolTip(cell_tooltip)

                if oor:
                    item.setBackground(QBrush(OOR_BG))
                    item.setForeground(QBrush(OOR_FG))
                else:
                    item.setBackground(QBrush(row_bg))
                    item.setForeground(QBrush(BLACK))

                self.table.setItem(r_idx, c_idx, item)

            self.table.setRowHeight(r_idx, 23)

        self.table.setSortingEnabled(False)

    def _draw_graph(self):
        self.fig.clear()
        if not self._rows:
            self.canvas.hide()
            self.no_graph_lbl.show()
            return

        self.no_graph_lbl.hide()
        self.canvas.show()

        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#FFFFFF')

        dates = []
        for row in self._rows:
            d = row['TestDate']
            if isinstance(d, str):
                d = datetime.strptime(d, '%Y-%m-%d').date()
            dates.append(d)

        for param in PARAMS:
            meta = PARAM_META[param]
            color = meta['color']
            label = f"{param} ({meta['unit']})"

            values = [
                float(row[param]) if row.get(param) is not None else None
                for row in self._rows
            ]
            plot_dates = [d for d, v in zip(dates, values) if v is not None]
            plot_vals  = [v for v in values if v is not None]
            if plot_dates:
                ax.plot(
                    plot_dates, plot_vals,
                    color=color, marker='o', markersize=5,
                    linewidth=1.8, label=label, zorder=3
                )

        ax.set_title(
            f"Blood Count Progress History \u2014 {self.pat_name}",
            fontsize=10, fontweight='bold', color='#003399', pad=8
        )
        ax.set_xlabel("Sample Date", fontsize=8, color='#333333')
        ax.set_ylabel("Value (see legend for units)", fontsize=8, color='#333333')
        ax.grid(True, linestyle='--', alpha=0.4, color='#C8C8C8', zorder=0)
        ax.tick_params(labelsize=8)

        if len(dates) > 1:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.fig.autofmt_xdate(rotation=30, ha='right')

        ax.legend(
            loc='upper left', bbox_to_anchor=(1.01, 1.0),
            fontsize=7, frameon=True, framealpha=0.9,
            edgecolor='#808080'
        )
        self.fig.subplots_adjust(right=0.72, bottom=0.18, top=0.90, left=0.08)
        self.canvas.draw()

    # ── Selection ─────────────────────────────────────────────────────────────

    def _on_selection_changed(self):
        has_sel = bool(self.table.selectedItems()) and bool(self._rows)
        self.btn_edit.setEnabled(has_sel)
        self.btn_del.setEnabled(has_sel)

    def _selected_row_data(self):
        rows = self.table.selectedItems()
        if not rows:
            return None
        r_idx = self.table.currentRow()
        if r_idx < 0 or r_idx >= len(self._rows):
            return None
        return self._rows[r_idx]

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_add(self):
        dlg = BloodEntryDialog(self.pat_id, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()

    def _on_edit(self):
        data = self._selected_row_data()
        if not data:
            return
        dlg = BloodEntryDialog(self.pat_id, parent=self, existing=data)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()

    def _on_delete(self):
        data = self._selected_row_data()
        if not data:
            return
        rid = data.get('ResultID')
        date_str = str(data.get('TestDate', ''))
        reply = QMessageBox.question(
            self, "Confirm Record Deletion",
            f"Are you sure you want to delete the blood test record for {date_str}?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM blood_test_results WHERE ResultID=%s AND PatID=%s",
                (rid, self.pat_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Delete Error", f"Could not delete record:\n{e}")
