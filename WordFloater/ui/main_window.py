"""主窗口：悬浮歌词风格的单词背诵工具"""

import os
import random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsDropShadowEffect,
    QFileDialog, QMessageBox, QMenu, QAction, QApplication,
)
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QFont, QColor

from ..config import COLORS, BASE_DIR
from ..word_data import WordData
from ..widgets import ScrollLabel
from .settings_dialog import SettingsDialog


class FloatingLyricWidget(QMainWindow):
    """半透明置顶悬浮单词窗口"""

    def __init__(self):
        super().__init__()
        self.word_data = WordData()
        cfg = self.word_data.config
        self.settings = {
            'font_size': cfg.get('font_size', 16),
            'words_per_page': cfg.get('words_per_page', 5),
            'refresh_interval': cfg.get('refresh_interval', 5),
            'mode': 'brush',
            'quiz_answer': None,
            'quiz_answer_word': '',
            'quiz_answer_meaning': '',
            'quiz_options': [],
            'quiz_answered': False,
        }
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.opacity = cfg.get('opacity', 0.85)
        self.timer_interval = self.settings['refresh_interval'] * 1000
        self.resize(520, 480)
        self.setMinimumSize(400, 350)
        self._center()
        self.init_ui()
        self.start_timer()

    def _center(self):
        s = QApplication.desktop().screenGeometry()
        self.move((s.width() - self.width()) // 2, (s.height() - self.height()) // 3)

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        ml = QVBoxLayout(cw)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        # ---- 顶栏 ----
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(40)
        self.top_bar.setStyleSheet("background: rgba(45,55,72,0.7);")
        tl = QHBoxLayout(self.top_bar)
        tl.setContentsMargins(15, 5, 10, 5)

        title = QLabel("📖 随机背单词")
        title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        title.setStyleSheet("color:white;background:transparent;")

        btn_s = ("QPushButton{background:rgba(255,255,255,0.2);color:white;border:none;border-radius:14px;}"
                 "QPushButton:hover{background:rgba(255,255,255,0.3);}")
        close_s = ("QPushButton{background:#fc8181;color:white;border:none;border-radius:14px;}"
                   "QPushButton:hover{background:#e53e3e;}")

        self.toggle_btn = QPushButton("  ✏️ 做题  ")
        self.toggle_btn.setFixedSize(90, 28)
        self.toggle_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.toggle_btn.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.25);color:white;border:none;border-radius:14px;}"
            "QPushButton:hover{background:rgba(255,255,255,0.35);}"
        )
        self.toggle_btn.clicked.connect(self._toggle_mode)

        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(30, 28)
        settings_btn.setFont(QFont("Arial", 12))
        settings_btn.setStyleSheet(btn_s)
        settings_btn.clicked.connect(self.open_settings)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 28)
        close_btn.setFont(QFont("Arial", 12))
        close_btn.setStyleSheet(close_s)
        close_btn.clicked.connect(self.close)

        tl.addWidget(title)
        tl.addStretch()
        tl.addWidget(self.toggle_btn)
        tl.addWidget(settings_btn)
        tl.addWidget(close_btn)

        # ---- 单词区域 ----
        self.word_container = QWidget()
        self.word_container.setStyleSheet(
            f"QWidget#wordBubble{{background:rgba(255,255,255,{int(self.opacity*220)});border-radius:18px;}}"
        )
        self.word_container.setObjectName("wordBubble")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.word_container.setGraphicsEffect(shadow)

        self.word_layout = QVBoxLayout(self.word_container)
        self.word_layout.setSpacing(6)
        self.word_layout.setContentsMargins(20, 18, 20, 18)
        self.word_widgets = []
        self.current_display_words = []
        self._init_word_widgets()

        # ---- 底栏 ----
        self.bottom_bar = QWidget()
        self.bottom_bar.setStyleSheet("background: rgba(45,55,72,0.7);")
        bl = QHBoxLayout(self.bottom_bar)
        bl.setContentsMargins(15, 8, 15, 8)

        self.countdown_label = QLabel("⏱️ 5秒后刷新")
        self.countdown_label.setFont(QFont("Arial", 10))
        self.countdown_label.setStyleSheet("color:rgba(255,255,255,0.8);background:transparent;")

        self.book_btn = QPushButton(f"📚 {self.word_data.get_active_book_name()}")
        self.book_btn.setFont(QFont("Microsoft YaHei", 10))
        self.book_btn.setCursor(Qt.PointingHandCursor)
        self.book_btn.setStyleSheet(
            "QPushButton{color:rgba(255,255,255,0.9);background:rgba(255,255,255,0.15);"
            "border:none;border-radius:12px;padding:3px 12px;}"
            "QPushButton:hover{background:rgba(255,255,255,0.25);}"
        )
        self.book_btn.setToolTip("点击切换单词本")
        self.book_btn.clicked.connect(self._show_book_menu)

        bl.addWidget(self.countdown_label)
        bl.addStretch()
        bl.addWidget(self.book_btn)

        ml.addWidget(self.top_bar)
        ml.addWidget(self.word_container, 1)
        ml.addWidget(self.bottom_bar)
        self.setWindowOpacity(self.opacity)
        self.refresh_content()

    # ---- 底部弹出菜单 ----

    def _show_book_menu(self):
        menu = QMenu(self)
        menu.setFont(QFont("Microsoft YaHei", 13))
        menu.setStyleSheet("""
            QMenu {
                background: #2d3748; color: white;
                border: 1px solid #4a5568; border-radius: 8px;
                padding: 5px; font-size: 14px;
            }
            QMenu::item { padding: 10px 24px; border-radius: 4px; }
            QMenu::item:selected { background: #4a5568; }
            QMenu::separator { height: 1px; background: #4a5568; margin: 4px 8px; }
        """)

        wb_act = QAction(f"📚 内置单词本 ({len(self.word_data.builtin_wb)} 词)", self)
        wb_act.triggered.connect(lambda: self._switch_source('builtin'))
        menu.addAction(wb_act)

        vocab_act = QAction(f"📝 生词本 ({len(self.word_data.vocab)} 词)", self)
        vocab_act.triggered.connect(lambda: self._switch_source('vocab'))
        menu.addAction(vocab_act)

        ext_books = self.word_data.config.get('word_books', [])
        if ext_books:
            menu.addSeparator()
            for path in ext_books:
                abs_path = os.path.abspath(path)
                name = os.path.splitext(os.path.basename(path))[0]
                count = len(self.word_data.books.get(abs_path, []))
                act = QAction(f"📖 {name} ({count} 词)", self)
                act.triggered.connect(lambda checked, p=abs_path: self._switch_source(p))
                menu.addAction(act)

        menu.addSeparator()
        add_act = QAction("➕ 导入辞书...", self)
        add_act.triggered.connect(self._import_book)
        menu.addAction(add_act)

        btn_pos = self.book_btn.mapToGlobal(QPoint(0, 0))
        menu.exec_(QPoint(btn_pos.x(), btn_pos.y() - menu.sizeHint().height()))

    def _switch_source(self, source):
        self.word_data.switch_source(source)
        self._update_count_label()
        if self.settings['mode'] == 'brush':
            self.refresh_content()
        else:
            self._init_word_widgets()
            self._start_quiz()

    def _import_book(self):
        fp, _ = QFileDialog.getOpenFileName(self, "选择CSV单词本", BASE_DIR, "CSV (*.csv);;所有 (*)")
        if not fp:
            return
        count = self.word_data.add_book(fp)
        if count == 0:
            QMessageBox.warning(self, "⚠️", "无法解析该文件")
            return
        self._switch_source(os.path.abspath(fp))

    def _update_count_label(self):
        self.book_btn.setText(f"📚 {self.word_data.get_active_book_name()}")

    # ---- 模式切换 ----

    def _toggle_mode(self):
        if self.settings['mode'] == 'brush':
            self.settings['mode'] = 'quiz'
            self.toggle_btn.setText("  📚 刷词  ")
            self.toggle_btn.setStyleSheet(
                "QPushButton{background:rgba(72,187,120,0.7);color:white;border:none;border-radius:14px;}"
                "QPushButton:hover{background:rgba(72,187,120,0.9);}"
            )
            self._init_word_widgets()
            self._start_quiz()
        else:
            self.settings['mode'] = 'brush'
            self.toggle_btn.setText("  ✏️ 做题  ")
            self.toggle_btn.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.25);color:white;border:none;border-radius:14px;}"
                "QPushButton:hover{background:rgba(255,255,255,0.35);}"
            )
            self._init_word_widgets()
            self._update_count_label()
            self.refresh_content()

    # ---- 单词组件 ----

    def _init_word_widgets(self):
        while self.word_layout.count():
            item = self.word_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.word_widgets.clear()

        count = self.settings['words_per_page']
        fs = self.settings['font_size']
        is_quiz = self.settings['mode'] == 'quiz'

        for i in range(count):
            rw = QWidget()
            rw.setStyleSheet("background:transparent;")
            rw.setCursor(Qt.ArrowCursor)
            rw.mousePressEvent = lambda e, idx=i: self._on_row_click(idx)
            rl = QHBoxLayout(rw)
            rl.setContentsMargins(8, 4, 8, 4)
            rl.setSpacing(12)

            ml = ScrollLabel()
            ml.setFont(QFont("Arial", fs, QFont.Bold))
            ml.setStyleSheet(f"color:{COLORS['primary']};background:transparent;")

            if is_quiz:
                rl.addWidget(ml, 1)
                self.word_widgets.append((ml, None, rw))
            else:
                sl = ScrollLabel()
                sl.setFont(QFont("Microsoft YaHei", max(fs - 4, 10)))
                sl.setStyleSheet(f"color:{COLORS['text_secondary']};background:transparent;")
                rl.addWidget(ml, 1)
                rl.addWidget(sl, 2)
                self.word_widgets.append((ml, sl, rw))

            self.word_layout.addWidget(rw)
            if i < count - 1:
                sep = QWidget()
                sep.setFixedHeight(1)
                sep.setStyleSheet("background:rgba(0,0,0,0.08);")
                self.word_layout.addWidget(sep)

    # ---- 行点击 ----

    def _on_row_click(self, index):
        # 刷词模式：点击加入生词本
        if self.settings['mode'] == 'brush':
            if index < len(self.current_display_words):
                w, m = self.current_display_words[index]
                if self.word_data.active_source != 'vocab':
                    self.word_data.add_vocab(w, m)
            return

        # 做题模式
        if self.settings['mode'] != 'quiz' or self.settings['quiz_answered']:
            return
        if index == 0 or index - 1 >= len(self.settings['quiz_options']):
            return

        clicked = self.settings['quiz_options'][index - 1]
        answer = self.settings['quiz_answer']
        self.settings['quiz_answered'] = True

        # 答错加入生词本
        if clicked != answer:
            w = self.settings['quiz_answer_word']
            m = self.settings['quiz_answer_meaning']
            if self.word_data.active_source != 'vocab':
                self.word_data.add_vocab(w, m)

        # 生词本做题：调整熟练度
        if self.word_data.active_source == 'vocab':
            if clicked == answer:
                self.word_data.vocab_correct(self.settings['quiz_answer_word'])
            else:
                self.word_data.vocab_wrong(self.settings['quiz_answer_word'])

        # 颜色反馈
        for i, (ml, sl, rw) in enumerate(self.word_widgets):
            if i == 0:
                continue
            if i - 1 >= len(self.settings['quiz_options']):
                break
            opt = self.settings['quiz_options'][i - 1]
            if opt == answer:
                ml.setStyleSheet("color:white;background:#48bb78;font-weight:bold;")
                rw.setStyleSheet("background:#48bb78;border-radius:8px;")
            elif i == index:
                ml.setStyleSheet("color:white;background:#fc8181;")
                rw.setStyleSheet("background:#fc8181;border-radius:8px;")
            else:
                ml.setStyleSheet("color:#a0aec0;background:transparent;")
                rw.setStyleSheet("background:transparent;")

        QTimer.singleShot(1500, self._start_quiz)

    # ---- 定时器 ----

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_content)
        self.timer.start(self.timer_interval)
        self.seconds = self.timer_interval // 1000
        self.countdown = QTimer()
        self.countdown.timeout.connect(self._tick)
        self.countdown.start(1000)

    def _tick(self):
        self.seconds -= 1
        if self.seconds <= 0:
            self.seconds = self.timer_interval // 1000
        self.countdown_label.setText(f"⏱️ {self.seconds}秒后刷新")

    # ---- 刷词 ----

    def refresh_content(self):
        if self.settings['mode'] == 'quiz':
            return
        self.seconds = self.timer_interval // 1000
        words = self.word_data.get_random_words(self.settings['words_per_page'])
        self.current_display_words = words
        for i, (ml, sl, rw) in enumerate(self.word_widgets):
            ml.setStyleSheet(f"color:{COLORS['primary']};background:transparent;")
            sl.setStyleSheet(f"color:{COLORS['text_secondary']};background:transparent;")
            if i < len(words):
                ml.setText(words[i][0])
                sl.setText(words[i][1])
                ml.setToolTip(words[i][0])
                sl.setToolTip(words[i][1])
            else:
                ml.setText("")
                sl.setText("")
                ml.setToolTip("")
                sl.setToolTip("")

    # ---- 做题 ----

    def _start_quiz(self):
        self._update_count_label()
        words = self.word_data.get_random_words(self.settings['words_per_page'])
        if len(words) < 2:
            for ml, sl, rw in self.word_widgets:
                ml.setText("📭 单词不足，需要至少2个")
                ml.setStyleSheet(f"color:{COLORS['text_secondary']};background:transparent;")
            return

        direction = random.choice(['cn_to_en', 'en_to_cn'])
        target = words[0]
        pool = words[:min(len(words), self.settings['words_per_page'])]
        random.shuffle(pool)

        if direction == 'cn_to_en':
            question = target[1]
            options = [w[0] for w in pool]
            answer = target[0]
        else:
            question = target[0]
            options = [w[1] for w in pool]
            answer = target[1]

        self.settings['quiz_answer'] = answer
        self.settings['quiz_answer_word'] = target[0]
        self.settings['quiz_answer_meaning'] = target[1]
        self.settings['quiz_options'] = options
        self.settings['quiz_answered'] = False

        for i, (ml, sl, rw) in enumerate(self.word_widgets):
            ml.setToolTip("")
            ml.setStyleSheet(f"color:{COLORS['primary']};background:transparent;")
            rw.setStyleSheet("background:transparent;")
            rw.setCursor(Qt.ArrowCursor)
            if i == 0:
                prefix = "🇨🇳" if direction == 'cn_to_en' else "🇬🇧"
                ml.setText(f"{prefix}  {question}")
                ml.setStyleSheet("color:#1a202c;background:rgba(0,0,0,0.05);")
            elif i - 1 < len(options):
                ml.setText(f"  {'ABCD'[i-1]}.  {options[i-1]}")
                rw.setCursor(Qt.PointingHandCursor)
            else:
                ml.setText("")

        self.countdown_label.setText("✏️ 点击选项作答")

    # ---- 设置 ----

    def open_settings(self):
        SettingsDialog(self).exec_()

    # ---- 拖拽 ----

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()
