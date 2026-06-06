from typing import Self

from PySide6.QtWidgets import (
    QProgressBar
)

class LoadingBar(QProgressBar):
    """allows for updating the value of QProgressBar using a scaled point value"""

    # ———VARIABLES———

    # self.__range
    # self.range
    @property
    def range(self: Self) -> int: return self.__range

    # self.scale

    # ———CONSTRUCTOR———

    def __init__(self: Self) -> Self:
        """allows for updating the value of QProgressBar using a scaled point value"""
        super().__init__()

        self.scale: float = 1
        self.__range: int = self.maximum() - self.minimum()

    # ———METHODS———

    def set_scale(self: Self, scale: float) -> None:
        """set the scale ratio of (base) progress points added for every (given) provided point added

        Args:
            scale (float): the scale ratio of (base) progress points added for every (given) provided point added
        """
        self.scale = scale

    def set_scale_ʃ_range(self: Self, range: int) -> None:
        """set the scale ratio of (base) progress points added for every (given) provided point added by providing the range|total of the (given) provided points

        Args:
            range (int): the range|total of the (given) provided points
        """
        self.scale = self.range / range

    def step_reset(self: Self) -> None:
        """resets the step of the progress bar to 0"""
        super().setValue(0)

    def step(self: Self, amount: int = 1) -> None:
        """steps the progress bar by the amount given

        Args:
            amount (int, optional): the amount of (scaled) steps to move the progress bar. Defaults to 1.
        """
        super().setValue(self.value() + (amount * self.scale))

    # ———METHOD OVERRIDES———

    def setValue(self: Self, value: int) -> None:
        super().setValue(value * self.scale)

    def setRange(self: Self, minimum: int, maximum: int) -> None:
        super().setRange(minimum, maximum)
        self.__range = maximum - minimum