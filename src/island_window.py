"""
Main floating island window — top center, always on top, frameless, transparent.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QStackedWidget, QLineEdit, QSlider, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QPen, QPainterPath, QCursor


class IslandWindow(QWidget):
    COLLAPSED_W = 190
    COLLAPSED_H = 40
    EXPANDED_W = 380
    EXPANDED_H = 300

    def __init__(self):
        super().__init__()
        self.expanded = False
        self._drag_pos = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        self._setup_ui()
        self._position_top_center()
        self._apply_collapsed()

    def _setup_ui(self):
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # Main glass container
        self.container = QFrame()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background: rgba(18, 18, 22, 0.88);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 22px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 8, 10, 8)
        self.container_layout.setSpacing(6)

        # --- Collapsed row ---
        self.collapsed_row = QWidget()
        collapsed_layout = QHBoxLayout(self.collapsed_row)
        collapsed_layout.setContentsMargins(6, 0, 6, 0)
        collapsed_layout.setSpacing(8)

        self.logo = QLabel("F")
        self.logo.setFixedSize(26, 26)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #4DA3FF, stop:1 #007AFF);
            color: white;
            font-weight: 800;
            font-size: 12px;
            border-radius: 13px;
        """)

        self.title_label = QLabel("Fhish's View")
        self.title_label.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 12px; font-weight: 600;")

        collapsed_layout.addWidget(self.logo)
        collapsed_layout.addWidget(self.title_label)
        collapsed_layout.addStretch()

        # --- Expanded content ---
        self.expanded_area = QWidget()
        expanded_layout = QVBoxLayout(self.expanded_area)
        expanded_layout.setContentsMargins(4, 4, 4, 4)
        expanded_layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        header_title = QLabel("Fhish's View")
        header_title.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 600;")
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.6);
                border: none;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self.collapse)
        header.addWidget(header_title)
        header.addStretch()
        header.addWidget(self.close_btn)
        expanded_layout.addLayout(header)

        # Menu buttons
        self.menu_btns = []
        for label, desc in [
            ("Music", "Now playing controls"),
            ("Search", "Apps, files, web"),
            ("System", "Wi-Fi, volume, focus"),
        ]:
            btn = self._make_menu_button(label, desc)
            expanded_layout.addWidget(btn)
            self.menu_btns.append(btn)

        tagline = QLabel("Your Windows. Reimagined.")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 11px; margin-top: 6px;")
        expanded_layout.addWidget(tagline)

        self.expanded_area.hide()

        self.container_layout.addWidget(self.collapsed_row)
        self.container_layout.addWidget(self.expanded_area)
        self.root.addWidget(self.container)

        # Click collapsed row to expand
        self.collapsed_row.mousePressEvent = self._on_collapsed_click

    def _make_menu_button(self, label: str, desc: str) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 14px;
                padding: 12px 14px;
                text-align: left;
                color: white;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.1);
            }
        """)
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(4, 0, 4, 0)

        icon = QLabel(label[:2].upper())
        icon.setFixedSize(34, 34)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("""
            background: rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.7);
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        """)

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        t1 = QLabel(label)
        t1.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 600; background: transparent;")
        t2 = QLabel(desc)
        t2.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px; background: transparent;")
        text_col.addWidget(t1)
        text_col.addWidget(t2)

        layout.addWidget(icon)
        layout.addLayout(text_col)
        layout.addStretch()
        return btn

    def _position_top_center(self):
        screen = self.screen().availableGeometry() if self.screen() else None
        if screen is None:
            from PyQt6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen().availableGeometry()

        x = screen.x() + (screen.width() - self.COLLAPSED_W) // 2
        y = screen.y() + 10
        self.setGeometry(x, y, self.COLLAPSED_W, self.COLLAPSED_H)

    def _apply_collapsed(self):
        self.expanded = False
        self.expanded_area.hide()
        self.collapsed_row.show()
        self.setFixedSize(self.COLLAPSED_W, self.COLLAPSED_H)

        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            x = screen.x() + (screen.width() - self.COLLAPSED_W) // 2
            self.move(x, self.y())

    def expand(self):
        self.expanded = True
        self.collapsed_row.hide()
        self.expanded_area.show()
        self.setFixedSize(self.EXPANDED_W, self.EXPANDED_H)

        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            x = screen.x() + (screen.width() - self.EXPANDED_W) // 2
            self.move(x, self.y())

    def collapse(self):
        self._apply_collapsed()

    def _on_collapsed_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.expand()

    # --- Drag support ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
