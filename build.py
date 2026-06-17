"""PyInstaller 打包脚本：将 vcd 打包为单文件 exe"""
import PyInstaller.__main__
import os

BASE = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    os.path.join(BASE, 'run.py'),
    '--onefile',
    '--windowed',
    '--name', 'WordFloater',
    '--distpath', os.path.join(BASE, 'dist'),
    '--workpath', os.path.join(BASE, 'build'),
    '--specpath', BASE,
    '--add-data', f'{os.path.join(BASE, "WordFloater", "builtin.csv")};.',
    '--clean',
])
