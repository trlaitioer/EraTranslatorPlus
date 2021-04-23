from PySide2.QtWidgets import QTabWidget, QWidget
from Gui.Page import CSVPage, ERBPage, CharaPage
import typing


class TabWidget(QTabWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.buildUI()

    def buildUI(self) -> None:
        self.setTabPosition(QTabWidget.West)
        self.addTab(ERBPage(self, self.setTabToolTip), "ERB")
        self.addTab(CSVPage(self, self.setTabToolTip), "CSV")
        self.addTab(CharaPage(self, self.setTabToolTip), "Chara")
