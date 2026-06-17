"""滚动标签组件：文字超出宽度时自动水平无缝循环滚动"""

import re
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QFontMetrics, QPainter


class ScrollLabel(QWidget):
    """文字超出宽度时自动水平无缝循环滚动的标签"""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text or ""
        self._offset = 0.0
        self._speed = 1.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._color = QColor("#667eea")
        self._font = QFont("Arial", 14)
        self._need_scroll = False
        self._pause_frames = 0
        self.setMinimumHeight(24)

    def setText(self, text):
        self._text = text or ""
        self._offset = 0.0
        self._pause_frames = 0
        self._timer.stop()
        self._need_scroll = False
        self.update()
        QTimer.singleShot(50, self._check_scroll)

    def text(self):
        return self._text

    def setFont(self, font):
        self._font = font
        self.update()
        QTimer.singleShot(50, self._check_scroll)

    def setStyleSheet(self, style):
        super().setStyleSheet(style)
        m = re.search(r'color:\s*([^;]+)', style)
        if m:
            try:
                self._color = QColor(m.group(1).strip())
            except Exception:
                pass

    def setAlignment(self, a):
        pass

    def setWordWrap(self, b):
        pass

    def setTextInteractionFlags(self, f):
        pass

    def _check_scroll(self):
        if not self._text:
            return
        fm = QFontMetrics(self._font)
        if fm.horizontalAdvance(self._text) > self.width() + 2:
            self._need_scroll = True
            if not self._timer.isActive():
                self._offset = 0.0
                self._pause_frames = 45
                self._timer.start(30)
        else:
            self._need_scroll = False
            self._timer.stop()
            self._offset = 0.0
            self.update()

    def _tick(self):
        if not self._text:
            return
        if self._pause_frames > 0:
            self._pause_frames -= 1
            self.update()
            return
        fm = QFontMetrics(self._font)
        total = fm.horizontalAdvance(self._text) + 60
        self._offset += self._speed
        if self._offset >= total:
            self._offset = 0.0
            self._pause_frames = 45
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self._font)
        painter.setPen(self._color)
        fm = QFontMetrics(self._font)
        tw = fm.horizontalAdvance(self._text)
        y = (self.height() + fm.ascent() - fm.descent()) // 2
        if not self._need_scroll or tw <= self.width():
            painter.drawText(4, y, self._text)
        else:
            x = -int(self._offset)
            painter.drawText(x, y, self._text)
            painter.drawText(x + tw + 60, y, self._text)
        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._check_scroll()

    def minimumSizeHint(self):
        return QSize(0, QFontMetrics(self._font).height() + 4)
