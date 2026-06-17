# WordFloater 源码模块

## 模块说明

| 文件 | 职责 |
|---|---|
| `__init__.py` | 包标识 |
| `__main__.py` | `python -m vcd` 入口 |
| `main.py` | `main()` 启动函数 |
| `config.py` | 路径常量、颜色主题、配置读写（兼容 PyInstaller） |
| `csv_manager.py` | CSV 解析、多编码支持、数据持久化 |
| `word_data.py` | 词库管理、随机抽题、熟练度计算 |
| `builtin.csv` | 内置单词本 + 生词本 CSV 数据 |
| `widgets/scroll_label.py` | 自动水平滚动 QLabel |
| `ui/main_window.py` | 主窗口：刷词/做题切换、顶栏按钮、底部菜单 |
| `ui/settings_dialog.py` | 设置弹窗：基本设置、单词本管理、生词本管理 |

## 数据流

1. `config.py` 加载/保存 `config.json`（设置）和定位 `builtin.csv`（数据）
2. `csv_manager.py` 读写 `builtin.csv`，提供增删改查接口
3. `word_data.py` 基于 `csv_manager` 实现词库选择、随机抽题、熟练度更新
4. `ui/main_window.py` 调用 `word_data` 获取数据，渲染到界面
5. `ui/settings_dialog.py` 提供设置修改和数据管理入口
