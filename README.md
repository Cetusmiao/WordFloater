# WordFloater - 单词悬浮窗

悬浮歌词风格的桌面英语单词背诵工具，支持刷词和做题两种模式。

## 功能特性

### 刷词模式
- 每隔设定时间自动刷新显示单词和释义
- 单词/释义左右排版，超长文本自动滚动
- 点击任意一行可将单词加入生词本

### 做题模式
- 随机出题：中选英 / 英选中混合
- ABCD 四个选项，颜色反馈（绿色正确 / 红色错误）
- 答错的单词自动加入生词本

### 单词本系统
- **内置单词本**：程序自带单词表，可在设置中增删改
- **生词本**：自动收集刷词点击和做题答错的单词，带熟练度系统
- **外部辞书**：支持导入自定义 CSV 文件（每两列为一组：单词 + 释义）

### 熟练度系统
- 新加入的单词熟练度为 3（最高）
- 生词本做题：答对 -1，答错 +1
- 熟练度降为 0 时自动删除（已掌握）

## 快速开始

### 直接运行
```bash
pip install PyQt5
python run.py
```

### 打包为便携式 exe
```bash
pip install PyQt5 pyinstaller
python build.py
```
打包产物在 `dist/WordFloater.exe`，可单独拷贝运行。

## 项目结构

```
ielts/
├── run.py              # PyInstaller 打包入口
├── build.py            # 打包脚本
├── README.md           # 项目说明
├── dist/               # 打包输出
└── WordFloater/        # 源码
    ├── __init__.py
    ├── __main__.py      # python -m vcd 入口
    ├── main.py          # 启动函数
    ├── config.py        # 配置与路径管理
    ├── csv_manager.py   # CSV 解析（UTF-8 / GBK 自动检测）
    ├── word_data.py     # 数据层（词库管理、随机抽题、熟练度）
    ├── builtin.csv      # 内置单词本 + 生词本数据
    ├── widgets/
    │   └── scroll_label.py   # 自动滚动标签组件
    └── ui/
        ├── main_window.py    # 主窗口（刷词 / 做题）
        └── settings_dialog.py # 设置弹窗
```

## 外部辞书格式

CSV 文件，每两列为一组（单词 + 释义），一行可有多组：

```csv
abandon,放弃,abstract,抽象的
academic,学术的,accelerate,加速
```

支持编码：UTF-8、GBK、GB2312、GB18030。

## 内置数据格式 (builtin.csv)

5 列结构：

| 列 | 说明 |
|---|---|
| 第1列 | 内置单词本 - 单词 |
| 第2列 | 内置单词本 - 释义 |
| 第3列 | 生词本 - 单词 |
| 第4列 | 生词本 - 释义 |
| 第5列 | 生词本 - 熟练度（数字） |

删除任意一行后自动挪位补齐，不留空行。

## 依赖

- Python 3.7+
- PyQt5
- PyInstaller（仅打包时需要）
