#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Worker objects to run long tasks without blocking UI."""
from __future__ import annotations
import io
from contextlib import redirect_stdout, redirect_stderr
from typing import Callable, Any
from PyQt6.QtCore import QObject, pyqtSignal


class Worker(QObject):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, fn: Callable, *args: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args

    def run(self) -> None:
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        try:
            with redirect_stdout(buf_out), redirect_stderr(buf_err):
                # Prefer calling with a progress callback if supported
                try:
                    self.fn(self._emit_progress, *self.args)
                except TypeError:
                    self.fn(*self.args)
            out = buf_out.getvalue()
            err = buf_err.getvalue()
            msg = (out + ("\n" + err if err else "")).strip()
            if not msg:
                msg = "[OK] Done."
            self.finished.emit(msg)
        except Exception as e:
            err_full = buf_out.getvalue() + "\n" + buf_err.getvalue()
            msg = (str(e) + ("\n" + err_full if err_full.strip() else "")).strip()
            self.failed.emit(msg)

    # Callable passed into worker task to emit progress safely from worker thread
    def _emit_progress(self, text: str) -> None:
        self.progress.emit(str(text))
