from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys
from widgets.window import Window


if __name__ == "__main__":
    app = QApplication([])

    window = Window()
    window.show()

    sys.exit(app.exec_())
