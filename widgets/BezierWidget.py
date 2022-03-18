from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import utils.splines as spl

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


class BezierMenuWidget(QWidget):
    def __init__(self, parent: QWidget, fixed_size: QSize = None) -> None:
        super().__init__(parent)

        if fixed_size:
            self.setFixedSize(fixed_size)

        self.initUI()

    def initUI(self):
        self.setStyleSheet(
            f"color: rgba({TEXT_COLOR[0]},{TEXT_COLOR[1]},{TEXT_COLOR[2]},{TEXT_COLOR[3]});"
        )
        self.Layout = QFormLayout(spacing=10)
        self.num_of_points = QSpinBox()
        self.num_of_points.setStyleSheet(
            f"background-color: rgb({WIDGET_BG_COLOR[0]},{WIDGET_BG_COLOR[1]},{WIDGET_BG_COLOR[2]});"
        )
        self.num_of_points.setValue(MINIMUM_POINTS)
        self.num_of_points.valueChanged.connect(self.numberOfPointsChanged)
        self.num_of_points.setMinimum(MINIMUM_POINTS)
        self.num_of_points.setMaximum(MAXIMUM_POINTS)

        self.Layout.addWidget(QLabel("Number of points:"))
        self.Layout.addWidget(self.num_of_points)

        self.pointsWidget = QWidget()
        self.pointsLayout = QGridLayout(spacing=10)

        self.points = []
        self.coords = [[0, 0], [0, 0], [0, 0]]
        self.check_boxes = []
        self.toggled = [True] * MAXIMUM_POINTS
        self.updatePointsSB()

        self.pointsWidget.setLayout(self.pointsLayout)
        self.Layout.addWidget(self.pointsWidget)
        self.setLayout(self.Layout)

        self._sibling = None

    def setSibling(self, s):
        self._sibling = s

    def numberOfPointsChanged(self):
        """Called when attribute 'num_of_points' has been changed"""

        for i in reversed(range(self.pointsLayout.count())):
            self.pointsLayout.itemAt(i).widget().setParent(None)
        self.points.clear()
        self.check_boxes.clear()

        self.enableUnvisibleCheckBoxes()
        self.updatePointsSB()
        self.anyPointChanged()

    def updatePointsSB(self):
        """Method that updates widgets for points input when number of points has been changed"""

        cur_row = 0
        self.check_boxes.append(QCheckBox())
        if self.toggled[0]:
            self.check_boxes[-1].toggle()
        self.pointsLayout.addWidget(self.check_boxes[-1], cur_row, 0)
        for i in range(self.num_of_points.value() * 2):
            if i % 2 == 0 and i != 0:
                # Add check box for every row (point)
                cur_row += 1

                self.check_boxes.append(QCheckBox())
                if self.toggled[len(self.check_boxes) - 1]:
                    self.check_boxes[-1].toggle()
                self.check_boxes[-1].toggled.connect(self.boxToggled)
                self.pointsLayout.addWidget(self.check_boxes[-1], cur_row, 0)

            self.points.append(QDoubleSpinBox())
            self.points[i].setMinimum(-1.79e38)
            self.points[i].setSingleStep(SPINBOX_STEP)
            self.points[i].valueChanged.connect(self.anyPointChanged)
            self.points[i].setStyleSheet(
                f"background-color: rgb({WIDGET_BG_COLOR[0]},{WIDGET_BG_COLOR[1]},{WIDGET_BG_COLOR[2]});"
            )
            if i // 2 < len(self.coords):
                self.points[i].setValue(self.coords[i // 2][i % 2])

            self.pointsLayout.addWidget(self.points[i], cur_row, i % 2 + 1)

    def boxToggled(self):
        """Called when any point has been disabled by clicking on check box"""

        for i in range(len(self.check_boxes)):
            if self.check_boxes[i].isChecked():
                self.points[i * 2].setEnabled(True)
                self.points[i * 2 + 1].setEnabled(True)
                self.toggled[i] = True
            else:
                self.points[i * 2].setEnabled(False)
                self.points[i * 2 + 1].setEnabled(False)
                self.toggled[i] = False

        self.enableUnvisibleCheckBoxes()
        self.anyPointChanged()

    def enableUnvisibleCheckBoxes(self):
        """Enable unvisible check boxes so when the user adds new points, they are enabled by default"""

        for i in range(self.num_of_points.value(), MAXIMUM_POINTS):
            self.toggled[i] = True

    def updateCoordinates(self):
        """Update 'coords' list when any point has been changed"""

        if (
            len(self.points) % 2 != 0
            or len(self.points) != self.num_of_points.value() * 2
        ):
            return

        self.coords.clear()
        for i in range(self.num_of_points.value()):
            if self.toggled[i]:
                self.coords.append(
                    [self.points[i * 2].value(), self.points[i * 2 + 1].value()]
                )

    def anyPointChanged(self):
        """Called when any point has been changed"""

        self.updateCoordinates()
        self._sibling.setCoords(self.coords)


class BezierVisualizationWidget(QWidget):
    def __init__(self, parent: QWidget, geometry: QRect = None) -> None:
        super().__init__(parent)

        if geometry:
            self.setGeometry(geometry)

        self.initUI()

    def initUI(self):
        self.setAutoFillBackground(True)

        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(qRgb(*VISUALIZATION_BG_COLOR)))
        self.setPalette(p)

        self.coords = [[0, 0], [0, 0], [0, 0]]
        self.bezier = []

        self.scale = 25
        self._sibling = None

    def setSibling(self, s):
        self._sibling = s

    def mousePressEvent(self, event):
        """Add point to bezier spline if there is less than MAXIMUM_POINTS constant"""

        if self._sibling.num_of_points.value() == MAXIMUM_POINTS:
            return

        self._sibling.coords.append(
            [
                (event.pos().x() - self.ORIGIN[0]) / self.scale,
                (self.ORIGIN[1] - event.pos().y()) / self.scale,
            ]
        )

        self._sibling.num_of_points.setValue(self._sibling.num_of_points.value() + 1)
        self._sibling.anyPointChanged()

    def wheelEvent(self, event):
        """Change scale of drawings on mouse wheel scroll"""

        delta = event.angleDelta().y()
        self.scale += (delta and delta // abs(delta)) * SCALE_VELOCITY

        if self.scale < 1:
            self.scale = 1

        self.update()

    def setCoords(self, coords):
        """Set new coordinates for bezier spline calculation and calculate new bezier spline"""

        self.coords = coords
        self.calculate_bezier()
        self.update()

    def paintEvent(self, event):
        """Default paint event that draws coordinate system and caclulated figures"""

        self.ORIGIN = (
            self.width() // 2,
            self.height() // 2,
        )
        painter = QPainter(self)

        self.draw_coordinate_system(painter)
        if len(self.coords) > 0:
            self.draw_points(painter)

        painter.end()

    def draw_points(self, painter):
        """Draw points of bezier spline that stored in 'bezier' list"""

        pen = QPen()
        pen.setColor(QColor(qRgb(*SPLINE_COLOR)))
        pen.setWidth(PEN_WIDTH)
        painter.setPen(pen)

        for i in range(1, len(self.bezier) - 1):
            painter.drawLine(
                self.ORIGIN[0] + self.bezier[i][0] * self.scale,
                self.ORIGIN[1] - self.bezier[i][1] * self.scale,
                self.ORIGIN[0] + self.bezier[i + 1][0] * self.scale,
                self.ORIGIN[1] - self.bezier[i + 1][1] * self.scale,
            )

        pen.setColor(QColor(qRgb(*POINT_COLOR)))
        pen.setWidth(PEN_WIDTH + 4)
        painter.setPen(pen)

        for coord in self.coords:
            painter.drawPoint(
                self.ORIGIN[0] + coord[0] * self.scale,
                self.ORIGIN[1] - coord[1] * self.scale,
            )

        pen.setWidth(PEN_WIDTH)
        painter.setPen(pen)
        for i in range(len(self.coords) - 1):
            painter.drawLine(
                self.ORIGIN[0] + self.coords[i][0] * self.scale,
                self.ORIGIN[1] - self.coords[i][1] * self.scale,
                self.ORIGIN[0] + self.coords[i + 1][0] * self.scale,
                self.ORIGIN[1] - self.coords[i + 1][1] * self.scale,
            )

    def calculate_bezier(self):
        """Calculate bezier spline points using algorithm from utils.py"""

        self.bezier = spl.bezier(self.coords)

    def draw_coordinate_system(self, painter):
        """Method that draws coordinate system"""

        painter.drawLine(
            PADDING, self.height() // 2, self.width() - PADDING, self.height() // 2
        )
        painter.drawLine(
            self.width() // 2, PADDING, self.width() // 2, self.height() - PADDING
        )

        # Arrows
        arrow_length = 7
        painter.drawLine(
            self.width() - PADDING,
            self.height() // 2,
            self.width() - PADDING - arrow_length,
            self.height() // 2 + arrow_length,
        )
        painter.drawLine(
            self.width() - PADDING,
            self.height() // 2,
            self.width() - PADDING - arrow_length,
            self.height() // 2 - arrow_length,
        )
        painter.drawLine(
            self.width() // 2,
            PADDING,
            self.width() // 2 + arrow_length,
            PADDING + arrow_length,
        )
        painter.drawLine(
            self.width() // 2,
            PADDING,
            self.width() // 2 - arrow_length,
            PADDING + arrow_length,
        )
