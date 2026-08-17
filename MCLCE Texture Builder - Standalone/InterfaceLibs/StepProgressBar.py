from typing import Self, Protocol, runtime_checkable

from PySide6.QtCore import (
    Qt,
    Signal
)
from PySide6.QtWidgets import (
    QProgressBar
)

@runtime_checkable
class StepProgressBarProto(Protocol):
    @property
    def range(self: Self) -> int: ...

    def __init__(self: Self) -> Self: ...

    def set_scale(self: Self, scale: float) -> None: ...
    def set_scale_for_range(self: Self, range: int) -> None: ...
    def step_reset(self: Self) -> None: ...
    def step(self: Self, amount: int = 1) -> None: ...
    def setValue(self: Self, value: int) -> None: ...
    def setRange(self: Self, minimum: int, maximum: int) -> None: ...

class StepProgressBar(QProgressBar):
    """allows for updating the value of QProgressBar using a scaled point value"""

    # ———VARIABLES———

    on_set_value = Signal(int)

    # self.__range
    # self.range
    @property
    def range(self: Self) -> int: return self.__range

    # self.scale

    # ———CONSTRUCTOR———

    def __init__(self: Self) -> Self:
        """allows for updating the value of QProgressBar using a scaled point value"""
        super().__init__()
        self.__range: int = self.maximum() - self.minimum()
        self.on_set_value.connect(
            self.__setValue,
            Qt.ConnectionType.QueuedConnection
        )

    # ———METHODS———

    # system sends value based changes to the main thread for repainting
    def setValue(self: Self, value: int) -> None:
        self.on_set_value.emit(value)
    def __setValue(self: Self, value: int) -> None:
        super().setValue(value)

    def stepReset(self: Self) -> None:
        """resets the step of the progress bar to 0"""
        super().setValue(0)

    def step(self: Self, amount: int = 1) -> None:
        """steps the progress bar by the amount given

        Args:
            amount (int, optional): the amount of (scaled) steps to move the progress bar. Defaults to 1.
        """
        super().setValue(self.value() + amount)

    def stepBack(self: Self, amount: int = 1) -> None:
        """steps the progress bar back by the amount given
        
        Args:
            amount (int, optional): the amount of (scaled) steps to move the progress bar back. Defaults to 1.
        """
        super().setValue(self.value() - amount)

    # ———METHOD OVERRIDES———

    def setRange(self: Self, minimum: int, maximum: int) -> None:
        super().setRange(minimum, maximum)
        self.__range = maximum - minimum