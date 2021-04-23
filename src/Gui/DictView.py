from PySide2.QtCore import (QAbstractTableModel, QModelIndex, QObject, Qt, Signal)
from PySide2.QtGui import QMouseEvent
from PySide2.QtWidgets import QHeaderView, QTableView
from FileManager import ERBManager, CSVManager, CharaManager
import typing


class DictData(QAbstractTableModel):
    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.manager = {}

    def rowCount(self, parent: typing.Optional[QModelIndex] = None) -> int:
        return len(self.manager)

    def columnCount(self, parent: typing.Optional[QModelIndex] = None) -> int:
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> typing.Any:
        if not role == Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ["原文", "译文"][section]
        else:
            return None

    def data(self, index: QModelIndex, role: int) -> typing.Any:
        if not index.isValid() or self.manager is None:
            return None
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            if column == 0:
                return list(self.manager.keys())[row]
            elif column == 1:
                return list(self.manager.values())[row]
        return None

    def setManager(self, manager: typing.Union[ERBManager, CSVManager, CharaManager]) -> None:
        self.beginResetModel()
        self.manager = manager
        self.endResetModel()


class DictTable(QTableView):
    rowClicked = Signal(object)

    def __init__(self, parent: QObject, model: QAbstractTableModel) -> None:
        super().__init__(parent)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().hide()
        self.setSelectionMode(QTableView.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setModel(model)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            self.rowClicked.emit(self.currentIndex().row())
        super().mouseReleaseEvent(event)

    def silde(self, rowslide: int) -> None:
        current = self.currentIndex()
        current = current.siblingAtRow(current.row() + rowslide)
        if current.isValid():
            self.setCurrentIndex(current)
            self.rowClicked.emit(self.currentIndex().row())
