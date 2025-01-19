import sys
import time

import relay_boards
import relay_modbus

from PyQt6.QtGui import QAction, QPainter, QBrush, QColor
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QComboBox,
    QWidget,
    QTabWidget,
    QLabel,
    QSpinBox,
    QLineEdit,
    QDoubleSpinBox,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.relaisPanels = []

        self.setWindowTitle("Relais Steuerung")
        self.mainLayout = QVBoxLayout()

        # menubar file menu
        buttonFileLoad = QAction("&Konfiguration Laden", self)
        buttonFileLoad.triggered.connect(self.onMenubarFileLoadClick)

        buttonFileStore = QAction("&Konfiguration Speichern", self)
        buttonFileStore.triggered.connect(self.onMenubarFileStoreClick)

        # menubar board menu
        buttonBoardAdd = QAction("&Board hinzufügen", self)
        buttonBoardAdd.triggered.connect(self.onMenubarBoardAddClick)

        buttonBoardRemove = QAction("&Borad entfernen", self)
        buttonBoardRemove.triggered.connect(self.onMenubarBoardRemoveClick)

        buttonBoardRename = QAction("&Board Umbenennen", self)
        buttonBoardRename.triggered.connect(self.onMenubarBoardRenameClick)

        # menubar
        menu = self.menuBar()
        fileMenu = menu.addMenu("&Datei")
        fileMenu.addAction(buttonFileLoad)
        fileMenu.addAction(buttonFileStore)
        fileMenu.addSeparator()

        connectionMenu = menu.addMenu("&Verbindung")
        connectionMenu.addSeparator()

        boardMenu = menu.addMenu("&Board")
        boardMenu.addAction(buttonBoardAdd)
        boardMenu.addAction(buttonBoardRemove)
        boardMenu.addAction(buttonBoardRename)
        boardMenu.addSeparator()

        relaisMenu = menu.addMenu("&Relais")
        relaisMenu.addSeparator()

        # modbus object
        self.relay_modbus = relay_modbus.Modbus()

        # connection frame
        self.connectionFrame = QGroupBox(self)
        self.connectionFrame.setTitle("Verbindung")

        connectionFrameLayout = QHBoxLayout()
        connectionFrameDropdown = QComboBox()
        connectionConnectButton = QPushButton("Verbinden")
        connectionDisconnectButton = QPushButton("Trennen")
        connectionRefreshButton = QPushButton("Refresh")
        connectionFrameLayout.addWidget(connectionFrameDropdown)
        connectionFrameLayout.addWidget(connectionConnectButton)
        connectionFrameLayout.addWidget(connectionDisconnectButton)
        connectionFrameLayout.addWidget(connectionRefreshButton)
        self.connectionFrame.setLayout(connectionFrameLayout)
        self.mainLayout.addWidget(self.connectionFrame)

        # board tabs
        self.boardTabs = QTabWidget()

        panel1 = RelayPanel(name="Panel 1")
        self.relaisPanels.append(panel1)

        self.boardTabs.addTab(panel1, panel1.name)
        self.mainLayout.addWidget(self.boardTabs)

        mainWidget = QWidget()
        mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(mainWidget)

    def onMenubarFileLoadClick(self, s):
        print("Click Load", s)

    def onMenubarFileStoreClick(self, s):
        print("Click Store", s)

    def onMenubarBoardAddClick(self, s):
        print("Click Board Add", s)

    def onMenubarBoardRemoveClick(self, s):
        print("Click Board remove", s)

    def onMenubarBoardRenameClick(self, s):
        currentIndex = self.boardTabs.currentIndex()
        addressValue = self.relaisPanels[currentIndex].addressValue
        print(f"Current Tab index: {currentIndex}")
        print(f"Relais address: {addressValue}")


class RelayPanel(QWidget):

    def __init__(self, name: str):
        super().__init__()

        self.name = name
        mainLayout = QVBoxLayout()

        # board info layout
        boardInfo = QGroupBox("Board")
        boardInfoLayout = QGridLayout()
        addressLabel = QLabel("Adresse")
        self.addressBox = QSpinBox(minimum=0, maximum=64, singleStep=1)

        boardInfoLayout.addWidget(addressLabel, 0, 0)
        boardInfoLayout.addWidget(self.addressBox, 0, 1)

        boardTypeLabel = QLabel("Board Type")
        boardTypeDropDown = QComboBox()
        boardTypeDropDown.addItems(relay_boards.availableBoards)

        boardInfoLayout.addWidget(boardTypeLabel, 1, 0)
        boardInfoLayout.addWidget(boardTypeDropDown)

        boardInfo.setLayout(boardInfoLayout)

        self.relayStatus = []
        self.relayTextEdit = []
        self.relayDelay = []

        # relay control box

        relayControlPanel = QGroupBox("Relais Kontrolle")
        relayControlPanelLayout = QVBoxLayout()

        for idx in range(8):
            row = RelayRow(index=idx)
            relayControlPanelLayout.addWidget(row)

        relayControlPanel.setLayout(relayControlPanelLayout)

        mainLayout.addWidget(boardInfo)
        mainLayout.addWidget(relayControlPanel)
        self.setLayout(mainLayout)

    @property
    def addressValue(self):
        return self.addressBox.value()


class RelayRow(QWidget):
    def __init__(self, index: int, parent=None):
        super().__init__(parent)

        self.index = index
        self.relayStatus = False

        layout = QHBoxLayout()

        # status label
        self.relayIndicator = StatusIndicator("red")

        self.relayRowName = QLineEdit()
        self.relayRowOnButton = QPushButton("On")
        self.relayRowOffButton = QPushButton("Off")
        self.relayDelayLabel = QLabel("Delay:")
        self.relayDelaySpinBox = QDoubleSpinBox(minimum=0.1, maximum=10, singleStep=0.1)
        self.relayDelayPulseButton = QPushButton("Pulse")

        self.relayRowOnButton.setEnabled(True)
        self.relayRowOffButton.setEnabled(False)
        self.relayDelayPulseButton.setEnabled(False)

        self.relayRowOnButton.clicked.connect(self.onRelayOnButtonClicked)
        self.relayRowOffButton.clicked.connect(self.onRelayOffButtonClicked)
        self.relayDelayPulseButton.clicked.connect(self.onRelayDelayPulseButtonClicked)

        layout.addWidget(self.relayIndicator)
        layout.addWidget(self.relayRowName)
        layout.addWidget(self.relayRowOnButton)
        layout.addWidget(self.relayRowOffButton)
        layout.addWidget(self.relayDelayLabel)
        layout.addWidget(self.relayDelaySpinBox)
        layout.addWidget(self.relayDelayPulseButton)

        self.setLayout(layout)

    @property
    def relayName(self):
        return self.relayRowName.text()

    @property
    def relayDelayValue(self):
        return self.relayDelaySpinBox.value()

    def onRelayOnButtonClicked(self, s):
        self.triggerRelay()
        print(f"On Triggered from Row: {self.index}")

    def onRelayOffButtonClicked(self, s):
        self.triggerRelay()
        print(f"Off button triggered from Row: {self.index}")

    def onRelayDelayPulseButtonClicked(self, s):

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.triggerOn)

        duration = int(self.relayDelayValue * 1000)

        # turn relay off
        self.triggerOff()
        print(f"Delay value: {self.relayDelayValue} s")

        timer.start(duration)
        print(f"Pulse button triggered from Row: {self.index}")

    def triggerRelay(self):
        if self.relayStatus:
            self.triggerOff()
        else:
            self.triggerOn()

    def triggerOff(self):
        self.relayIndicator.setColor("red")
        self.relayRowOffButton.setEnabled(False)
        self.relayDelayPulseButton.setEnabled(False)
        self.relayRowOnButton.setEnabled(True)
        self.relayStatus = False

    def triggerOn(self):
        self.relayIndicator.setColor("green")
        self.relayRowOffButton.setEnabled(True)
        self.relayDelayPulseButton.setEnabled(True)
        self.relayRowOnButton.setEnabled(False)
        self.relayStatus = True


class StatusIndicator(QWidget):
    def __init__(self, color="green", parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(20, 20)

    def setColor(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        brush = QBrush(QColor(self.color))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.exec()
