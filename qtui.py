import sys

import relay_boards
import relay_modbus

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QWidget,
    QTabWidget,
    QLabel,
    QSpinBox,
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

        boardInfo = QGroupBox()
        boardInfoLayout = QHBoxLayout()
        addressLabel = QLabel("Adresse")
        self.addressBox = QSpinBox(minimum=0, maximum=8, singleStep=1)
        boardInfoLayout.addWidget(addressLabel)
        boardInfoLayout.addWidget(self.addressBox)
        boardInfo.setLayout(boardInfoLayout)

        mainLayout.addWidget(boardInfo)
        self.setLayout(mainLayout)

    @property
    def addressValue(self):
        return self.addressBox.value()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.exec()
