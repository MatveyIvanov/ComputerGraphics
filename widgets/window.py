from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from widgets.widgets import Menu, Visualization

MIN_SIZE = (1280, 720)
DARK_THEME_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255, 0.87)


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graphics")
        self.setFixedSize(MIN_SIZE[0], MIN_SIZE[1])

        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(qRgb(*DARK_THEME_COLOR)))
        self.setPalette(p)

        self.menu_widget = Menu(
            self, fixed_size=QSize(self.width() // 5, self.height())
        )
        self.visualization_widget = Visualization(
            self,
            geometry=QRect(
                QPoint(self.width() // 5, 0), QSize(4 / 5 * self.width(), self.height())
            ),
        )
        self.connect_widgets_pages(self.menu_widget, self.visualization_widget)

    def connect_widgets_pages(self, w1, w2):
        for i in range(len(w1.pages)):
            w1.pages[i].setSibling(w2.pages[i])
            w2.pages[i].setSibling(w1.pages[i])
