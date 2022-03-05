from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from widgets.BezierWidget import BezierMenuWidget, BezierVisualizationWidget
from widgets.RayTracing import RayTracingMenuWidget, RayTracingVisualizationWidget


VISUALIZATION_BG_COLOR = (50, 50, 50)
COORDINATE_SYSTEM_COLOR = (204, 98, 98)
WIDGET_BG_COLOR = (36, 36, 36)
TEXT_COLOR = (255, 255, 255, 0.87)
SPLINE_COLOR = (77, 172, 189)
POINT_COLOR = (181, 51, 51)
SELECTION_BG_COLOR = 242424

PADDING = 25
PEN_WIDTH = 1
SPINBOX_STEP = 0.1
MINIMUM_POINTS = 3
MAXIMUM_POINTS = 15
SCALE_VELOCITY = 4

MENU_WIDGETS = {}

VISUALIZATION_WIDGETS = {}


class Visualization(QWidget):
    """Visualization widget is responsible for drawing object(s) selected in Menu widget"""

    def __init__(self, parent, geometry: QRect = None):
        super().__init__(parent)

        if geometry:
            self.setGeometry(geometry)

        self.initUI()

    def initUI(self):
        self.setAutoFillBackground(True)

        self.stackedLayout = QStackedLayout()

        self.pages = []
        # Create pages
        self.pages.append(BezierVisualizationWidget(self, geometry=self.geometry()))
        self.pages.append(RayTracingVisualizationWidget(self, geometry=self.geometry()))

        for page in self.pages:
            self.stackedLayout.addWidget(page)

        # Add the combo box and the stacked layout to the top-level layout
        self.setLayout(self.stackedLayout)


class Menu(QWidget):
    """Menu widget is responsible for allowing the user to select the object they wish to visualize and for allowing the user to manimulate the parameters of the selected object"""

    def __init__(self, parent: QWidget, fixed_size: QSize = None):
        super().__init__(parent)

        if fixed_size:
            self.setFixedSize(fixed_size)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet(
            f"color: rgba({TEXT_COLOR[0]},{TEXT_COLOR[1]},{TEXT_COLOR[2]},{TEXT_COLOR[3]});"
        )
        # Create and connect the combo box to switch between pages
        self.pageCombo = QComboBox()

        self.pageCombo.addItems(["Кривая Безье", "Другое"])
        self.pageCombo.setStyleSheet(
            f"background-color: rgb({WIDGET_BG_COLOR[0]},{WIDGET_BG_COLOR[1]},{WIDGET_BG_COLOR[2]}); selection-background-color: #{SELECTION_BG_COLOR};"
        )
        self.pageCombo.activated.connect(self.switchPage)

        # Create the stacked layout
        self.stackedLayout = QStackedLayout()

        self.pages = []
        # Create pages
        self.pages.append(
            BezierMenuWidget(self, fixed_size=QSize(self.width(), self.height()))
        )
        self.pages.append(
            RayTracingMenuWidget(self, fixed_size=QSize(self.width(), self.height()))
        )

        for page in self.pages:
            self.stackedLayout.addWidget(page)

        # Add the combo box and the stacked layout to the top-level layout
        layout.addWidget(self.pageCombo)
        layout.addLayout(self.stackedLayout)

    def switchPage(self):
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())
        self.parent().visualization_widget.stackedLayout.setCurrentIndex(
            self.pageCombo.currentIndex()
        )
