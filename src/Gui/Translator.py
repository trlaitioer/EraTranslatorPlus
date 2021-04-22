from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QPlainTextEdit, QPushButton, QWidget
from Api import translate
import typing


class Translator(QWidget):
    textSave = Signal(str, str)
    leftright = Signal(int)

    def __init__(self, parent=typing.Optional[QWidget]) -> None:
        super().__init__(parent)
        self.buildUI()
        self.connectSignal()

    def buildUI(self) -> None:
        self.original = QPlainTextEdit(self)
        self.original.setReadOnly(True)
        self.originalEdit = QPlainTextEdit(self)
        self.translation = QPlainTextEdit(self)
        self.copyButton = QPushButton("复制原文", self)
        self.translateButton = QPushButton("API翻译", self)
        self.preButton = QPushButton("<-", self)
        self.saveButton = QPushButton("保存", self)
        self.nexButton = QPushButton("->", self)

        self.Layout = QGridLayout(self)
        self.Layout.addWidget(self.original, 0, 0, 1, 3)
        self.Layout.addWidget(self.copyButton, 1, 0, 1, 3)
        self.Layout.addWidget(self.originalEdit, 2, 0, 1, 3)
        self.Layout.addWidget(self.translateButton, 3, 0, 1, 3)
        self.Layout.addWidget(self.translation, 4, 0, 1, 3)
        self.Layout.addWidget(self.preButton, 5, 0)
        self.Layout.addWidget(self.saveButton, 5, 1)
        self.Layout.addWidget(self.nexButton, 5, 2)

    def connectSignal(self) -> None:
        self.copyButton.clicked.connect(self.originalCopy)
        self.translateButton.clicked.connect(self.translate)
        self.saveButton.clicked.connect(
            lambda: self.textSave.emit(self.original.toPlainText(), self.translation.toPlainText()))
        self.preButton.clicked.connect(lambda: self.leftright.emit(-1))
        self.nexButton.clicked.connect(lambda: self.leftright.emit(1))

    def translate(self) -> None:
        result = translate(self.originalEdit.toPlainText())
        if result is not None:
            self.translation.setPlainText(result)

    def originalCopy(self) -> None:
        self.originalEdit.setPlainText(self.original.toPlainText())

    def setText(self, ori: str, tra: str) -> None:
        self.original.setPlainText(ori)
        self.originalEdit.setPlainText(ori)
        self.translation.setPlainText(tra)

    def clear(self) -> None:
        self.setText("", "")
