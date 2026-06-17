"""入口点：启动应用程序"""

import sys
from PyQt5.QtWidgets import QApplication
from .ui.main_window import FloatingLyricWidget


def main():
    app = QApplication(sys.argv)
    w = FloatingLyricWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
