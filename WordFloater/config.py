"""全局配置：路径常量、颜色主题、配置文件读写

兼容 PyInstaller 打包：config.json 保存在 exe 所在目录，
builtin.csv 首次运行时从内嵌资源复制到 exe 目录，之后用户增删改都在 exe 目录操作。
"""

import os
import sys
import json
import shutil

# ========== 路径 ==========

# PyInstaller 打包后：exe 所在目录（持久化数据目录）
# 开发环境：本文件所在目录
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    # PyInstaller --onefile 解压到的临时目录
    _RESOURCE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _RESOURCE_DIR = BASE_DIR

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
BUILTIN_CSV = os.path.join(BASE_DIR, 'builtin.csv')

# 首次运行：从内嵌资源复制 builtin.csv 到 exe 目录
if getattr(sys, 'frozen', False) and not os.path.exists(BUILTIN_CSV):
    _src = os.path.join(_RESOURCE_DIR, 'builtin.csv')
    if os.path.exists(_src):
        shutil.copy2(_src, BUILTIN_CSV)

# ========== 颜色主题 ==========

COLORS = {
    'primary': '#667eea',
    'primary_dark': '#5a67d8',
    'success': '#48bb78',
    'danger': '#fc8181',
    'text_secondary': '#718096',
}


# ========== 工具函数 ==========

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)


def load_config():
    default = {
        'font_size': 16,
        'words_per_page': 5,
        'refresh_interval': 5,
        'opacity': 0.85,
        'word_books': [],
        'active_book': '',
        'active_source': 'builtin',
    }
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            default.update(json.load(f))
    except Exception:
        pass
    return default


def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
