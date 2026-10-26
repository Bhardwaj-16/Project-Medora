# xp_icons.py - Windows XP pixel art icons drawn with QPainter
# Pixel-perfect Windows XP style icons: folders, documents, stethoscope, test tubes,
# eye, cross, graph, disks, etc.

from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPolygon, QIcon
from PyQt5.QtCore import Qt, QPoint, QRect, QRectF


def _new_pixmap(w=16, h=16):
    px = QPixmap(w, h)
    px.fill(Qt.transparent)
    return px


def icon_folder(w=16, h=16):
    """Classic Windows XP yellow folder icon."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Back tab (darker yellow)
    p.setBrush(QBrush(QColor('#D4A017')))
    p.setPen(QPen(QColor('#9E7206'), 1))
    p.drawRect(2, 3, 6, 4)
    
    # Back folder body
    p.setBrush(QBrush(QColor('#E5B824')))
    p.drawRect(2, 5, 12, 8)
    
    # White paper inside folder
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#A0A0A0'), 1))
    p.drawRect(4, 3, 7, 5)
    
    # Front folder flap (bright XP folder yellow)
    p.setBrush(QBrush(QColor('#FFD954')))
    p.setPen(QPen(QColor('#C49000'), 1))
    front = QPolygon([
        QPoint(1, 6),
        QPoint(13, 6),
        QPoint(14, 13),
        QPoint(2, 13)
    ])
    p.drawPolygon(front)
    
    # Highlight on top edge of front flap
    p.setPen(QPen(QColor('#FFF0A0'), 1))
    p.drawLine(2, 7, 13, 7)
    
    p.end()
    return QIcon(px)


def icon_folder_open(w=16, h=16):
    """Classic Windows XP open folder."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Back tab
    p.setBrush(QBrush(QColor('#D4A017')))
    p.setPen(QPen(QColor('#9E7206'), 1))
    p.drawRect(1, 2, 6, 4)
    p.drawRect(1, 4, 13, 9)
    
    # White document sticking out
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#808080'), 1))
    p.drawRect(4, 1, 8, 8)
    p.setPen(QPen(QColor('#336699'), 1))
    p.drawLine(6, 3, 10, 3)
    p.drawLine(6, 5, 10, 5)
    
    # Front open flap
    p.setBrush(QBrush(QColor('#FFE070')))
    p.setPen(QPen(QColor('#B08000'), 1))
    front = QPolygon([
        QPoint(0, 8),
        QPoint(13, 8),
        QPoint(15, 14),
        QPoint(2, 14)
    ])
    p.drawPolygon(front)
    p.end()
    return QIcon(px)


def icon_document(w=16, h=16):
    """Classic Windows document with folded corner."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Document body
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#505050'), 1))
    doc = QPolygon([
        QPoint(3, 1),
        QPoint(10, 1),
        QPoint(13, 4),
        QPoint(13, 14),
        QPoint(3, 14)
    ])
    p.drawPolygon(doc)
    
    # Fold corner
    p.setBrush(QBrush(QColor('#E0E0E0')))
    corner = QPolygon([
        QPoint(10, 1),
        QPoint(10, 4),
        QPoint(13, 4)
    ])
    p.drawPolygon(corner)
    
    # Text lines on document
    p.setPen(QPen(QColor('#316AC5'), 1))
    p.drawLine(5, 5, 9, 5)
    p.setPen(QPen(QColor('#808080'), 1))
    p.drawLine(5, 7, 11, 7)
    p.drawLine(5, 9, 11, 9)
    p.drawLine(5, 11, 9, 11)
    
    p.end()
    return QIcon(px)


def icon_dashboard(w=16, h=16):
    """XP Clinic Master Home / Summary card icon."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Monitor frame
    p.setBrush(QBrush(QColor('#ECE9D8')))
    p.setPen(QPen(QColor('#707070'), 1))
    p.drawRect(1, 1, 13, 10)
    
    # Blue screen
    p.setBrush(QBrush(QColor('#0055EA')))
    p.drawRect(3, 3, 9, 6)
    
    # Screen mini window
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.drawRect(4, 5, 4, 3)
    p.setBrush(QBrush(QColor('#FFCC00')))
    p.drawRect(9, 5, 2, 3)
    
    # Stand
    p.setBrush(QBrush(QColor('#A0A0A0')))
    p.setPen(QPen(QColor('#505050'), 1))
    p.drawRect(6, 11, 3, 2)
    p.drawRect(4, 13, 7, 2)
    p.end()
    return QIcon(px)


def icon_blood(w=16, h=16):
    """Red droplet with highlight."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    p.setBrush(QBrush(QColor('#D01010')))
    p.setPen(QPen(QColor('#800000'), 1))
    drop = QPolygon([
        QPoint(7, 1),
        QPoint(12, 8),
        QPoint(12, 11),
        QPoint(10, 14),
        QPoint(5, 14),
        QPoint(3, 11),
        QPoint(3, 8),
    ])
    p.drawPolygon(drop)
    
    # Glint
    p.setPen(QPen(QColor('#FF9090'), 1))
    p.drawPoint(6, 4)
    p.drawPoint(5, 7)
    p.drawLine(5, 8, 5, 10)
    p.end()
    return QIcon(px)


def icon_doctor(w=16, h=16):
    """Doctor with coat and stethoscope/cross."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Head
    p.setBrush(QBrush(QColor('#FFD1A4')))
    p.setPen(QPen(QColor('#B07840'), 1))
    p.drawEllipse(5, 1, 6, 5)
    
    # Hair
    p.setBrush(QBrush(QColor('#5A3818')))
    p.setPen(Qt.NoPen)
    p.drawRect(5, 1, 6, 2)
    
    # White doctor coat
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#606060'), 1))
    p.drawRect(3, 7, 10, 8)
    
    # Blue tie / stethoscope
    p.setPen(QPen(QColor('#003399'), 1))
    p.drawLine(8, 7, 8, 11)
    # Stethoscope loop
    p.drawArc(QRect(5, 7, 6, 5), 180 * 16, 180 * 16)
    
    # Red cross badge
    p.setPen(QPen(QColor('#CC0000'), 1))
    p.drawLine(10, 10, 12, 10)
    p.drawLine(11, 9, 11, 11)
    
    p.end()
    return QIcon(px)


def icon_tests(w=16, h=16):
    """Lab test tube with blue serum."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Tube glass
    p.setBrush(QBrush(QColor('#EAF4FF')))
    p.setPen(QPen(QColor('#5588BB'), 1))
    p.drawRect(5, 2, 6, 10)
    
    # Rounded tube bottom
    p.drawArc(QRect(5, 9, 5, 5), 180 * 16, 180 * 16)
    
    # Fluid inside (amber/blue)
    p.setBrush(QBrush(QColor('#2080E0')))
    p.setPen(Qt.NoPen)
    p.drawRect(6, 6, 5, 6)
    
    # Tube rim
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#336699'), 1))
    p.drawRect(4, 1, 8, 2)
    
    # Measurement marks
    p.setPen(QPen(QColor('#FFFFFF'), 1))
    p.drawLine(8, 8, 10, 8)
    p.drawLine(8, 10, 10, 10)
    p.end()
    return QIcon(px)


def icon_profile(w=16, h=16):
    """Patient ID card."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Card base
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#507090'), 1))
    p.drawRect(1, 2, 14, 11)
    
    # Top card stripe (blue XP)
    p.setBrush(QBrush(QColor('#0055EA')))
    p.setPen(Qt.NoPen)
    p.drawRect(2, 3, 13, 3)
    
    # Photo square
    p.setBrush(QBrush(QColor('#D0E0FF')))
    p.setPen(QPen(QColor('#80A0C0'), 1))
    p.drawRect(3, 7, 4, 5)
    
    # Card lines
    p.setPen(QPen(QColor('#606060'), 1))
    p.drawLine(9, 8, 13, 8)
    p.drawLine(9, 10, 13, 10)
    p.end()
    return QIcon(px)


def icon_graph(w=16, h=16):
    """Line graph / chart icon."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Background chart area
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#808080'), 1))
    p.drawRect(1, 1, 13, 13)
    
    # Grid lines
    p.setPen(QPen(QColor('#E0E0E0'), 1))
    p.drawLine(2, 5, 13, 5)
    p.drawLine(2, 9, 13, 9)
    p.drawLine(5, 2, 5, 13)
    p.drawLine(9, 2, 9, 13)
    
    # Graph line (red)
    p.setPen(QPen(QColor('#CC0000'), 1))
    p.drawLine(2, 11, 5, 7)
    p.drawLine(5, 7, 9, 9)
    p.drawLine(9, 9, 13, 3)
    
    # Data dots
    p.setBrush(QBrush(QColor('#003399')))
    p.setPen(Qt.NoPen)
    p.drawRect(4, 6, 2, 2)
    p.drawRect(8, 8, 2, 2)
    p.drawRect(12, 2, 2, 2)
    p.end()
    return QIcon(px)


def icon_add(w=16, h=16):
    """Classic green plus on white circle/square."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # White square with border
    p.setBrush(QBrush(QColor('#F4FFF4')))
    p.setPen(QPen(QColor('#008000'), 1))
    p.drawRect(1, 1, 13, 13)
    
    # Green plus
    p.setBrush(QBrush(QColor('#00A000')))
    p.setPen(Qt.NoPen)
    p.drawRect(6, 3, 3, 9)
    p.drawRect(3, 6, 9, 3)
    p.end()
    return QIcon(px)


def icon_edit(w=16, h=16):
    """Yellow pencil."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Pencil shaft
    p.setBrush(QBrush(QColor('#FFCC00')))
    p.setPen(QPen(QColor('#AA8800'), 1))
    shaft = QPolygon([
        QPoint(3, 12), QPoint(3, 7),
        QPoint(10, 0), QPoint(14, 4),
        QPoint(7, 13)
    ])
    p.drawPolygon(shaft)
    
    # Eraser tip
    p.setBrush(QBrush(QColor('#FF8080')))
    p.setPen(QPen(QColor('#CC5050'), 1))
    eraser = QPolygon([
        QPoint(10, 0), QPoint(14, 4),
        QPoint(15, 3), QPoint(12, 0)
    ])
    p.drawPolygon(eraser)
    
    # Lead tip
    p.setBrush(QBrush(QColor('#303030')))
    p.setPen(Qt.NoPen)
    tip = QPolygon([QPoint(1, 14), QPoint(4, 13), QPoint(2, 11)])
    p.drawPolygon(tip)
    p.end()
    return QIcon(px)


def icon_delete(w=16, h=16):
    """Red X mark."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    p.setPen(QPen(QColor('#CC0000'), 2))
    p.drawLine(3, 3, 12, 12)
    p.drawLine(12, 3, 3, 12)
    p.end()
    return QIcon(px)


def icon_refresh(w=16, h=16):
    """Green/blue circular reload arrows."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, True)
    
    p.setPen(QPen(QColor('#008020'), 2))
    p.drawArc(QRect(2, 2, 11, 11), 30 * 16, 280 * 16)
    
    p.setBrush(QBrush(QColor('#008020')))
    p.setPen(Qt.NoPen)
    arr = QPolygon([QPoint(11, 1), QPoint(15, 5), QPoint(10, 6)])
    p.drawPolygon(arr)
    p.end()
    return QIcon(px)


def icon_save(w=16, h=16):
    """3.5 inch blue floppy disk."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Blue disk body
    p.setBrush(QBrush(QColor('#2055A0')))
    p.setPen(QPen(QColor('#103060'), 1))
    p.drawRect(1, 1, 13, 13)
    
    # Silver slider on top
    p.setBrush(QBrush(QColor('#D0D0D8')))
    p.setPen(QPen(QColor('#808090'), 1))
    p.drawRect(4, 1, 6, 5)
    p.setBrush(QBrush(QColor('#2055A0')))
    p.drawRect(8, 2, 1, 3)
    
    # White label on bottom
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#A0A0A0'), 1))
    p.drawRect(3, 7, 9, 7)
    
    # Red line on label
    p.setPen(QPen(QColor('#CC0000'), 1))
    p.drawLine(5, 9, 10, 9)
    p.end()
    return QIcon(px)


def icon_eye(w=16, h=16):
    """Eye icon for show password."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, True)
    
    # Eye white outline
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#404040'), 1))
    p.drawEllipse(2, 4, 12, 8)
    
    # Iris (XP blue)
    p.setBrush(QBrush(QColor('#316AC5')))
    p.setPen(Qt.NoPen)
    p.drawEllipse(5, 5, 6, 6)
    
    # Pupil
    p.setBrush(QBrush(QColor('#000000')))
    p.drawEllipse(7, 7, 2, 2)
    p.end()
    return QIcon(px)


def icon_logout(w=16, h=16):
    """Classic Windows XP logoff key / door icon."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Gold key / red arrow
    p.setBrush(QBrush(QColor('#FFC020')))
    p.setPen(QPen(QColor('#B08000'), 1))
    p.drawEllipse(2, 3, 6, 6)
    p.drawRect(7, 5, 7, 2)
    p.drawRect(10, 7, 2, 2)
    p.drawRect(12, 7, 2, 2)
    p.end()
    return QIcon(px)


def icon_medora(w=24, h=24):
    """MEDORA Red Cross Shield app logo."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Shield
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(QPen(QColor('#003399'), 2))
    pts = QPolygon([
        QPoint(3, 3),
        QPoint(w - 3, 3),
        QPoint(w - 3, h // 2 + 3),
        QPoint(w // 2, h - 2),
        QPoint(3, h // 2 + 3)
    ])
    p.drawPolygon(pts)
    
    # Red Cross
    cx, cy = w // 2, h // 2 - 1
    p.setBrush(QBrush(QColor('#D01010')))
    p.setPen(Qt.NoPen)
    p.drawRect(cx - 2, cy - 6, 4, 12)
    p.drawRect(cx - 6, cy - 2, 12, 4)
    p.end()
    return QIcon(px)


def icon_console(w=16, h=16):
    """Classic Windows XP Command Prompt / CMD icon (black terminal with >_)."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Outer terminal window
    p.setBrush(QBrush(QColor('#000000')))
    p.setPen(QPen(QColor('#707070'), 1))
    p.drawRect(1, 1, 13, 13)
    
    # Title strip
    p.setBrush(QBrush(QColor('#0A246A')))
    p.setPen(Qt.NoPen)
    p.drawRect(2, 2, 12, 3)
    
    # Green prompt >_
    p.setPen(QPen(QColor('#00FF00'), 1))
    p.drawLine(3, 7, 5, 9)
    p.drawLine(5, 9, 3, 11)
    p.drawLine(7, 11, 10, 11)
    
    p.end()
    return QIcon(px)


def icon_database(w=16, h=16):
    """MySQL database cylinder stack."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, True)
    
    blue = QColor('#2060C0')
    dark_blue = QColor('#0A3070')
    
    p.setBrush(QBrush(blue))
    p.setPen(QPen(dark_blue, 1))
    
    # Cylinders stack
    p.drawEllipse(QRectF(2, 2, 12, 4))
    
    p.drawRect(QRectF(2, 4, 12, 3))
    p.drawEllipse(QRectF(2, 5, 12, 4))
    
    p.drawRect(QRectF(2, 8, 12, 3))
    p.drawEllipse(QRectF(2, 9, 12, 4))
    
    p.end()
    return QIcon(px)


def icon_admin(w=16, h=16):
    """Admin golden star / badge."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Gold badge shield
    p.setBrush(QBrush(QColor('#FFCC00')))
    p.setPen(QPen(QColor('#996600'), 1))
    pts = QPolygon([
        QPoint(3, 2), QPoint(12, 2),
        QPoint(14, 6), QPoint(8, 14),
        QPoint(1, 6)
    ])
    p.drawPolygon(pts)
    
    # Star center
    p.setBrush(QBrush(QColor('#FFFFFF')))
    p.setPen(Qt.NoPen)
    p.drawRect(7, 4, 2, 6)
    p.drawRect(5, 6, 6, 2)
    p.end()
    return QIcon(px)


def icon_users(w=16, h=16):
    """Multiple users / patients icon."""
    px = _new_pixmap(w, h)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    
    # Back person (blue)
    p.setBrush(QBrush(QColor('#A0C0E0')))
    p.setPen(QPen(QColor('#507090'), 1))
    p.drawEllipse(9, 1, 5, 5)
    p.drawRect(8, 7, 7, 6)
    
    # Front person (yellow/skin)
    p.setBrush(QBrush(QColor('#FFD1A4')))
    p.setPen(QPen(QColor('#9E6E38'), 1))
    p.drawEllipse(3, 2, 6, 5)
    p.setBrush(QBrush(QColor('#316AC5')))
    p.setPen(QPen(QColor('#1A4080'), 1))
    p.drawRect(2, 8, 8, 6)
    
    p.end()
    return QIcon(px)

