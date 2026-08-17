from typing import Self, Callable, TypeVar, Iterable
from builtins import type as typeof
from threading import Thread

from xLPyBasics.StructuresAPI import Event

from PySide6.QtCore import Signal, QThread, QCoreApplication

# this is needed so that the call site of either _Runner or _QRunner have the same method calls
EVENT_PARAM_TYPE = TypeVar("P")
class ConnectEvent[EVENT_PARAM_TYPE](Event[EVENT_PARAM_TYPE]):
    type Listener = Callable[[EVENT_PARAM_TYPE], None]

    def connect(self: Self, listener: Listener) -> None:
        self.subscribe(listener)

class Runner(Thread):
    def __init__(
        self: Self, 
        run_callback: Callable[[], None]|None = None
    ) -> Self:
        super().__init__()
        self._run_callback = run_callback
        self.on_exception = ConnectEvent[Exception]()
        self.on_complete = ConnectEvent()

    def run(self: Self) -> None:
        try:
            self._run_callback()
        except Exception as err:
            self.on_exception.emit(err)
            raise 
        finally:
            self.on_complete.emit()

class LoopRunner[T](Runner):
    def __init__(
        self: Self,
        iterable: Iterable[T],
        run_callback: Callable[[tuple[int, T]], None]|None = None
    ) -> Self:
        super().__init__(run_callback)
        self.__iterable = iterable
        self.on_progress = ConnectEvent[int]()

    def run(self: Self) -> None:
        try:
            for i, ele in enumerate(self.__iterable):
                self._run_callback((i, ele))
                self.on_progress.emit(i)
        except Exception as err:
            self.on_exception.emit(err)
            raise 
        finally:
            self.on_complete.emit()

class QRunner(QThread):
    # for some reason signals are actually per-instance despite needing to be defined at class level
    on_exception = Signal(Exception) 
    on_complete = Signal()

    def __init__(
        self: Self, 
        run_callback: Callable[[], None]|None = None
    ) -> Self:
        super().__init__()
        self._run_callback = run_callback

    def run(self: Self) -> None:
        try:
            self._run_callback()
        except Exception as err:
            self.on_exception.emit(err)
            raise 
        finally:
            self.on_complete.emit()

class QLoopRunner[T](QRunner):
    on_progress = Signal(int)

    def __init__(
        self: Self,
        iterable: Iterable[T],
        run_callback: Callable[[tuple[int, T]], None]|None = None
    ) -> Self:
        super().__init__(run_callback)
        self.__iterable = iterable
    
    def run(self: Self) -> None:
        try:
            for i, ele in enumerate(self.__iterable):
                self._run_callback((i, ele))
                self.on_progress.emit(i)
        except Exception as err:
            self.on_exception.emit(err)
            raise 
        finally:
            self.on_complete.emit()

def create_runner(run_callback: Callable[[], None]|None = None) -> Runner|QRunner:
    if QCoreApplication.instance() is None: return Runner(run_callback)
    else: return QRunner(run_callback)

def create_loop_runner[T](
    iterable: Iterable,
    run_callback: Callable[[tuple[int, T]], None]|None = None
) -> LoopRunner|QLoopRunner:
    if QCoreApplication.instance() is None: return LoopRunner[T](iterable, run_callback)
    else: return QLoopRunner[T](iterable, run_callback)
    