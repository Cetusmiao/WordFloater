"""单词数据管理：WordData 类
管理内置单词本、生词本、外部辞书的加载、切换、增删。
"""

import os
import random
from .config import load_config, save_config
from .csv_manager import (
    load_builtin_csv, save_builtin_csv,
    parse_csv_words, compact_list,
)


class WordData:
    """单词数据管理器"""

    def __init__(self):
        self.config = load_config()
        self.books = {}           # {abs_path: [(word, meaning), ...]}
        self.active_words = []    # 当前激活源的单词列表
        self.active_source = self.config.get('active_source', 'builtin')

        # 内置数据
        wb_raw, vocab_raw = load_builtin_csv()
        self.builtin_wb = compact_list(wb_raw)       # [(word, meaning)]
        self.vocab = compact_list(vocab_raw)          # [(word, meaning, proficiency)]

        self._load_all_books()
        self._refresh_active()

    # ---- 激活源切换 ----

    def switch_source(self, source):
        """切换激活源: 'builtin', 'vocab', 或外部文件路径"""
        self.active_source = source
        self.config['active_source'] = source
        save_config(self.config)
        self._refresh_active()

    def _refresh_active(self):
        src = self.active_source
        if src == 'builtin':
            self.active_words = [(w, m) for w, m in self.builtin_wb]
        elif src == 'vocab':
            self.active_words = [(w, m) for w, m, p in self.vocab]
        elif src in self.books:
            self.active_words = self.books[src]
        else:
            self.active_words = []

    def get_active_book_name(self):
        src = self.active_source
        if src == 'builtin':
            return f"内置单词本({len(self.builtin_wb)})"
        elif src == 'vocab':
            return f"生词本({len(self.vocab)})"
        elif src in self.books:
            return os.path.splitext(os.path.basename(src))[0]
        return '未选择'

    def get_random_words(self, count=5):
        src = self.active_words
        if not src:
            return []
        if len(src) < count:
            return src.copy()
        return random.sample(src, count)

    # ---- 外部单词本 ----

    def add_book(self, filepath):
        abs_path = os.path.abspath(filepath)
        if abs_path in self.books:
            return len(self.books[abs_path])
        words = parse_csv_words(abs_path)
        if not words:
            return 0
        self.books[abs_path] = words
        if abs_path not in self.config['word_books']:
            self.config['word_books'].append(abs_path)
            save_config(self.config)
        return len(words)

    def remove_book(self, filepath):
        abs_path = os.path.abspath(filepath)
        self.books.pop(abs_path, None)
        if abs_path in self.config['word_books']:
            self.config['word_books'].remove(abs_path)
        if self.config['active_book'] == abs_path:
            self.config['active_book'] = ''
        save_config(self.config)

    def _load_all_books(self):
        for path in list(self.config['word_books']):
            abs_path = os.path.abspath(path)
            words = parse_csv_words(abs_path)
            if words:
                self.books[abs_path] = words
            else:
                self.config['word_books'].remove(path)
        save_config(self.config)

    # ---- 内置单词本增删（自动挪位补齐） ----

    def add_builtin_word(self, word, meaning):
        self.builtin_wb.append((word, meaning))
        self._sync()
        if self.active_source == 'builtin':
            self.active_words = [(w, m) for w, m in self.builtin_wb]

    def delete_builtin_word(self, word):
        self.builtin_wb = [(w, m) for w, m in self.builtin_wb if w != word]
        self._sync()
        if self.active_source == 'builtin':
            self.active_words = [(w, m) for w, m in self.builtin_wb]

    # ---- 生词本增删（熟练度系统） ----

    def add_vocab(self, word, meaning):
        """添加单词到生词本，熟练度=3，去重"""
        for w, m, p in self.vocab:
            if w == word:
                return  # 已存在
        self.vocab.append((word, meaning, 3))
        self._sync()
        if self.active_source == 'vocab':
            self.active_words = [(w, m) for w, m, p in self.vocab]

    def vocab_correct(self, word):
        """做对：熟练度-1，为0时删除"""
        for i, (w, m, p) in enumerate(self.vocab):
            if w == word:
                new_p = p - 1
                if new_p <= 0:
                    self.vocab.pop(i)
                else:
                    self.vocab[i] = (w, m, new_p)
                self._sync()
                if self.active_source == 'vocab':
                    self.active_words = [(w, m) for w, m, p in self.vocab]
                return
        self.vocab = compact_list(self.vocab)

    def vocab_wrong(self, word):
        """做错：熟练度+1"""
        for i, (w, m, p) in enumerate(self.vocab):
            if w == word:
                self.vocab[i] = (w, m, min(p + 1, 99))
                self._sync()
                return

    def delete_vocab_word(self, word):
        self.vocab = [(w, m, p) for w, m, p in self.vocab if w != word]
        self._sync()
        if self.active_source == 'vocab':
            self.active_words = [(w, m) for w, m, p in self.vocab]

    # ---- 同步保存 ----

    def _sync(self):
        save_builtin_csv(self.builtin_wb, self.vocab)
