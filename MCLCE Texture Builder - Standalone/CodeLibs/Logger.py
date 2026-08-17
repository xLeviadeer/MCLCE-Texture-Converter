from typing import Self, Iterable
from enum import Enum
import sys
from builtins import print as pyPrint

from xLPyBasics import Sentinels as df
from xLPyBasics.JsonAPI import JsonHandler
from xLPyBasics.PathAPI import PathHandler, Path, Pathable

from bidict import bidict

from TextureLibs import Global

class _LoggerValue():
    """
    Description:
        Class to house logger status values
    ---
    Other:
        - Class is required so that Enum can have duplicate "values"
    """
    status = None
    syntax = None
    syntaxEnd = None
    isIndentable = None
    isCustom = None
    def __init__(self, status: bool, syntax: str, syntaxEnd: str="", *, isIndentable: bool=False, isCustom: bool=False):
        self.status = status
        self.syntax = syntax
        self.syntaxEnd = syntaxEnd
        self.isIndentable = isIndentable
        self.isCustom = isCustom

    def __str__(self) -> str:
        return f"{self.status}"
    
    def buildSyntax(self, message) -> str:
        return f"{self.syntax}{message}{self.syntaxEnd}"

# Logger Modes
class LoggerMode(Enum):
    """
    Description:
        List of logger type values
    """
    VERYIMPORTANT = _LoggerValue(True, "!! ") # non-exit cases, signifying importance
    IMPORTANT = _LoggerValue(True, "!  ") # non-exit cases, signifying importance
    EXIT = _LoggerValue(True, "EXITED: ") # exit cases
    ERROR = _LoggerValue(True, "---", isIndentable=True) # errors
    WARNING = _LoggerValue(True, " --", isIndentable=True) # warnings
    LOG = _LoggerValue(True, "  -", isIndentable=True) # routine logging
    DEBUG = _LoggerValue(False, "  *", isIndentable=True) # same as log but defaults as off
    NOTE = _LoggerValue(True, "   ", isIndentable=True) # used for prints like doPrint
    PLAIN = _LoggerValue(True, "") # AVOID using
    SECTION = _LoggerValue(True, "\n-----", "-----") # splits prints
    CHANNELONE = _LoggerValue(True, "    +")
    CHANNELTWO = _LoggerValue(True, "   ++")
    CHANNELTHREE = _LoggerValue(True, "  +++")
    # specials
    CUSTOMFUNCTION = _LoggerValue(False, "  *", isIndentable=True, isCustom=True)
    CUSTOMFUNCTIONRECURSION = _LoggerValue(False, "  * (", ")", isIndentable=True, isCustom=True)
    CUSTOMFUNCTIONTIMING = _LoggerValue(False, "  _*", isIndentable=True, isCustom=True)
    PATCHFUNCTION = _LoggerValue(False, "  *", isIndentable=True, isCustom=True)
    CUSTOMWEATHER = _LoggerValue(False, "  '", isIndentable=True)
    DEBUGTWO = _LoggerValue(False, "   *", isIndentable=True)
    DEBUGBRACKETRANDOM = _LoggerValue(False, "  '", isIndentable=True)

# sets mods to the module
module = sys.modules[__name__]
for item in LoggerMode:
    setattr(module, item.name, item.value)

def print(message: str="", mode: LoggerMode=LoggerMode.PLAIN, indent: int=0):
    """
    Description:
        Print to the terminal and use "logger" settings for better debugging
    ---
    Arguments:
        - mode : _LoggerMode <>
            - mode for this print to use
        - message : String <>
    ---
    Other:
        - Prints will not be made if doPrint is not set correctly in uiInput
    """
    # check if it's printable
    logMode = LoggerMode(mode)
    if logMode.value.status == True:
        message = logMode.value.buildSyntax(message)

        # check if mode is indentable
        if (LoggerMode(mode).value.isIndentable == True):
            while indent > 0:
                message = f" {message}"
                indent -= 1

        # print & log
        pyPrint(message)
        Global.log_win.push_text(message)

def isEnabled(mode: LoggerMode):
    logMode = LoggerMode(mode)
    return (logMode.value.status == True)

def setStatus(mode: LoggerMode, status: bool):
    """
    Description:
        Sets the status of a LoggerMode
    ---
    Arguments:
        - mode : LoggerMode <>
        - status : Boolean <>
    """
    logMode = LoggerMode(mode)
    logMode.value.status = status # changes the value
    setattr(module, logMode.name, logMode.value) # updates the module

    # if the mode is debug, change all custom modes too
    if (logMode == LoggerMode.DEBUG):
        for item in LoggerMode:
            if (item.value.isCustom == True):
                setStatus(item.value, status)

def enableAll():
    """
    Description:
        Enables all LoggerModes
    """
    for item in LoggerMode:
        LoggerMode(item).value.status = True 
        setattr(module, item.name, item.value)

def disableAll(exception: LoggerMode=None):
    """
    Description:
        Disables all LoggerModes
    """
    for item in LoggerMode:
        if (exception != None):
            if (item == LoggerMode(exception)): # will exclude the exception
                continue
        item.value.status = False 
        setattr(module, item.name, item.value)

def debugPrint():
    for item in LoggerMode:
        pyPrint(f"{item.__str__()}: {item.value}")

class LoggerHandler:
    DEFAULT_FLAGS: list[LoggerMode] = [
        LoggerMode.VERYIMPORTANT,
        LoggerMode.IMPORTANT,
        LoggerMode.EXIT,
        LoggerMode.ERROR,
        LoggerMode.WARNING,
        LoggerMode.LOG,
        # no debug
        LoggerMode.NOTE,
        LoggerMode.PLAIN,
        LoggerMode.SECTION,
        LoggerMode.CHANNELONE,
        LoggerMode.CHANNELTWO,
        LoggerMode.CHANNELTHREE
    ]

    FLAG_CONVERSIONS: bidict[str, LoggerMode] = bidict({
        "veryimportant": LoggerMode.VERYIMPORTANT,
        "important": LoggerMode.IMPORTANT,
        "exit": LoggerMode.EXIT,
        "error": LoggerMode.ERROR,
        "warning": LoggerMode.WARNING,
        "log": LoggerMode.LOG,
        "debug": LoggerMode.DEBUG,
        "note": LoggerMode.NOTE,
        "plain": LoggerMode.PLAIN,
        "section": LoggerMode.SECTION,
        "channelone": LoggerMode.CHANNELONE,
        "channeltwo": LoggerMode.CHANNELTWO,
        "channelthree": LoggerMode.CHANNELTHREE,
        "customfunction": LoggerMode.CUSTOMFUNCTION,
        "customfunctionrecursion": LoggerMode.CUSTOMFUNCTIONRECURSION,
        "customfunctiontiming": LoggerMode.CUSTOMFUNCTIONTIMING,
        "pathfunction": LoggerMode.PATCHFUNCTION,
        "customweather": LoggerMode.CUSTOMWEATHER,
        "debugtwo": LoggerMode.DEBUGTWO,
        "debugbracketrandom": LoggerMode.DEBUGBRACKETRANDOM
    })

    def __init__(
        self: Self,
        pathable: Pathable
    ) -> Self:
        path = Path.create(pathable)
        path.extension = "json"
        self.__handler = PathHandler(path)

    def __write_default_flags(self: Self) -> None:
        default_strs: list[str] = [self.FLAG_CONVERSIONS.inv[flag] for flag in self.DEFAULT_FLAGS]
        JsonHandler.write_all(self.__handler.path, default_strs)

    def __convert_str_to_flags(self: Self, flag_strs: Iterable[str]) -> list[LoggerMode]|df.Type.Invalid:
        flag_lst: list[LoggerMode] = []
        for flag_str in flag_strs:
            if flag_str in self.FLAG_CONVERSIONS:
                flag_lst.append(self.FLAG_CONVERSIONS[flag_str])
            else:
                return df.Value.Invalid
        return flag_lst

    def read_flags(self: Self) -> list[LoggerMode]|df.Type.Invalid:
        """reads the flags at this loggerhandler's path or returns invalid if the log flags are not valid 
        ╎ does not handle a non-existent log flags file"""
        flag_strs: list[str] = JsonHandler.read_all(self.__handler.path)
        flag_lst: list[LoggerMode]|df.Type.Invalid = self.__convert_str_to_flags(flag_strs)
        return flag_lst

    def get_flags(self: Self) -> tuple[list[LoggerMode], bool]:
        """reads the logger flags at the given path 
        ╎ if any logger flag is invalid → returns the default logging flags 
        ╎ if logger flags file doesn't exist writes it and returns defaults
        ╎ bool represents whether the flags were default because flags were invalid (True invalid)"""
        if not self.__handler.exists_file: 
            self.__write_default_flags()
            return self.DEFAULT_FLAGS, False
        flags: list[LoggerMode]|df.Type.Invalid = self.read_flags()
        if df.is_sentinel(flags, df.Type.Invalid): return self.DEFAULT_FLAGS, True
        return flags, False

