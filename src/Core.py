from pathlib import Path
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget
from Gui.Tabs import TabWidget
import sys
import typing


def getIconPath() -> str:
    return str(Path(__file__).parent.joinpath("Gui/ico.ico"))


def getStyle() -> str:
    if Path("style.css").exists():
        return Path("style.css").read_text()
    else:
        return Path(__file__).parent.joinpath("Gui/style.css").read_text()


class MainGui(QMainWindow):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.buildUI()

    def buildUI(self) -> None:
        self.setStyleSheet(getStyle())
        self.setWindowIcon(QIcon(getIconPath()))
        self.setWindowTitle("ERATranslator+")
        self.resize(800, 600)

        self.setCentralWidget(QWidget(self))

        self.tabs = TabWidget(self.centralWidget())

        self.gLayout = QGridLayout(self.centralWidget())
        self.gLayout.setContentsMargins(0, 0, 0, 0)
        self.gLayout.addWidget(self.tabs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainGui()
    win.show()
    sys.exit(app.exec_())
