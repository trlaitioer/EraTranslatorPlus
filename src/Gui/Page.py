from pathlib import Path
from PySide6.QtWidgets import (QFrame, QGridLayout, QPushButton, QWidget, QFileDialog)
from Config import getConfig
from FileManager import ERBManager, CSVManager, CharaManager
from Gui.DictView import DictData, DictTable
from Gui.Translator import Translator
import typing

CSVFitler = f"CSV({';'.join(list(getConfig('SystemCSV').values()))})"


class Page(QWidget):
    def __init__(self, parent: QWidget, tooltip: typing.Callable[[int, str], None]) -> None:
        super().__init__(parent)
        self.manager = None
        self.buildUI()
        self.connectSignal()
        self.setToolTipTab = tooltip

    def buildUI(self) -> None:
        self.model = DictData(self)
        self.table = DictTable(self, self.model)

        self.buttons = QFrame(self)
        self.fileLoadButton = QPushButton("选择文件", self.buttons)
        self.fileSaveButton = QPushButton("保存文件", self.buttons)
        self.dictLoadButton = QPushButton("读取字典", self.buttons)
        self.dictSaveButton = QPushButton("保存字典", self.buttons)

        self.buttonsLayout = QGridLayout(self.buttons)
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout.addWidget(self.fileLoadButton)
        self.buttonsLayout.addWidget(self.fileSaveButton)
        self.buttonsLayout.addWidget(self.dictLoadButton)
        self.buttonsLayout.addWidget(self.dictSaveButton)

        self.translator = Translator(self)

        self.Layout = QGridLayout(self)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.addWidget(self.table, 0, 0)
        self.Layout.addWidget(self.buttons, 0, 1)
        self.Layout.addWidget(self.translator, 0, 2)

    def connectSignal(self) -> None:  #to do
        self.fileLoadButton.clicked.connect(self.loadFile)
        self.fileSaveButton.clicked.connect(self.saveFile)
        self.dictLoadButton.clicked.connect(lambda: print("LoadDict"))
        self.dictSaveButton.clicked.connect(lambda: print("SaveDict"))

        self.table.rowClicked.connect(self.loadText)
        self.translator.textSave.connect(self.translate)
        self.translator.leftright.connect(self.table.silde)

    def translate(self, original: str, translation: str) -> None:
        if self.manager:
            temp = self.table.currentIndex()
            self.model.beginResetModel()
            self.manager.translate(original, translation)
            self.model.endResetModel()
            self.table.setCurrentIndex(temp)

    def saveFile(self) -> None:
        if self.manager:
            temp = self.table.currentIndex()
            self.model.beginResetModel()
            self.manager.save()
            self.model.endResetModel()
            self.table.setCurrentIndex(temp)

    def loadText(self, row: int) -> None:
        if row < 0 or not self.manager:
            return
        self.translator.setText(*list(self.manager.items())[row])


class ERBPage(Page):
    def loadFile(self) -> None:
        tempPath = QFileDialog.getOpenFileName(caption="选择ERB文件",
                                               dir=str(self.manager.root.joinpath("erb")) if self.manager else "",
                                               filter="ERB(*.erb)")[0]
        if not tempPath:
            return
        self.manager = ERBManager(tempPath)
        self.model.setManager(self.manager)
        self.translator.clear()
        self.setToolTipTab(0, tempPath)


class CSVPage(Page):
    def loadFile(self) -> None:
        tempPath = QFileDialog.getOpenFileName(caption="选择CSV文件",
                                               dir=str(self.manager.root.joinpath("csv")) if self.manager else "",
                                               filter=CSVFitler)[0]
        if not tempPath:
            return
        self.manager = CSVManager(tempPath)
        self.model.setManager(self.manager)
        self.translator.clear()
        self.setToolTipTab(1, tempPath)


class CharaPage(Page):
    def buildUI(self) -> None:
        super().buildUI()
        self.fileLoadButton.setText("选择")
        self.fileSaveButton.setText("保存")

    def loadFile(self) -> None:
        tempPath = QFileDialog.getExistingDirectory(caption="选择CSV文件夹")
        if not tempPath:
            return
        if Path(tempPath).name.lower() != 'csv':
            print("请选择游戏目录下的CSV文件夹")
            return
        self.manager = CharaManager(tempPath)
        self.model.setManager(self.manager)
        self.translator.clear()
        self.setToolTipTab(2, tempPath)
