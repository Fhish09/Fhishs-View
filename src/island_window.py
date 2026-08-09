"""
Fhish's View — Premium Windows Dynamic Island overlay.
Matches the React frontend structure: compact island → expanded panel
with Menu / Music / Search / System content.
System panel drives real Windows volume, brightness, and Settings.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QSlider, QLineEdit, QGridLayout
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect
)
from PyQt6.QtGui import QColor, QCursor

from src import system_control as sysctl


# Sizes aligned with frontend (App.tsx / Island.tsx)
COMPACT_W, COMPACT_H = 180, 36
EXPANDED_W, EXPANDED_H = 380, 320
ANIM_MS = 300

GLASS_BG = "rgba(0, 0, 0, 0.85)"
GLASS_BORDER = "rgba(255, 255, 255, 0.10)"
TEXT_PRIMARY = "rgba(255, 255, 255, 0.90)"
TEXT_SECONDARY = "rgba(255, 255, 255, 0.50)"
TEXT_MUTED = "rgba(255, 255, 255, 0.30)"

# Map UI labels → system_control keys
TOGGLE_KEYS = {
    "Wi-Fi": "wifi",
    "Bluetooth": "bluetooth",
    "Focus": "focus",
    "Night Light": "night_light",
}


def _logo(size: int = 20, font_size: int = 10) -> QLabel:
    logo = QLabel("F")
    logo.setFixedSize(size, size)
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    r = size // 2
    logo.setStyleSheet(f"""
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #60A5FA, stop:1 #2563EB);
        color: white;
        font-weight: 800;
        font-size: {font_size}px;
        border-radius: {r}px;
    """)
    return logo


def _close_btn() -> QPushButton:
    btn = QPushButton("✕")
    btn.setFixedSize(24, 24)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setStyleSheet("""
        QPushButton {
            background: rgba(255,255,255,0.10);
            color: rgba(255,255,255,0.60);
            border: none;
            border-radius: 12px;
            font-size: 11px;
        }
        QPushButton:hover {
            background: rgba(255,255,255,0.20);
            color: white;
        }
        QPushButton:pressed {
            background: rgba(255,59,48,0.40);
            color: white;
        }
    """)
    return btn


def _slider(value: int = 50) -> QSlider:
    s = QSlider(Qt.Orientation.Horizontal)
    s.setRange(0, 100)
    s.setValue(value)
    s.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 6px;
            background: rgba(255,255,255,0.10);
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            width: 14px;
            height: 14px;
            margin: -4px 0;
            background: white;
            border-radius: 7px;
        }
        QSlider::sub-page:horizontal {
            background: rgba(255,255,255,0.50);
            border-radius: 3px;
        }
    """)
    return s


class IslandWindow(QWidget):
    """Floating Dynamic Island — matches React frontend behaviour."""

    def __init__(self):
        super().__init__()
        self.mode = "collapsed"  # collapsed | menu | music | search | system
        self._drag_pos = None
        self._anim = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self._position_top_center(COMPACT_W, COMPACT_H)
        self._apply_mode("collapsed", animate=False)

    # ─── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        self.glass = QFrame()
        self.glass.setObjectName("glass")
        self._set_glass_radius(18)
        shadow = QGraphicsDropShadowEffect(self.glass)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.glass.setGraphicsEffect(shadow)

        self.glass_layout = QVBoxLayout(self.glass)
        self.glass_layout.setContentsMargins(0, 0, 0, 0)
        self.glass_layout.setSpacing(0)

        self.compact_view = self._build_compact()
        self.glass_layout.addWidget(self.compact_view)

        self.expanded_shell = QWidget()
        shell_lay = QVBoxLayout(self.expanded_shell)
        shell_lay.setContentsMargins(0, 0, 0, 0)
        shell_lay.setSpacing(0)

        shell_lay.addWidget(self._build_header())

        self.content = QWidget()
        self.content_lay = QVBoxLayout(self.content)
        self.content_lay.setContentsMargins(12, 12, 12, 12)
        self.content_lay.setSpacing(0)

        self.menu_panel = self._build_menu_panel()
        self.music_panel = self._build_music_panel()
        self.search_panel = self._build_search_panel()
        self.system_panel = self._build_system_panel()

        for p in (self.menu_panel, self.music_panel, self.search_panel, self.system_panel):
            self.content_lay.addWidget(p)
            p.hide()

        shell_lay.addWidget(self.content)
        self.glass_layout.addWidget(self.expanded_shell)
        self.expanded_shell.hide()

        self.root.addWidget(self.glass)

    def _set_glass_radius(self, r: int):
        self.glass.setStyleSheet(f"""
            #glass {{
                background: {GLASS_BG};
                border: 1px solid {GLASS_BORDER};
                border-radius: {r}px;
            }}
        """)

    def _build_compact(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(_logo(20, 10))

        title = QLabel("Fhish's View")
        title.setStyleSheet(
            "color: rgba(255,255,255,0.70); font-size: 12px; font-weight: 500; letter-spacing: 0.3px;"
        )
        lay.addWidget(title)

        w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        w.mousePressEvent = self._on_compact_click
        return w

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(48)
        lay = QHBoxLayout(header)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(8)

        lay.addWidget(_logo(24, 11))

        title = QLabel("Fhish's View")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")
        lay.addWidget(title)
        lay.addStretch()

        close = _close_btn()
        close.clicked.connect(self.collapse)
        lay.addWidget(close)

        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: rgba(255,255,255,0.05);")

        wrap = QWidget()
        v = QVBoxLayout(wrap)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(header)
        v.addWidget(line)
        return wrap

    def _build_menu_panel(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        items = [
            ("music", "Music", "Now playing controls"),
            ("search", "Search", "Apps, files, web"),
            ("system", "System", "Wi-Fi, volume, focus"),
        ]
        for mode, label, desc in items:
            btn = QPushButton()
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(52)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.05);
                    border: none;
                    border-radius: 16px;
                    text-align: left;
                    padding: 0 12px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.10);
                }
                QPushButton:pressed {
                    background: rgba(255,255,255,0.14);
                }
            """)
            inner = QHBoxLayout(btn)
            inner.setContentsMargins(4, 0, 4, 0)
            inner.setSpacing(12)

            icon = QLabel(label[:2].upper())
            icon.setFixedSize(36, 36)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("""
                background: rgba(255,255,255,0.10);
                color: rgba(255,255,255,0.70);
                border-radius: 12px;
                font-size: 11px;
                font-weight: 700;
            """)

            texts = QVBoxLayout()
            texts.setSpacing(1)
            t1 = QLabel(label)
            t1.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500; background: transparent;")
            t2 = QLabel(desc)
            t2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
            texts.addWidget(t1)
            texts.addWidget(t2)

            inner.addWidget(icon)
            inner.addLayout(texts)
            inner.addStretch()

            btn.clicked.connect(lambda checked=False, m=mode: self._apply_mode(m))
            lay.addWidget(btn)

        tag = QLabel("Your Windows. Reimagined.")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; margin-top: 10px;")
        lay.addWidget(tag)
        lay.addStretch()
        return w

    def _build_music_panel(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        row = QHBoxLayout()
        row.setSpacing(12)

        art = QLabel("")
        art.setFixedSize(56, 56)
        art.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #A855F7, stop:1 #EC4899);
            border-radius: 12px;
        """)

        meta = QVBoxLayout()
        meta.setSpacing(2)
        song = QLabel("No media playing")
        song.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")
        artist = QLabel("Open Spotify, YouTube, or VLC")
        artist.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        meta.addWidget(song)
        meta.addWidget(artist)
        meta.addStretch()

        row.addWidget(art)
        row.addLayout(meta)
        lay.addLayout(row)

        progress = QFrame()
        progress.setFixedHeight(4)
        progress.setStyleSheet("background: rgba(255,255,255,0.10); border-radius: 2px;")
        lay.addWidget(progress)

        controls = QHBoxLayout()
        controls.setSpacing(24)
        controls.addStretch()

        for text, primary in [("Prev", False), ("Play", True), ("Next", False)]:
            b = QPushButton(text)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if primary:
                b.setFixedSize(40, 40)
                b.setStyleSheet("""
                    QPushButton {
                        background: rgba(255,255,255,0.15);
                        color: white;
                        border: none;
                        border-radius: 20px;
                        font-size: 12px;
                        font-weight: 500;
                    }
                    QPushButton:hover { background: rgba(255,255,255,0.25); }
                    QPushButton:pressed { background: rgba(255,255,255,0.30); }
                """)
            else:
                b.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: rgba(255,255,255,0.50);
                        border: none;
                        font-size: 12px;
                    }
                    QPushButton:hover { color: rgba(255,255,255,0.80); }
                """)
            controls.addWidget(b)

        controls.addStretch()
        lay.addLayout(controls)

        back = QPushButton("←  Menu")
        back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 11px;
                text-align: left;
            }}
            QPushButton:hover {{ color: {TEXT_SECONDARY}; }}
        """)
        back.clicked.connect(lambda: self._apply_mode("menu"))
        lay.addWidget(back)
        lay.addStretch()
        return w

    def _build_search_panel(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search apps, files, web...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                color: white;
                font-size: 13px;
                padding: 0 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(255,255,255,0.25);
            }
        """)
        self.search_input.returnPressed.connect(self._on_search)
        lay.addWidget(self.search_input)

        self.search_hint = QLabel("Start typing to search")
        self.search_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; padding: 16px 0;")
        lay.addWidget(self.search_hint)

        self.search_input.textChanged.connect(self._on_search_text)

        back = QPushButton("←  Menu")
        back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 11px;
                text-align: left;
            }}
            QPushButton:hover {{ color: {TEXT_SECONDARY}; }}
        """)
        back.clicked.connect(lambda: self._apply_mode("menu"))
        lay.addWidget(back)
        lay.addStretch()
        return w

    def _build_system_panel(self) -> QWidget:
        """2×2 settings buttons + live volume & brightness."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # Capability note
        self.sys_status = QLabel("")
        self.sys_status.setWordWrap(True)
        self.sys_status.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
        lay.addWidget(self.sys_status)

        grid = QGridLayout()
        grid.setSpacing(8)

        controls = ["Wi-Fi", "Bluetooth", "Focus", "Night Light"]
        self.toggle_btns = {}
        for i, label in enumerate(controls):
            btn = QPushButton()
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(52)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.05);
                    border-radius: 14px;
                    text-align: left;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.12);
                    border: 1px solid rgba(96, 165, 250, 0.35);
                }
                QPushButton:pressed {
                    background: rgba(59, 130, 246, 0.30);
                }
            """)

            inner = QVBoxLayout(btn)
            inner.setContentsMargins(4, 2, 4, 2)
            inner.setSpacing(1)
            t1 = QLabel(label)
            t1.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500; background: transparent;")
            t2 = QLabel("Open Settings")
            t2.setObjectName("status")
            t2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
            inner.addWidget(t1)
            inner.addWidget(t2)

            key = TOGGLE_KEYS[label]
            btn.clicked.connect(lambda checked=False, k=key, b=btn: self._on_toggle_clicked(k, b))
            self.toggle_btns[label] = btn
            grid.addWidget(btn, i // 2, i % 2)

        lay.addLayout(grid)

        # Volume — real OS control
        vol_lbl = QLabel("Volume")
        vol_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; margin-top: 2px;")
        lay.addWidget(vol_lbl)
        vol_now = sysctl.get_volume()
        self.volume_slider = _slider(vol_now if vol_now is not None else 50)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        lay.addWidget(self.volume_slider)

        # Brightness — real OS control (laptops)
        bri_lbl = QLabel("Brightness")
        bri_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        lay.addWidget(bri_lbl)
        bri_now = sysctl.get_brightness()
        self.brightness_slider = _slider(bri_now if bri_now is not None else 50)
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        lay.addWidget(self.brightness_slider)

        back = QPushButton("←  Menu")
        back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 11px;
                text-align: left;
                margin-top: 2px;
            }}
            QPushButton:hover {{ color: {TEXT_SECONDARY}; }}
        """)
        back.clicked.connect(lambda: self._apply_mode("menu"))
        lay.addWidget(back)
        lay.addStretch()

        self._refresh_sys_status()
        return w

    # ─── Real system actions ───────────────────────────────────────────────────

    def _refresh_sys_status(self):
        caps = sysctl.capabilities()
        parts = []
        if caps["volume"]:
            parts.append("Volume ✓")
        else:
            parts.append("Volume unavailable")
        if caps["brightness"]:
            parts.append("Brightness ✓")
        else:
            parts.append("Brightness N/A (external monitor?)")
        parts.append("Toggles open Windows Settings")
        self.sys_status.setText("  ·  ".join(parts))

    def _sync_sliders_from_os(self):
        """Pull current OS values when System panel opens."""
        vol = sysctl.get_volume()
        if vol is not None:
            self.volume_slider.blockSignals(True)
            self.volume_slider.setValue(vol)
            self.volume_slider.blockSignals(False)

        bri = sysctl.get_brightness()
        if bri is not None:
            self.brightness_slider.blockSignals(True)
            self.brightness_slider.setValue(bri)
            self.brightness_slider.blockSignals(False)

        self._refresh_sys_status()

    def _on_volume_changed(self, value: int):
        ok = sysctl.set_volume(value)
        if not ok:
            self.sys_status.setText("Could not set volume — is audio device available?")

    def _on_brightness_changed(self, value: int):
        ok = sysctl.set_brightness(value)
        if not ok:
            self.sys_status.setText("Brightness not supported on this display")

    def _on_toggle_clicked(self, key: str, btn: QPushButton):
        ok = sysctl.open_setting(key)
        status = btn.findChild(QLabel, "status")
        if status:
            status.setText("Opened Settings…" if ok else "Failed to open")

    # ─── Search ────────────────────────────────────────────────────────────────

    def _on_search_text(self, text: str):
        if text.strip():
            self.search_hint.setText(f'Searching for "{text}"…')
        else:
            self.search_hint.setText("Start typing to search")

    def _on_search(self):
        query = self.search_input.text().strip()
        if query:
            self.search_hint.setText(f'Results for "{query}" (coming soon)')

    def _on_compact_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._apply_mode("menu")

    def collapse(self):
        self._apply_mode("collapsed")

    # ─── Mode / animation ──────────────────────────────────────────────────────

    def _apply_mode(self, mode: str, animate: bool = True):
        self.mode = mode

        for p in (self.menu_panel, self.music_panel, self.search_panel, self.system_panel):
            p.hide()

        if mode == "collapsed":
            self.expanded_shell.hide()
            self.compact_view.show()
            self._set_glass_radius(18)
            target = (COMPACT_W, COMPACT_H)
        else:
            self.compact_view.hide()
            self.expanded_shell.show()
            self._set_glass_radius(28)

            if mode == "menu":
                self.menu_panel.show()
            elif mode == "music":
                self.music_panel.show()
            elif mode == "search":
                self.search_panel.show()
                self.search_input.setFocus()
            elif mode == "system":
                self.system_panel.show()
                self._sync_sliders_from_os()

            target = (EXPANDED_W, EXPANDED_H)

        if animate:
            self._animate_to(*target)
        else:
            self.setFixedSize(*target)
            self._recenter(target[0])

    def _animate_to(self, w: int, h: int):
        if self._anim and self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()

        screen = self._screen_geo()
        x = screen.x() + (screen.width() - w) // 2
        y = self.y()

        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(ANIM_MS)
        anim.setStartValue(self.geometry())
        anim.setEndValue(QRect(x, y, w, h))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def done():
            self.setFixedSize(w, h)

        anim.finished.connect(done)
        self._anim = anim
        anim.start()

    def _recenter(self, w: int):
        screen = self._screen_geo()
        x = screen.x() + (screen.width() - w) // 2
        self.move(x, self.y())

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

    # ─── Drag + keyboard ───────────────────────────────────────────────────────

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
            if self.mode in ("music", "search", "system"):
                self._apply_mode("menu")
            else:
                self.collapse()
