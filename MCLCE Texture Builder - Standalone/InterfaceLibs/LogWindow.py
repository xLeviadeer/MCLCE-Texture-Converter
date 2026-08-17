from typing import Self, Protocol, runtime_checkable

from PySide6.QtCore import (
    Qt,
    Signal
)
from PySide6.QtWidgets import (
    QWidget,
    QBoxLayout,
    QTextEdit
)

@runtime_checkable
class LogWindowProto(Protocol):
    def __init__(self: Self, parent: QWidget) -> Self: ...

    def push_text(self: Self, text: str) -> None: ...
    def clear_text(self: Self) -> None: ...

class LogWindow(QWidget):
    text_recieved = Signal(str)

    def __init__(self: Self, parent: QWidget) -> Self:
        super().__init__(parent)
        self.setProperty("role", "window")
        self.setWindowTitle("Log-book")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setMinimumSize(200, 400)
        self.__layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.setLayout(self.__layout)

        # log paper
        self.__log_paper = QTextEdit()
        self.__log_paper.setProperty("role", "text_display")
        self.__log_paper.setReadOnly(True)
        self.__log_paper.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.__layout.addWidget(self.__log_paper)

        # text handling
        self.text_recieved.connect(self.__push_text)

    def push_text(self: Self, text: str) -> None:
        self.text_recieved.emit(f"{text}\n") # sends to main thread

    def __push_text(self: Self, text: str) -> None:
        if not self.isVisible(): return
        self.__log_paper.setText(self.__log_paper.toPlainText() + text)

    def clear_text(self: Self) -> None:
        if not self.isVisible(): return
        self.__log_paper.setText("")

    def hide(self):
        self.clear_text()
        super().hide()
