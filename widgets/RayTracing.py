from time import time
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PIL import Image
from utils.raytracing import render_image
import os


class RayTracingMenuWidget(QWidget):
    def __init__(self, parent: QWidget, fixed_size: QSize = None) -> None:
        super().__init__(parent)

        if fixed_size:
            self.setFixedSize(fixed_size)

        self.initUI()

    def initUI(self):
        self.Layout = QFormLayout(spacing=10)

        self.load_button = QPushButton("Load ray tracing")
        self.load_button.clicked.connect(self.load)
        self.Layout.addWidget(self.load_button)

        self.setLayout(self.Layout)

        self._sibling = None

    def setSibling(self, s):
        self._sibling = s

    def load(self):
        if self._sibling:
            self._sibling.load()


class RayTracingVisualizationWidget(QWidget):
    def __init__(self, parent: QWidget, geometry: QRect = None) -> None:
        super().__init__(parent)

        if geometry:
            self.setGeometry(geometry)

        self.initUI()

    def initUI(self):
        self.rendered = None

        self._sibling = None

    def setSibling(self, s):
        self._sibling = s

    def load(self):
        start = time()
        os.system("cd ../RayTracing/build/Debug/ && tinyraytracer")

        im = Image.open("utils/out.ppm")
        im.save("utils/out.png")

        self.pic = QLabel(self)
        self.pic.setPixmap(QPixmap("utils/out.png"))

        self.pic.show()
        print(time() - start)

    def paintEvent(self, event):
        pass

    def render(self):
        if not self.rendered:
            self.rendered = render_image(self.width(), self.height())
            for i in range(self.pixmap.width()):
                for j in range(self.pixmap.height()):
                    self.pixmap.setPixel(
                        i,
                        j,
                        QColor(
                            self.rendered[i][j][0],
                            self.rendered[i][j][1],
                            self.rendered[i][j][2],
                        ).rgb(),
                    )
