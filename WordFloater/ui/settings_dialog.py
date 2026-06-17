"""设置对话框：基本设置、不透明度、内置单词本管理、生词本管理、帮助"""

import os
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QSlider, QListWidget, QTextEdit,
    QFileDialog, QMessageBox, QInputDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..config import COLORS, BASE_DIR, save_config


class SettingsDialog(QDialog):
    """设置弹窗：基本参数、不透明度、单词本管理、生词本管理"""

    def __init__(self, parent):
        super().__init__(parent)
        self.pw = parent
        self.setWindowTitle("⚙️ 设置")
        self.setMinimumSize(500, 620)
        self.setStyleSheet("""
            QDialog{background:#f7fafc;}
            QSpinBox{border:2px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:15px;}
            QLineEdit{border:2px solid #e2e8f0;border-radius:6px;padding:6px 8px;font-size:15px;}
            QSlider::groove:horizontal{height:6px;background:#e2e8f0;border-radius:3px;}
            QSlider::handle:horizontal{background:#667eea;width:16px;height:16px;margin:-5px 0;border-radius:8px;}
            QListWidget{border:2px solid #e2e8f0;border-radius:6px;font-size:14px;}
        """)
        self._init_ui()

    def _init_ui(self):
        lo = QVBoxLayout(self)
        lo.setSpacing(10)
        lo.setContentsMargins(20, 20, 20, 20)

        # 标题栏带帮助按钮
        header_row = QHBoxLayout()
        settings_title = QLabel("⚙️ 设置")
        settings_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        help_btn = QPushButton("?")
        help_btn.setFixedSize(30, 30)
        help_btn.setFont(QFont("Arial", 14, QFont.Bold))
        help_btn.setStyleSheet(
            "QPushButton{background:#667eea;color:white;border:none;border-radius:15px;}"
            "QPushButton:hover{background:#5a67d8;}"
        )
        help_btn.setToolTip("关于本软件")
        help_btn.clicked.connect(self._show_about)
        header_row.addWidget(settings_title)
        header_row.addStretch()
        header_row.addWidget(help_btn)
        lo.addLayout(header_row)

        # ---- 基本设置 ----
        for label, attr, rng, suffix, val in [
            ("⏱️ 刷新间隔（秒）", 'interval_spin', (1, 60), " 秒", self.pw.settings['refresh_interval']),
            ("🔤 字体大小", 'font_spin', (12, 28), " px", self.pw.settings['font_size']),
            ("📊 每页显示个数", 'count_spin', (3, 10), " 个", self.pw.settings['words_per_page']),
        ]:
            row = QHBoxLayout()
            lb = QLabel(label)
            lb.setFont(QFont("Microsoft YaHei", 13))
            sp = QSpinBox()
            sp.setRange(*rng)
            sp.setValue(val)
            sp.setSuffix(suffix)
            sp.setFixedWidth(100)
            setattr(self, attr, sp)
            row.addWidget(lb)
            row.addStretch()
            row.addWidget(sp)
            lo.addLayout(row)

        # 不透明度
        op_row = QHBoxLayout()
        op_lb = QLabel("🔆 不透明度")
        op_lb.setFont(QFont("Microsoft YaHei", 13))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(40, 100)
        self.opacity_slider.setValue(int(self.pw.opacity * 100))
        self.opacity_val = QLabel(f"{int(self.pw.opacity * 100)}%")
        self.opacity_val.setFont(QFont("Arial", 11))
        self.opacity_val.setFixedWidth(40)
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_val.setText(f"{v}%"))
        op_row.addWidget(op_lb)
        op_row.addStretch()
        op_row.addWidget(self.opacity_slider)
        op_row.addWidget(self.opacity_val)
        lo.addLayout(op_row)

        # ---- 分隔线 ----
        sep1 = QWidget()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet("background:#e2e8f0;")
        lo.addWidget(sep1)

        # ---- 内置单词本管理 ----
        wb_header = QLabel("📚 内置单词本管理")
        wb_header.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        lo.addWidget(wb_header)

        self.wb_list = QListWidget()
        self.wb_list.setMaximumHeight(120)
        self._refresh_wb_list()
        lo.addWidget(self.wb_list)

        wb_btns = QHBoxLayout()
        add_wb_btn = QPushButton("➕ 添加单词")
        add_wb_btn.setFont(QFont("Microsoft YaHei", 12))
        add_wb_btn.setStyleSheet(
            f"QPushButton{{background:{COLORS['success']};color:white;border:none;border-radius:6px;"
            f"padding:6px 14px;font-size:13px;}}"
            "QPushButton:hover{background:#38a169;}"
        )
        add_wb_btn.clicked.connect(self._add_wb)

        del_wb_btn = QPushButton("🗑️ 删除选中")
        del_wb_btn.setFont(QFont("Microsoft YaHei", 12))
        del_wb_btn.setStyleSheet(
            f"QPushButton{{background:{COLORS['danger']};color:white;border:none;border-radius:6px;"
            f"padding:6px 14px;font-size:13px;}}"
            "QPushButton:hover{background:#e53e3e;}"
        )
        del_wb_btn.clicked.connect(self._del_wb)

        wb_btns.addWidget(add_wb_btn)
        wb_btns.addWidget(del_wb_btn)
        wb_btns.addStretch()
        lo.addLayout(wb_btns)

        # ---- 分隔线 ----
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background:#e2e8f0;")
        lo.addWidget(sep2)

        # ---- 生词本管理 ----
        vocab_header = QLabel("📝 生词本管理")
        vocab_header.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        lo.addWidget(vocab_header)

        self.vocab_list = QListWidget()
        self.vocab_list.setMaximumHeight(120)
        self._refresh_vocab_list()
        lo.addWidget(self.vocab_list)

        vocab_btns = QHBoxLayout()
        del_vocab_btn = QPushButton("🗑️ 删除选中")
        del_vocab_btn.setFont(QFont("Microsoft YaHei", 12))
        del_vocab_btn.setStyleSheet(
            f"QPushButton{{background:{COLORS['danger']};color:white;border:none;border-radius:6px;"
            f"padding:6px 14px;font-size:13px;}}"
            "QPushButton:hover{background:#e53e3e;}"
        )
        del_vocab_btn.clicked.connect(self._del_vocab)
        vocab_btns.addWidget(del_vocab_btn)
        vocab_btns.addStretch()
        lo.addLayout(vocab_btns)

        # ---- 保存按钮 ----
        lo.addStretch()
        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton("保存并关闭")
        save_btn.setFixedWidth(120)
        save_btn.setStyleSheet(
            f"QPushButton{{background:{COLORS['primary']};color:white;border:none;border-radius:8px;"
            f"padding:8px 16px;}}"
            f"QPushButton:hover{{background:{COLORS['primary_dark']};}}"
        )
        save_btn.clicked.connect(self._save)
        save_row.addWidget(save_btn)
        lo.addLayout(save_row)

    # ---- 内置单词本 ----

    def _refresh_wb_list(self):
        self.wb_list.clear()
        for w, m in self.pw.word_data.builtin_wb:
            self.wb_list.addItem(f"{w}  —  {m}")

    def _add_wb(self):
        word, ok1 = QInputDialog.getText(self, "添加单词", "单词:")
        if not ok1 or not word.strip():
            return
        meaning, ok2 = QInputDialog.getText(self, "添加释义", "释义:")
        if not ok2 or not meaning.strip():
            return
        self.pw.word_data.add_builtin_word(word.strip(), meaning.strip())
        self._refresh_wb_list()

    def _del_wb(self):
        row = self.wb_list.currentRow()
        if row < 0:
            return
        w, m = self.pw.word_data.builtin_wb[row]
        reply = QMessageBox.question(self, "确认", f"删除「{w}」？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.pw.word_data.delete_builtin_word(w)
            self._refresh_wb_list()

    # ---- 生词本 ----

    def _refresh_vocab_list(self):
        self.vocab_list.clear()
        for w, m, p in self.pw.word_data.vocab:
            stars = "⭐" * min(p, 5)
            self.vocab_list.addItem(f"{w}  —  {m}  ({stars} {p})")

    def _del_vocab(self):
        row = self.vocab_list.currentRow()
        if row < 0:
            return
        w, m, p = self.pw.word_data.vocab[row]
        reply = QMessageBox.question(self, "确认", f"从生词本删除「{w}」？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.pw.word_data.delete_vocab_word(w)
            self._refresh_vocab_list()

    # ---- 帮助 ----

    def _show_about(self):
        readme_path = os.path.join(BASE_DIR, 'README.md')
        content = "README.md 文件未找到。"
        try:
            for enc in ['utf-8-sig', 'utf-8', 'gb2312', 'gbk']:
                try:
                    with open(readme_path, 'r', encoding=enc) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
        except Exception:
            pass

        dlg = QDialog(self)
        dlg.setWindowTitle("📖 关于 - 单词悬浮窗")
        dlg.setMinimumSize(600, 500)
        dlg.setStyleSheet("QDialog{background:#f7fafc;}")
        lo = QVBoxLayout(dlg)
        lo.setContentsMargins(16, 16, 16, 16)
        lo.setSpacing(12)

        title = QLabel("📖 单词悬浮窗 — 使用说明")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet(f"color:{COLORS['primary']};")
        lo.addWidget(title)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(content)
        text_edit.setFont(QFont("Microsoft YaHei", 12))
        text_edit.setStyleSheet(
            "QTextEdit{border:2px solid #e2e8f0;border-radius:10px;padding:12px;background:white;}"
        )
        lo.addWidget(text_edit, 1)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet(
            f"QPushButton{{background:{COLORS['primary']};color:white;border:none;border-radius:8px;"
            f"padding:8px;font-size:13px;}}"
            f"QPushButton:hover{{background:{COLORS['primary_dark']};}}"
        )
        close_btn.clicked.connect(dlg.accept)
        close_row.addWidget(close_btn)
        lo.addLayout(close_row)

        dlg.exec_()

    # ---- 保存 ----

    def _save(self):
        pw = self.pw
        cfg = pw.word_data.config

        val = self.interval_spin.value()
        pw.settings['refresh_interval'] = val
        cfg['refresh_interval'] = val
        pw.timer_interval = val * 1000
        pw.timer.setInterval(pw.timer_interval)
        pw.seconds = val

        fs = self.font_spin.value()
        pw.settings['font_size'] = fs
        cfg['font_size'] = fs

        nc = self.count_spin.value()
        if nc != pw.settings['words_per_page']:
            pw.settings['words_per_page'] = nc
            cfg['words_per_page'] = nc
            pw._init_word_widgets()

        pw.opacity = self.opacity_slider.value() / 100.0
        pw.setWindowOpacity(pw.opacity)
        cfg['opacity'] = pw.opacity

        pw.word_container.setStyleSheet(
            f"QWidget#wordBubble{{background:rgba(255,255,255,{int(pw.opacity*220)});border-radius:18px;}}"
        )

        save_config(cfg)
        pw._update_count_label()

        if pw.settings['mode'] == 'brush':
            pw.refresh_content()
        else:
            pw._start_quiz()

        self.accept()
