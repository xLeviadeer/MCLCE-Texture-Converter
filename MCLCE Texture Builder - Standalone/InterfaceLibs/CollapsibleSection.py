from typing import Self
import sys

from PySide6.QtWidgets import (
    QWidget,
    QToolButton,
    QGridLayout,
    QBoxLayout,
    QSizePolicy
)
from PySide6.QtGui import (
    QMouseEvent
)

import InterfaceLibs.InterfaceUtil as iUt

class CollapsibleSection(QWidget):
    """collapsible section of UI

    Properties
        .content: this is what content is contained within the collapsible section
    """ 

    # ———VARIABLES———

    #self.__grid
    #self.__button

    #self.__button_text
    #self.button_text
    @property
    def button_text(self: Self) -> str: return self.__button_text
    @button_text.setter
    def button_text(self: Self, text: str) -> None: 
        self.__button_text = text
        self.__button.setText(f"{text} {self.__appropriate_arrow}")

    #self.button_height
    @property
    def button_height(self: Self) -> str: return self.__grid.rowMinimumHeight(0)
    @button_height.setter
    def button_height(self: Self, height: int) -> None: 
        if height is not None: 
            self.__grid.setRowMinimumHeight(0, height)
            self.__grid.setRowStretch(0, 0)
        else:
            self.__grid.setRowStretch(0, 1)

    # self.button_font_size
    @property
    def button_font_size(self: Self) -> int: return self.__button.font().pointSize()
    @button_font_size.setter
    def button_font_size(self: Self, size_in_points: int) -> None: iUt.set_font_size(self.__button, size_in_points)

    #self.__content
    
    #self.content
    @property
    def content(self: Self) -> QWidget|None: 
        if self.__content.count() == 0: return None
        return self.__content.itemAt(0).widget()
    @content.setter
    def content(self: Self, content_: QWidget) -> None: 
        if self.content:
            self.__content.removeWidget(self.content)
        self.__content.addWidget(content_)

    #self.content_is_visible
    @property
    def content_is_visible(self: Self) -> bool: return self.__button.isChecked()
    @content_is_visible.setter
    def content_is_visible(self: Self, visibility: bool) -> None: 
        if self.__button.isChecked() != visibility: self.__button.setChecked(visibility) # update ui to match
        self.__update_button_arrow()
        if visibility == True:
            self.__content_container.show()
        else: 
            self.__content_container.hide()

    #self.__appropriate_arrow
    @property
    def __appropriate_arrow(self: Self) -> str: 
        if self.content_is_visible: return "⌄"
        else: return "‹"

    # ———CONSTRUCTOR———

    def __init__(
        self: Self,
        button_text: str|None = None,
        *,
        content: QWidget|None = None,
        hidden: bool = True
    ) -> None:
        super().__init__()
        if content is None: content = QWidget()

        # main grid rows
        self.__grid = QGridLayout()
        self.__grid.setRowStretch(1, 0)
        self.__grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__grid)

        # collapsible button & button container
            # button is placed in a container so that click events can be observed for the whole cell instead of just the button
        self.__button = QToolButton()
        self.button_text = button_text
        self.__button.setCheckable(True)
        self.__button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.__button.clicked.connect(self.__handle_button_click)
        self.__button_container = QWidget()
        self.__button_container.mousePressEvent = self.__handle_button_container_click
        self.__button_container_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        iUt.change_margins(self.__button_container_layout, bottom=0)
        self.__button_container_layout.addWidget(self.__button)
        self.__button_container.setLayout(self.__button_container_layout)
        self.__grid.addWidget(self.__button_container, 0, 0, 1, 1)

        # content section & content container
            # real content is a container holding the content
            # changing public "content" changes what the real content container holds
        self.__content = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.__content.setContentsMargins(0, 0, 0, 0)
        self.__content.addWidget(content)
        self.__content_container = QWidget()
        self.__content_container.setLayout(self.__content)
        self.content_is_visible = not hidden
        self.__grid.addWidget(self.__content_container, 1, 0, 1, 1)

    # ———METHODS———

    def __update_button_arrow(self: Self) -> None:
        self.button_text = self.button_text # forces arrow update

    # ———EVENTS———

    def __handle_button_click(self: Self) -> None:
        self.content_is_visible = self.__button.isChecked()

    def __handle_button_container_click(self: Self, event: QMouseEvent) -> None:
        self.content_is_visible = not self.content_is_visible
    