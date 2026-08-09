"""
Fhish's View — Premium Windows Dynamic Island overlay.
Apple-inspired glass island with fluid compact → medium → expanded states.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QSlider, QSizePolicy, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize,
    QParallelAnimationGroup, QTimer, pyqtProperty
)
from PyQt6.QtGui import QColor, QFont, QCursor, QPainter, QPainterPath, QBrush, QPen, QLinearGradient


# ─── Design tokens (Windows-friendly sizing) ───────────────────────────────────
COMPACT_W, COMPACT_H = 168, 36
MEDIUM_W, MEDIUM_H = 340, 48
EXPANDED_W, EXPANDED_H = 400, 320
ANIM_MS = 320

GLASS_BG = "rgba(12, 12, 14, 0.82)"
GLASS_BORDER = "rgba(255, 255, 255, 0.14)"
ACCENT = "#0A84FF"
TEXT_PRIMARY = "rgba(255, 255, 255, 0.95)"
TEXT_SECONDARY = "rgba(255, 255, 255, 0.55)"
TEXT_MUTED = "rgba(255, 255, 255, 0.32)"


class GlassFrame(QFrame):
    """Rounded glass container with soft outer glow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glass")
        self.setStyleSheet(f"""
            #glass {{
                background: {GLASS_BG};
                border: 1px solid {GLASS_BORDER};
                border-radius: 18px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)


class IslandWindow(QWidget):
    """Floating Dynamic Island for Windows."""

    def __init__(self):
        super().__init__()
        self.mode = "compact"  # compact | medium | music | search | system
        self._drag_pos = None
        self._anim_group = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        self._build_ui()
        self._position_top_center(COMPACT_W, COMPACT_H)
        self._show_compact()

    # ─── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        self.glass = GlassFrame()
        self.glass_layout = QVBoxLayout(self.glass)
        self.glass_layout.setContentsMargins(0, 0, 0, 0)
        self.glass_layout.setSpacing(0)

        # Stack of views
        self.compact_view = self._build_compact()
        self.medium_view = self._build_medium()
        self.music_view = self._build_music()
        self.search_view = self._build_search()
        self.system_view = self._build_system()

        for v in (self.compact_view, self.medium_view, self.music_view,
                  self.search_view, self.system_view):
            self.glass_layout.addWidget(v)
            v.hide()

        self.root.addWidget(self.glass)

    def _build_compact(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 12, 0)
        lay.setSpacing(8)

        # Live indicator dot
        self.dot = QLabel("●")
        self.dot.setStyleSheet(f"color: {ACCENT}; font-size: 9px;")
        self.dot.setFixedWidth(12)

        self.compact_label = QLabel("Fhish's View")
        self.compact_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 600; letter-spacing: 0.2px;"
        )

        lay.addWidget(self.dot)
        lay.addWidget(self.compact_label)
        lay.addStretch()

        # Subtle activity hint
        hint = QLabel("Ready")
        hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        lay.addWidget(hint)

        w.mousePressEvent = self._on_compact_click
        w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return w

    def _build_medium(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(10)

        # Logo pill
        logo = QLabel("F")
        logo.setFixedSize(28, 28)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #5AC8FA, stop:1 #0A84FF);
            color: white;
            font-weight: 800;
            font-size: 13px;
            border-radius: 14px;
        """)

        title = QLabel("Fhish's View")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")

        lay.addWidget(logo)
        lay.addWidget(title)
        lay.addStretch()

        # Quick action chips
        for label, mode in [("Music", "music"), ("Search", "search"), ("System", "system")]:
            btn = QPushButton(label)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(26)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.08);
                    color: {TEXT_SECONDARY};
                    border: none;
                    border-radius: 13px;
                    padding: 0 12px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.16);
                    color: {TEXT_PRIMARY};
                }}
                QPushButton:pressed {{
                    background: rgba(255,255,255,0.22);
                }}
            """)
            btn.clicked.connect(lambda checked=False, m=mode: self._go(m))
            lay.addWidget(btn)

        close = self._make_close_btn()
        close.clicked.connect(self.collapse)
        lay.addWidget(close)
        return w

    def _build_music(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("Now Playing")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        close = self._make_close_btn()
        close.clicked.connect(lambda: self._go("medium"))
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close)
        lay.addLayout(header)

        # Artwork + meta
        row = QHBoxLayout()
        row.setSpacing(14)

        art = QLabel("♪")
        art.setFixedSize(72, 72)
        art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1C1C1E, stop:1 #2C2C2E);
            color: {ACCENT};
            font-size: 28px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
        """)

        meta = QVBoxLayout()
        meta.setSpacing(2)
        song = QLabel("Blinding Lights")
        song.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 600;")
        artist = QLabel("The Weeknd")
        artist.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        meta.addWidget(song)
        meta.addWidget(artist)
        meta.addStretch()

        # Equalizer dots (visual only)
        eq = QHBoxLayout()
        eq.setSpacing(3)
        for h in (10, 16, 8, 14, 6):
            bar = QFrame()
            bar.setFixedSize(3, h)
            bar.setStyleSheet(f"background: {ACCENT}; border-radius: 1px;")
            eq.addWidget(bar, alignment=Qt.AlignmentFlag.AlignBottom)
        meta.addLayout(eq)

        row.addWidget(art)
        row.addLayout(meta)
        lay.addLayout(row)

        # Progress
        progress = QSlider(Qt.Orientation.Horizontal)
        progress.setRange(0, 100)
        progress.setValue(38)
        progress.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: rgba(255,255,255,0.12);
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                width: 12px;
                height: 12px;
                margin: -4px 0;
                background: white;
                border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {ACCENT};
                border-radius: 2px;
            }}
        """)
        lay.addWidget(progress)

        times = QHBoxLayout()
        t1 = QLabel("1:24")
        t1.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
        t2 = QLabel("-2:18")
        t2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
        times.addWidget(t1)
        times.addStretch()
        times.addWidget(t2)
        lay.addLayout(times)

        # Controls
        controls = QHBoxLayout()
        controls.setSpacing(20)
        controls.addStretch()
        for symbol in ("⏮", "▶", "⏭"):
            b = QPushButton(symbol)
            b.setFixedSize(40, 40)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.08);
                    color: {TEXT_PRIMARY};
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.16);
                }}
                QPushButton:pressed {{
                    background: rgba(255,255,255,0.24);
                }}
            """)
            controls.addWidget(b)
        controls.addStretch()
        lay.addLayout(controls)

        return w

    def _build_search(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Search")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        close = self._make_close_btn()
        close.clicked.connect(lambda: self._go("medium"))
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close)
        lay.addLayout(header)

        # Fake search field
        field = QLabel("  Search apps, files, web…")
        field.setFixedHeight(40)
        field.setStyleSheet(f"""
            background: rgba(255,255,255,0.06);
            color: {TEXT_MUTED};
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            font-size: 13px;
            padding-left: 8px;
        """)
        lay.addWidget(field)

        for icon, label in [("📁", "Documents"), ("🌐", "Web"), ("⚙️", "Settings")]:
            row = QHBoxLayout()
            i = QLabel(icon)
            i.setFixedWidth(28)
            t = QLabel(label)
            t.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
            row.addWidget(i)
            row.addWidget(t)
            row.addStretch()
            lay.addLayout(row)

        lay.addStretch()
        return w

    def _build_system(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("System")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        close = self._make_close_btn()
        close.clicked.connect(lambda: self._go("medium"))
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close)
        lay.addLayout(header)

        # Volume
        vol_row = QHBoxLayout()
        vol_label = QLabel("🔊  Volume")
        vol_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        vol_row.addWidget(vol_label)
        vol_row.addStretch()
        lay.addLayout(vol_row)

        vol = QSlider(Qt.Orientation.Horizontal)
        vol.setRange(0, 100)
        vol.setValue(62)
        vol.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: rgba(255,255,255,0.12);
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: white;
                border-radius: 7px;
            }}
            QSlider::sub-page:horizontal {{
                background: {ACCENT};
                border-radius: 2px;
            }}
        """)
        lay.addWidget(vol)

        # Quick toggles
        toggles = QHBoxLayout()
        toggles.setSpacing(10)
        for label, active in [("Wi-Fi", True), ("Bluetooth", False), ("Focus", False)]:
            chip = QPushButton(label)
            chip.setCheckable(True)
            chip.setChecked(active)
            chip.setFixedHeight(36)
            chip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            chip.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.06);
                    color: {TEXT_SECONDARY};
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 12px;
                    padding: 0 14px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:checked {{
                    background: rgba(10, 132, 255, 0.25);
                    color: {TEXT_PRIMARY};
                    border: 1px solid rgba(10, 132, 255, 0.4);
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.12);
                }}
            """)
            toggles.addWidget(chip)
        lay.addLayout(toggles)

        # Battery / status
        status = QLabel("🔋  78%  ·  Balanced")
        status.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-top: 8px;")
        lay.addWidget(status)
        lay.addStretch()
        return w

    def _make_close_btn(self) -> QPushButton:
        btn = QPushButton("✕")
        btn.setFixedSize(26, 26)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.08);
                color: {TEXT_SECONDARY};
                border: none;
                border-radius: 13px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.18);
                color: white;
            }}
            QPushButton:pressed {{
                background: rgba(255,59,48,0.35);
                color: white;
            }}
        """)
        return btn

    # ─── State machine ─────────────────────────────────────────────────────────

    def _go(self, mode: str):
        if mode == self.mode:
            return
        self.mode = mode

        # Hide all views first
        for v in (self.compact_view, self.medium_view, self.music_view,
                  self.search_view, self.system_view):
            v.hide()

        if mode == "compact":
            target_w, target_h = COMPACT_W, COMPACT_H
            self.compact_view.show()
            radius = 18
        elif mode == "medium":
            target_w, target_h = MEDIUM_W, MEDIUM_H
            self.medium_view.show()
            radius = 20
        else:
            target_w, target_h = EXPANDED_W, EXPANDED_H
            if mode == "music":
                self.music_view.show()
            elif mode == "search":
                self.search_view.show()
            else:
                self.system_view.show()
            radius = 22

        self.glass.setStyleSheet(f"""
            #glass {{
                background: {GLASS_BG};
                border: 1px solid {GLASS_BORDER};
                border-radius: {radius}px;
            }}
        """)

        self._animate_to(target_w, target_h)

    def _show_compact(self):
        self.mode = "compact"
        for v in (self.medium_view, self.music_view, self.search_view, self.system_view):
            v.hide()
        self.compact_view.show()
        self.setFixedSize(COMPACT_W, COMPACT_H)

    def collapse(self):
        self._go("compact")

    def _on_compact_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._go("medium")

    # ─── Animation ─────────────────────────────────────────────────────────────

    def _animate_to(self, w: int, h: int):
        if self._anim_group and self._anim_group.state() == QPropertyAnimation.State.Running:
            self._anim_group.stop()

        screen = self._screen_geo()
        target_x = screen.x() + (screen.width() - w) // 2
        target_y = self.y()  # keep vertical position

        # Geometry animation on the window itself
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(ANIM_MS)
        anim.setStartValue(self.geometry())
        anim.setEndValue(QRect(target_x, target_y, w, h))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Soft scale-like feel: also force fixed size at end
        def on_finished():
            self.setFixedSize(w, h)

        anim.finished.connect(on_finished)
        self._anim_group = anim
        anim.start()

    # ─── Positioning & drag ────────────────────────────────────────────────────

    def _screen_geo(self):
        if self.screen():
            return self.screen().availableGeometry()
        from PyQt6.QtGui import QGuiApplication
        return QGuiApplication.primaryScreen().availableGeometry()

    def _position_top_center(self, w: int, h: int):
        screen = self._screen_geo()
        x = screen.x() + (screen.width() - w) // 2
        y = screen.y() + 12
        self.setGeometry(x, y, w, h)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.collapse()
