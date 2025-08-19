#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application-wide styling (Fusion dark theme + stylesheet)."""
from __future__ import annotations
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor


def apply_modern_style(app: QApplication) -> None:
    QApplication.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(40, 44, 52))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Base, QColor(33, 37, 43))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(44, 49, 58))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Button, QColor(52, 58, 64))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(33, 150, 243))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QWidget { font-size: 14px; }
        QLabel#Title { font-size: 22px; font-weight: 700; color: #E6E6E6; }
        QLabel#Subtitle { font-size: 13px; color: #AAB2BF; margin-bottom: 4px; }

        QGroupBox { border: 1px solid #3C4048; border-radius: 8px; margin-top: 12px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }

        QComboBox, QTextEdit {
            border: 1px solid #3C4048; border-radius: 6px; padding: 6px; background: #2B2F36; color: #E6E6E6;
        }
        QComboBox::drop-down { border: 0; }

        QPushButton { border: 1px solid #3C4048; border-radius: 6px; padding: 8px 14px; background: #2F343C; color: #EDEDED; }
        QPushButton:hover { background: #3A4049; }
        QPushButton:disabled { color: #888; border-color: #2E3238; }
        QPushButton#PrimaryButton { background: #2B6CB0; border-color: #2B6CB0; }
        QPushButton#PrimaryButton:hover { background: #2F79C6; }

        QProgressBar { border: 1px solid #3C4048; border-radius: 6px; height: 10px; }
        QProgressBar::chunk { background: #2196F3; border-radius: 6px; }
        """
    )


# ---- Windows title bar dark mode ----
def apply_dark_titlebar(window) -> None:
    """
    Try to set a dark title bar on Windows 10/11 using DwmSetWindowAttribute.
    Safe no-op on non-Windows or when the API is unavailable.
    """
    import sys as _sys
    if _sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        hwnd = int(window.winId())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 10 1903+
        DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19  # Windows 10 1809

        dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)

        def _set_attr(attr: int, value: int) -> bool:
            val = ctypes.c_int(value)
            res = dwmapi.DwmSetWindowAttribute(wintypes.HWND(hwnd), ctypes.c_uint(attr), ctypes.byref(val), ctypes.sizeof(val))
            return res == 0

        if not _set_attr(DWMWA_USE_IMMERSIVE_DARK_MODE, 1):
            _set_attr(DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, 1)
    except Exception:
        # Quietly ignore; title bar will remain system default
        pass
