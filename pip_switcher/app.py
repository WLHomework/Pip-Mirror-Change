#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application entry point."""
from __future__ import annotations
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from .style import apply_modern_style, apply_dark_titlebar
from .ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("PipMirrorSwitcher")
    QCoreApplication.setOrganizationDomain("example.local")
    QCoreApplication.setApplicationName("PipMirrorSwitcher")
    apply_modern_style(app)
    w = MainWindow()
    # Attempt to match title bar to dark theme on Windows
    apply_dark_titlebar(w)
    w.show()
    return app.exec()
