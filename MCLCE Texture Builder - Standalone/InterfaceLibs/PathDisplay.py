from typing import Self

from PySide6.QtCore import (
    Qt
)
from PySide6.QtWidgets import (
    QApplication,
    QTextEdit
)
from PySide6.QtGui import (
    QMouseEvent
)

from . import InterfaceUtil as iUt

class PathDisplay(QTextEdit):

    # ———VARIABLES———

    def __init__(self: Self) -> Self:
        super().__init__()

        # create text edit ⧼box⧽
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # set events
        self.mousePressEvent = self.__handle_click
        self.mouseDoubleClickEvent = self.__handle_double_click

    def __handle_click(self: Self, event: QMouseEvent) -> None:
        QApplication.clipboard().setText(self.toPlainText())
        iUt.show_tooltip(self, "Copied!", 1000)

    def __handle_double_click(self: Self, event: QMouseEvent) -> None:
        text: str = self.toPlainText()
        if text: iUt.open_in_explorer(text) # open path if not nothing