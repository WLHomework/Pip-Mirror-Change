#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MainWindow UI construction and interactions."""
from __future__ import annotations
from typing import Any, Callable
import json

from PyQt6.QtCore import QThread, Qt, QSettings, QLocale
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QTextEdit,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QProgressBar,
    QFrame,
    QStyle,
    QApplication,
)

from . import core
from .workers import Worker

# Display names for mirrors per language
MIRROR_DISPLAY = {
    "zh": {
        "tsinghua": "清华 TUNA",
        "aliyun": "阿里云",
        "huawei": "华为云",
        "tencent": "腾讯云",
        "ustc": "中科大 USTC",
        "douban": "豆瓣",
    },
    "en": {
        "tsinghua": "Tsinghua TUNA",
        "aliyun": "Aliyun",
        "huawei": "Huawei Cloud",
        "tencent": "Tencent Cloud",
        "ustc": "USTC",
        "douban": "Douban",
    },
}

TEXTS = {
    "zh": {
        "app_title": "pip 镜像切换器 - 中国镜像",
        "title": "pip 镜像切换器",
        "subtitle": "快速切换国内镜像源 · 支持用户/环境/系统作用域",
        "mirror": "镜像源：",
        "scope": "作用域：",
        "switch": "切换为所选镜像",
        "reset": "还原默认官方源",
        "show": "查看当前配置",
        "speed": "测速并推荐",
        "log_placeholder": "日志输出将显示在这里…",
        "ready": "就绪",
        "running": "执行中…",
        "intro": (
            "欢迎使用 Pip 镜像切换器！\n"
            "- 选择镜像与作用域，点击“切换为所选镜像”。\n"
            "- 如需恢复官方源，点击“还原默认官方源”。\n"
            "- 点击“查看当前配置”可显示当前 pip 配置。\n"
            "提示：用户级无需管理员权限，系统级可能需要以管理员身份运行。华为官方镜像可能检测失败，但是可以使用。\n"
        ),
        "act_switch": "执行：切换镜像 -> {name} (scope={scope})",
        "act_reset": "执行：还原默认源 (scope={scope})",
        "act_show": "执行：查看当前配置…",
        "act_speed": "执行：镜像测速并推荐…",
        "testing_prefix": "正在测试 ",
        "testing_suffix": " 源…",
        "speed_done": "测速完成。正在计算推荐结果…",
        "rank_header": "测速结果（单位：ms，越小越好）：",
        "timeout": "超时/失败",
        "speed_finished": "测速完成",
        "fastest_is_current": "当前已是最快镜像：{name}（≈{ms:.0f}ms）",
        "recommend_text": (
            "检测到推荐镜像：{best}（≈{ms:.0f}ms）。\n"
            "当前镜像：{current}。\n\n"
            "是否切换到推荐镜像？（作用域：{scope}）"
        ),
        "apply_recommend": "应用推荐镜像",
        "lang_label": "语言：",
    },
    "en": {
        "app_title": "pip Mirror Switcher - China Mirrors",
        "title": "pip Mirror Switcher",
        "subtitle": "Quickly switch China mirrors · User/Env/System scopes",
        "mirror": "Mirror:",
        "scope": "Scope:",
        "switch": "Switch to Selected",
        "reset": "Restore Official Default",
        "show": "Show Current Config",
        "speed": "Speed Test & Recommend",
        "log_placeholder": "Logs will appear here…",
        "ready": "Ready",
        "running": "Running…",
        "intro": (
            "Welcome to the Pip Mirror Switcher!\n"
            "- Choose a mirror and scope, then click 'Switch to Selected'.\n"
            "- Click 'Restore Official Default' to revert.\n"
            "- Click 'Show Current Config' to view pip config.\n"
            "Tip: User scope needs no admin; System scope may require admin.Huawei's official image may fail to detect, but it can be used\n"
        ),
        "act_switch": "Action: Switch mirror -> {name} (scope={scope})",
        "act_reset": "Action: Reset to default (scope={scope})",
        "act_show": "Action: Show current config…",
        "act_speed": "Action: Speed test & recommendation…",
        "testing_prefix": "Testing ",
        "testing_suffix": " mirror…",
        "speed_done": "Speed test finished. Computing recommendation…",
        "rank_header": "Speed test results (ms, lower is better):",
        "timeout": "timeout/fail",
        "speed_finished": "Speed Test",
        "fastest_is_current": "Already on the fastest mirror: {name} (≈{ms:.0f}ms)",
        "recommend_text": (
            "Recommended mirror: {best} (≈{ms:.0f}ms).\n"
            "Current mirror: {current}.\n\n"
            "Switch to the recommended one? (scope: {scope})"
        ),
        "apply_recommend": "Apply Recommendation",
        "lang_label": "Language:",
    },
}

SCOPES = [
    ("user", {"zh": "用户级(推荐)", "en": "User (recommended)"}),
    ("site", {"zh": "当前环境/虚拟环境", "en": "Current env/venv"}),
    ("global", {"zh": "系统级(需管理员)", "en": "System (admin)"}),
]


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        # Load saved language preference
        settings = QSettings()
        saved = settings.value("lang", None)
        if saved in ("zh", "en"):
            self.lang = saved
        else:
            # Follow system language as default
            sys_lang = QLocale.system().language()
            if sys_lang in (
                QLocale.Language.Chinese,
                QLocale.Language.ChineseTraditional,
                QLocale.Language.ChineseSimplified,
            ):
                self.lang = "zh"
            else:
                self.lang = "en"
        self.setWindowTitle(TEXTS[self.lang]["title"])  # simplified window title
        self.setMinimumSize(820, 520)
        self._intro_shown = False
        self._init_ui()
        self._append_intro()

    def _init_ui(self) -> None:
        self.lbl_title = QLabel(TEXTS[self.lang]["title"])
        self.lbl_title.setObjectName("Title")
        self.lbl_subtitle = QLabel(TEXTS[self.lang]["subtitle"])
        self.lbl_subtitle.setObjectName("Subtitle")
        # Hide big header to reduce redundancy; we'll show subtitle in the intro area instead
        self.lbl_title.setVisible(False)
        self.lbl_subtitle.setVisible(False)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        self.lbl_mirror = QLabel(TEXTS[self.lang]["mirror"])
        self.cmb_mirror = QComboBox()
        for key in core.MIRRORS.keys():
            self.cmb_mirror.addItem(MIRROR_DISPLAY[self.lang].get(key, key), userData=key)
        self.cmb_mirror.setCurrentIndex(0)

        self.lbl_scope = QLabel(TEXTS[self.lang]["scope"])
        self.cmb_scope = QComboBox()
        for key, texts in SCOPES:
            self.cmb_scope.addItem(texts[self.lang], userData=key)
        self.cmb_scope.setCurrentIndex(0)

        self.btn_switch = QPushButton(TEXTS[self.lang]["switch"])
        self.btn_switch.setObjectName("PrimaryButton")
        self.btn_switch.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_reset = QPushButton(TEXTS[self.lang]["reset"])
        self.btn_reset.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        self.btn_show = QPushButton(TEXTS[self.lang]["show"])
        self.btn_show.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.btn_speed = QPushButton(TEXTS[self.lang]["speed"])
        self.btn_speed.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

        # Language chooser
        self.lbl_lang = QLabel(TEXTS[self.lang]["lang_label"] if "lang_label" in TEXTS[self.lang] else ("语言：" if self.lang=="zh" else "Language:"))
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItem("中文", userData="zh")
        self.cmb_lang.addItem("English", userData="en")
        # Set initial language in combo to match loaded preference
        idx = self.cmb_lang.findData(self.lang)
        if idx >= 0:
            self.cmb_lang.setCurrentIndex(idx)
        else:
            self.cmb_lang.setCurrentIndex(0)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setPlaceholderText(TEXTS[self.lang]["log_placeholder"])

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        self.status = QLabel(TEXTS[self.lang]["ready"])

        top = QGridLayout()
        top.addWidget(self.lbl_mirror, 0, 0)
        top.addWidget(self.cmb_mirror, 0, 1)
        top.addWidget(self.lbl_scope, 0, 2)
        top.addWidget(self.cmb_scope, 0, 3)
        top.addWidget(self.lbl_lang, 0, 4)
        top.addWidget(self.cmb_lang, 0, 5)

        actions = QHBoxLayout()
        actions.addWidget(self.btn_switch)
        actions.addWidget(self.btn_reset)
        actions.addWidget(self.btn_show)
        actions.addWidget(self.btn_speed)
        actions.addStretch(1)

        layout = QVBoxLayout()
        # header labels are hidden and not added to layout
        layout.addWidget(line)
        layout.addLayout(top)
        layout.addLayout(actions)
        layout.addWidget(self.txt_log, 1)
        bottom = QHBoxLayout()
        bottom.addWidget(self.status)
        bottom.addStretch(1)
        bottom.addWidget(self.progress)
        layout.addLayout(bottom)

        self.setLayout(layout)

        self.btn_switch.clicked.connect(self.on_switch)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_show.clicked.connect(self.on_show)
        self.btn_speed.clicked.connect(self.on_speedtest)
        self.cmb_lang.currentIndexChanged.connect(self.on_lang_changed)

    def _append_intro(self) -> None:
        self.txt_log.clear()
        # Show subtitle + intro as the usage instructions block
        self.txt_log.append(self._escape_html(TEXTS[self.lang]["subtitle"]))
        self.txt_log.append("")
        self.txt_log.append(TEXTS[self.lang]["intro"])  # welcome text
        self._intro_shown = True

    def _append_text(self, text: str, error: bool = False) -> None:
        # Any new output means intro is no longer the only content
        self._intro_shown = False
        if error:
            self.txt_log.append(f"<span style='color:#c00;'>{self._escape_html(text)}</span>")
        else:
            self.txt_log.append(self._escape_html(text))

    @staticmethod
    def _escape_html(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )

    # --- threading helper ---
    def _run_in_thread(self, fn: Callable, *args: Any) -> None:
        self.btn_switch.setEnabled(False)
        self.btn_reset.setEnabled(False)
        self.btn_show.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        self.progress.setVisible(True)
        self.status.setText(TEXTS[self.lang]["running"])

        self.thread = QThread(self)  # type: ignore[attr-defined]
        self.worker = Worker(fn, *args)  # type: ignore[attr-defined]
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_worker)
        self.thread.start()

    def _cleanup_worker(self) -> None:
        QApplication.restoreOverrideCursor()
        self.btn_switch.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.btn_show.setEnabled(True)
        self.progress.setVisible(False)
        # Ensure objects can be GC'ed
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _on_finished(self, msg: str) -> None:
        self._append_text(msg, error=False)
        self.status.setText(TEXTS[self.lang]["ready"])
        # Detect speedtest result marker to offer recommendation
        marker = "##RANKING_JSON "
        if marker in msg:
            try:
                line = [l for l in msg.split("\n") if l.startswith(marker)][0]
                ranking = json.loads(line[len(marker):])  # List[[name, ms], ...]
                best = next(((name, ms) for name, ms in ranking if ms != float("inf")), None)
                if not best:
                    return
                best_name, best_ms = best
                best_name_disp = MIRROR_DISPLAY[self.lang].get(best_name, best_name)
                # Identify current mirror
                current_url = core.get_effective_index_url()
                current_name = None
                if current_url:
                    for name, (url, host) in core.MIRRORS.items():
                        if host in current_url or url.rstrip('/') in current_url:
                            current_name = name
                            break
                if current_name == best_name:
                    QMessageBox.information(
                        self,
                        TEXTS[self.lang]["speed_finished"],
                        TEXTS[self.lang]["fastest_is_current"].format(name=best_name_disp, ms=best_ms),
                    )
                    return
                # Ask user to switch
                scope = self.cmb_scope.currentData()
                current_disp = (
                    MIRROR_DISPLAY[self.lang].get(current_name, current_name)
                    if current_name else ("未设置/官方默认" if self.lang == "zh" else "Not set/Official default")
                )
                text = TEXTS[self.lang]["recommend_text"].format(best=best_name_disp, ms=best_ms, current=current_disp, scope=scope)
                if QMessageBox.question(self, TEXTS[self.lang]["apply_recommend"], text) == QMessageBox.StandardButton.Yes:
                    self._append_text(TEXTS[self.lang]["act_switch"].format(name=best_name_disp, scope=scope))
                    self._run_in_thread(core.set_mirror, best_name, scope)
            except Exception:
                # Ignore parsing errors; message already printed
                pass

    def _on_failed(self, msg: str) -> None:
        self._append_text(msg, error=True)
        QMessageBox.warning(self, "Error" if self.lang == "en" else "操作失败", msg)
        self.status.setText(TEXTS[self.lang]["ready"])

    def _on_progress(self, text: str) -> None:
        # Real-time progress lines during speed test or other tasks
        self._append_text(text)

    # --- actions ---
    def on_switch(self) -> None:
        name = self.cmb_mirror.currentData()
        scope = self.cmb_scope.currentData()
        self._append_text(TEXTS[self.lang]["act_switch"].format(name=MIRROR_DISPLAY[self.lang].get(name, name), scope=scope))
        self._run_in_thread(core.set_mirror, name, scope)

    def on_reset(self) -> None:
        scope = self.cmb_scope.currentData()
        self._append_text(TEXTS[self.lang]["act_reset"].format(scope=scope))
        self._run_in_thread(core.reset_mirror, scope)

    def on_show(self) -> None:
        def _show():
            core.show_config()
        self._append_text(TEXTS[self.lang]["act_show"])
        self._run_in_thread(_show)

    def on_speedtest(self) -> None:
        def _speed(progress):
            from . import speedtest
            # Wrap progress to show Chinese display names
            def _p(msg: str) -> None:
                zh_prefix = "正在测试 "
                zh_suffix = " 源…"
                if msg.startswith(zh_prefix) and msg.endswith(zh_suffix):
                    key = msg[len(zh_prefix):-len(zh_suffix)]
                    disp = MIRROR_DISPLAY[self.lang].get(key, key)
                    msg = f"{TEXTS[self.lang]['testing_prefix']}{disp}{TEXTS[self.lang]['testing_suffix']}"
                elif msg.strip().startswith("测速完成"):
                    msg = TEXTS[self.lang]["speed_done"]
                progress(msg)

            ranking = speedtest.benchmark_mirrors(core.MIRRORS, attempts=2, timeout=3.0, progress=_p)
            # Localized ranking printout
            print(TEXTS[self.lang]["rank_header"])
            for i, (name, ms) in enumerate(ranking, 1):
                disp = MIRROR_DISPLAY[self.lang].get(name, name)
                human = (TEXTS[self.lang]["timeout"] if ms == float("inf") else f"{ms:.0f}ms")
                print(f"{i:>2}. {disp:<12}  {human}")
            print("##RANKING_JSON " + json.dumps(ranking))
        self._append_text(TEXTS[self.lang]["act_speed"])
        self._run_in_thread(_speed)

    # --- language ---
    def on_lang_changed(self) -> None:
        self.lang = self.cmb_lang.currentData()
        # Save preference
        QSettings().setValue("lang", self.lang)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.setWindowTitle(TEXTS[self.lang]["title"])  # simplified window title
        # Update static widgets
        # Title & subtitle
        self.lbl_title.setText(TEXTS[self.lang]["title"])
        self.lbl_subtitle.setText(TEXTS[self.lang]["subtitle"])
        # Rebuild mirror combo and scope labels
        # Find widgets by existing layout positions
        # Simpler: recreate mirror combo labels
        for i in range(self.cmb_mirror.count()):
            key = self.cmb_mirror.itemData(i)
            self.cmb_mirror.setItemText(i, MIRROR_DISPLAY[self.lang].get(key, key))
        # Mirror/Scope label captions
        self.lbl_mirror.setText(TEXTS[self.lang]["mirror"])
        # Scope texts
        for i, (_, texts) in enumerate(SCOPES):
            self.cmb_scope.setItemText(i, texts[self.lang])
        self.lbl_scope.setText(TEXTS[self.lang]["scope"])
        # Buttons and labels
        self.btn_switch.setText(TEXTS[self.lang]["switch"])
        self.btn_reset.setText(TEXTS[self.lang]["reset"])
        self.btn_show.setText(TEXTS[self.lang]["show"])
        self.btn_speed.setText(TEXTS[self.lang]["speed"])
        self.lbl_lang.setText(TEXTS[self.lang]["lang_label"])
        self.txt_log.setPlaceholderText(TEXTS[self.lang]["log_placeholder"])
        self.status.setText(TEXTS[self.lang]["ready"])
        # Refresh intro block if it is currently shown
        if self._intro_shown:
            self.txt_log.clear()
            self.txt_log.append(TEXTS[self.lang]["intro"])
