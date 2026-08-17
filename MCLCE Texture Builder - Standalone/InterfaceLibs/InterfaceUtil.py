from typing import Self
from functools import partial
from types import SimpleNamespace as Object
import os

from PySide6.QtCore import (
    Qt,
    QTimer,
    QUrl
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QMessageBox
)
from PySide6.QtGui import (
    QCursor,
    QDesktopServices
)

from CodeLibs.Path import Path

# ———STYLE SETTER———

def set_style_of(widget: QWidget, state_name: str, state_value: str) -> None:
    widget.setProperty(state_name, state_value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

# ———FONT———

def set_font_size(widget: QWidget, size: int) -> None:
    """sets the font size of the widget

    Args:
        widget (QWidget): the widget to set font size on
        size (int): the size of the font
    """

    font = widget.font()
    font.setPointSize(size)
    widget.setFont(font)

# ———MARGINS———

def change_margins(
    widget: QWidget, 
    left: int|None = None, 
    top: int|None = None, 
    right: int|None = None, 
    bottom: int|None = None,
    *,
    all: int|None = None
) -> None:
    """change some or all margins of the provided widget

    Args:
        widget (QWidget): the widget to adjust margins
        left (int | None): left margin
        top (int | None): top margin
        right (int | None): right margin
        bottom (int | None): bottom margin
        all (int | None, optional): change all margins at once. Defaults to None.
    """

    # select margins
    new_margins = Object(
        left = None,
        top = None,
        right = None,
        bottom = None
    )
    if all is not None:
        new_margins.left, new_margins.top, new_margins.right, new_margins.bottom = all, all, all, all
    else:
        existing_margins = widget.contentsMargins()
        new_margins.left = left if left is not None else existing_margins.left()
        new_margins.top = top if top is not None else existing_margins.top()
        new_margins.right = right if right is not None else existing_margins.right()
        new_margins.bottom = bottom if bottom is not None else existing_margins.bottom()

    # change margins
    widget.setContentsMargins(
        new_margins.left,
        new_margins.top,
        new_margins.right,
        new_margins.bottom
    )

# ———TOOLTIP———

__TOOLTIP_MARGIN: int = 6

# tooltip (label) + timer holder dict by owner (widget)
class __TimedToolTipHolder:
    def __init__(self: Self, timer: QTimer, tooltip: QLabel) -> Self:
        self.timer = timer
        self.tooltip = tooltip
__active_tooltip_timers: dict[QWidget, __TimedToolTipHolder] = {}

# check if tooltip of owner is active
def __check_tooltip_timer(owner: QWidget) -> bool: 
    global __active_tooltip_timers

    return owner in __active_tooltip_timers.keys()

# create a new tooltip and timer
# • under the owner
# • with the given text
# • which lasts for ms time if not intercepted
def __new_tooltip(owner: QWidget, text: str, ms: int) -> None:
    global __active_tooltip_timers

    # create label and show it
    tooltip = QLabel(text, owner)
    tooltip.setWindowFlags(Qt.WindowType.ToolTip)
    change_margins(tooltip, all=__TOOLTIP_MARGIN)
    tooltip.adjustSize()
    tooltip.move(QCursor.pos())
    tooltip.show()

    # create timer and start it
    timer = QTimer(owner)
    timer.setSingleShot(True)
    timer.timeout.connect(partial(__del_tooltip, owner))
    timer.start(ms)

    # add both to active dict
    __active_tooltip_timers[owner] = __TimedToolTipHolder(timer, tooltip)

# try to delete the tooltip regardless of if it is still showing or not
def __del_tooltip(owner: QWidget) -> None:
    global __active_tooltip_timers
    
    if owner in __active_tooltip_timers: 
        # delete timer, tooltip and dict entry
        curr_entry: __TimedToolTipHolder = __active_tooltip_timers[owner]
        del __active_tooltip_timers[owner] # delete if exists
        curr_entry.timer.stop()
        curr_entry.timer.deleteLater()
        curr_entry.tooltip.deleteLater() 

# show a tooltip with the given text and time
# • categorized by owner (more than one tooltip of the same owner will not be permitted to exist)
def show_tooltip(owner: QWidget, text: str, ms: int) -> None:
    # check if timer already running
    if __check_tooltip_timer(owner):
        __del_tooltip(owner) # delete existing

    # create new with new timer
    __new_tooltip(owner, text, ms) 

# ———OPEN TO———

def open_in_explorer(path_or_str: str|Path):
    # convert to path if str
    path = path_or_str
    if isinstance(path_or_str, str): path = Path(path_or_str, isRootDirectory=True)
    path.formalize()

    # remove last (| file_name) if it's a file
    if (os.path.isfile(path.getPath())): path.removeAt(len(path) - 1)

    # open to path 
    QDesktopServices.openUrl(QUrl.fromLocalFile(path.getPath()))

# ———INFORMATION BOX———

# shows a popup window
# acts like a question if more than one button is given
def show_popup(
    parent: QWidget,
    title: str,
    desc: str,
    std_buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok
) -> None:
    window = QMessageBox(parent)
    window.setProperty("role", "window")
    window.setIcon(
        QMessageBox.Icon.Information
        if std_buttons.bit_count() <= 1
        else QMessageBox.Icon.Question
    )
    window.setWindowTitle(title)
    window.setText(desc)
    window.setStandardButtons(std_buttons)
    for button in window.buttons():
        button.setProperty("role", "button")
    return window.exec()
    