"""CSV 文件的解析、读写、挪位补齐"""

import csv
import os
from .config import BUILTIN_CSV


# ========== 编码自动检测 ==========

ENCODINGS = ['utf-8-sig', 'utf-8', 'gb2312', 'gbk', 'gb18030']


def _open_with_encoding(filepath, mode='r'):
    """尝试多种编码打开文件，返回 (file_handle, encoding)"""
    for enc in ENCODINGS:
        try:
            f = open(filepath, mode, encoding=enc)
            # 测试读取一行
            if 'r' in mode:
                f.read(1)
                f.seek(0)
            return f, enc
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return None, None


# ========== 内置 CSV (builtin.csv) ==========

def load_builtin_csv():
    """加载 builtin.csv → (wordbook_list, vocab_list)
    5列结构: wb_word, wb_meaning, vocab_word, vocab_meaning, vocab_proficiency
    返回: (wb:[(word,meaning)|None,...], vocab:[(word,meaning,prof)|None,...])
    """
    wb = []
    vocab = []
    if not os.path.exists(BUILTIN_CSV):
        return wb, vocab

    for enc in ENCODINGS:
        try:
            with open(BUILTIN_CSV, 'r', encoding=enc) as f:
                reader = csv.reader(f)
                for row in reader:
                    w1 = row[0].strip() if len(row) > 0 else ''
                    m1 = row[1].strip() if len(row) > 1 else ''
                    w2 = row[2].strip() if len(row) > 2 else ''
                    m2 = row[3].strip() if len(row) > 3 else ''
                    p2 = row[4].strip() if len(row) > 4 else ''

                    if w1 and m1:
                        wb.append((w1, m1))
                    else:
                        wb.append(None)

                    if w2 and m2 and p2:
                        try:
                            vocab.append((w2, m2, int(p2)))
                        except ValueError:
                            vocab.append(None)
                    else:
                        vocab.append(None)
            return wb, vocab
        except UnicodeDecodeError:
            continue
        except Exception:
            return [], []
    return [], []


def save_builtin_csv(wb, vocab):
    """保存 builtin.csv，自动挪位补齐"""
    max_len = max(len(wb), len(vocab))
    with open(BUILTIN_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        for i in range(max_len):
            w1 = wb[i][0] if i < len(wb) and wb[i] else ''
            m1 = wb[i][1] if i < len(wb) and wb[i] else ''
            w2 = vocab[i][0] if i < len(vocab) and vocab[i] else ''
            m2 = vocab[i][1] if i < len(vocab) and vocab[i] else ''
            p2 = str(vocab[i][2]) if i < len(vocab) and vocab[i] else ''
            writer.writerow([w1, m1, w2, m2, p2])


# ========== 通用 CSV 解析 ==========

_HEADER_KEYWORDS = {'word', 'meaning', '单词', '释义', 'english', 'chinese', '中文', '英文'}


def _is_header(w, m):
    return w.lower() in _HEADER_KEYWORDS or m.lower() in _HEADER_KEYWORDS


def parse_csv_words(filepath):
    """解析外部 CSV 单词本
    格式: 单数列=单词，偶数列=释义，两列一组，一行可有多组
    返回: [(word, meaning), ...] 或空列表
    """
    words = []
    for enc in ENCODINGS:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                reader = csv.reader(f)
                for row in reader:
                    for i in range(0, len(row) - 1, 2):
                        w = row[i].strip()
                        m = row[i + 1].strip()
                        if w and m and not _is_header(w, m):
                            words.append((w, m))
            if words:
                print(f"加载 {len(words)} 词 from {os.path.basename(filepath)} ({enc})")
                return words
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"加载失败 {filepath}: {e}")
            return []
    return []


# ========== 工具函数 ==========

def compact_list(lst):
    """挪位补齐：移除 None，保持顺序"""
    return [x for x in lst if x is not None]
