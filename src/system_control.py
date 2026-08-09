"""
Windows system control helpers for Fhish's View.

- Volume  → pycaw (actual master volume)
- Brightness → screen-brightness-control (laptop panels)
- Wi-Fi / Bluetooth / Focus / Night Light → open Windows Settings pages
  (full radio toggle often needs admin; Settings is the reliable path)
"""

from __future__ import annotations

import subprocess
import sys
from typing import Optional


def _is_windows() -> bool:
    return sys.platform == "win32"


# ─── Volume ────────────────────────────────────────────────────────────────────

def get_volume() -> Optional[int]:
    """Return master volume 0–100, or None if unavailable."""
    if not _is_windows():
        return None
    try:
        from pycaw.pycaw import AudioUtilities

        device = AudioUtilities.GetSpeakers()
        # Newer pycaw exposes volume_percent; fall back to scalar API
        if hasattr(device, "volume_percent"):
            return int(round(device.volume_percent))

        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import IAudioEndpointVolume

        interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return int(round(volume.GetMasterVolumeLevelScalar() * 100))
    except Exception:
        return None


def set_volume(percent: int) -> bool:
    """Set master volume 0–100. Returns True on success."""
    if not _is_windows():
        return False
    percent = max(0, min(100, int(percent)))
    try:
        from pycaw.pycaw import AudioUtilities

        device = AudioUtilities.GetSpeakers()
        if hasattr(device, "volume_percent"):
            device.volume_percent = percent
            return True

        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import IAudioEndpointVolume

        interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
        return True
    except Exception:
        return False


# ─── Brightness ────────────────────────────────────────────────────────────────

def get_brightness() -> Optional[int]:
    """Return display brightness 0–100, or None if unsupported (e.g. external monitor)."""
    if not _is_windows():
        return None
    try:
        import screen_brightness_control as sbc

        vals = sbc.get_brightness()
        if isinstance(vals, list):
            return int(vals[0]) if vals else None
        return int(vals)
    except Exception:
        return None


def set_brightness(percent: int) -> bool:
    """Set display brightness 0–100. Returns True on success."""
    if not _is_windows():
        return False
    percent = max(0, min(100, int(percent)))
    try:
        import screen_brightness_control as sbc

        sbc.set_brightness(percent)
        return True
    except Exception:
        return False


# ─── Settings deep-links (no admin required) ───────────────────────────────────

_SETTINGS = {
    "wifi": "ms-settings:network-wifi",
    "bluetooth": "ms-settings:bluetooth",
    "focus": "ms-settings:quiethours",       # Focus Assist / Do Not Disturb
    "night_light": "ms-settings:nightlight",
}


def open_setting(key: str) -> bool:
    """Open a Windows Settings page. key: wifi | bluetooth | focus | night_light."""
    if not _is_windows():
        return False
    uri = _SETTINGS.get(key)
    if not uri:
        return False
    try:
        # start is a shell built-in — use cmd /c
        subprocess.Popen(["cmd", "/c", "start", "", uri], shell=False)
        return True
    except Exception:
        return False


def capabilities() -> dict:
    """Report what this machine can control."""
    return {
        "volume": get_volume() is not None,
        "brightness": get_brightness() is not None,
        "settings": _is_windows(),
    }
