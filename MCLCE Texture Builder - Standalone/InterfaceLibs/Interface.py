import sys
import os
from typing import Self, Callable, Any

from xLPyBasics import Sentinels as df 
from xLPyBasics.JsonAPI import JsonHandler
from xLPyBasics.PathAPI import PathHandler, Search, Path as xLPyBasicsPath

from PySide6.QtCore import (
    Qt,
    QMimeData
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QSizePolicy,
    QFileDialog,
    QDialog,
    QStackedWidget,
    QListView,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QBoxLayout
)
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
    QMouseEvent,
    QIcon
)

from InterfaceLibs import ( 
    CollapsibleSection,
    PathDisplay,
    StepProgressBar,
    LogWindow,
    HelpWindow
)
import InterfaceLibs.InterfaceUtil as iUt
from CodeLibs.Path import Path
from CodeLibs.Threading import create_loop_runner
from TextureLibs.EntryPoint import EntryPoint
from CodeLibs import Logger as log
from TextureLibs import Global

AUTHOR: str = "xLevia"

# global libs holder
class GlobalLibs:
    program_version: str = JsonHandler.read_for(("global", "program_version"), 0)
    supported_versions: str = JsonHandler.read_for(("global", "supported_versions"), 0)
    
    input_games = JsonHandler.read_all(("global", "input_games"))

    input_versions_bedrock = JsonHandler.read_all(("global", "input_versions_bedrock"))
    input_versions_bedrock_plus = [f"{text}+" for text in input_versions_bedrock]
    input_versions_java = JsonHandler.read_all(("global", "input_versions_java"))
    input_versions_java_plus = [f"{text}+" for text in input_versions_java]

    output_structures_nintendo_switch = JsonHandler.read_all(("global", "output_structures_nintendo_switch"))
    output_structures_ps3 = JsonHandler.read_all(("global", "output_structures_ps3"))
    output_structures_ps4 = JsonHandler.read_all(("global", "output_structures_ps4"))
    output_structures_psV = JsonHandler.read_all(("global", "output_structures_psV"))
    output_structures_wiiu = JsonHandler.read_all(("global", "output_structures_wiiu"))
    output_structures_xbox_one = JsonHandler.read_all(("global", "output_structures_xbox_one"))
    output_structures_xbox360 = JsonHandler.read_all(("global", "output_structures_xbox360"))
    output_structures_all = [
        *output_structures_nintendo_switch,
        *output_structures_ps3,
        *output_structures_ps4,
        *output_structures_psV,
        *output_structures_wiiu,
        *output_structures_xbox_one,
        *output_structures_xbox360
    ]

    output_drives = JsonHandler.read_all(("global", "output_drives"))

    modes_size = JsonHandler.read_all(("global", "modes_size"))
    modes_build = JsonHandler.read_all(("global", "modes_build"))

# entry point data holder
class EntryPointData:
    def __init__(self: Self) -> Self:
        self.input_path = None
        self.input_path_type = None
        self.input_game = None
        self.input_version = None

        self.output_path = None
        self.output_structure = None
        self.output_drive = None
        
        self.build_mode = None # error mode
        self.size_mode = None
        self.complex_processing = None

    def __str__(self: Self) -> str:
        return (
            "{"
            f"input_path: {self.input_path}, "
            f"input_path_type: {self.input_path_type}, "
            f"input_game: {self.input_game}, "
            f"input_version: {self.input_version}, "
            f"output_path: {self.output_path}, "
            f"output_structure: {self.output_structure}, "
            f"output_drive: {self.output_drive}, "
            f"build_mode: {self.build_mode}, "
            f"size_mode: {self.size_mode}, "
            f"complex_processing: {self.complex_processing}"
            "}"
        )

# main window
class MainWindow(QWidget):

    ZIP: str = "zip"
    END_ZIP: str = f".{ZIP}"
    MCPACK: str = "mcpack"
    END_MCPACK: str = f".{MCPACK}"

    INPUT_DRAG_IDLE_STR: str = "Drag & Drop a texture pack here..."
    INPUT_DRAG_INVALID_HOVER: str = "Invalid pack! Check available input games."
    INPUT_DRAG_REJECTED_HOVER: str = "The selected input game does not accept file inputs."
    INPUT_DRAG_VALID_HOVER: str = "..."
    INPUT_DRAG_HOLDING_STR: str = "Got your pack!"

    BUILD_ENABLED_TOOLTIP: None = None
    BUILD_DISABLED_TOOLTIP: str = "Cannot build with the current configuration. Ensure all fields have been set."

    JAVA: str = "java"
    BEDROCK: str = "bedrock"
    NINTENDO_SWITCH: str = "nintendo_switch"
    PS3: str = "ps3"
    PS4: str = "ps4"
    PSV: str = "psV"
    WIIU: str = "wiiu"
    XBOX_ONE: str = "xbox_one"
    XBOX360: str = "xbox360"

    GAME_TO_OUTPUT_STRUCTURE_LIB: dict[str, list] = {
        JAVA: GlobalLibs.output_structures_all,
        BEDROCK: GlobalLibs.output_structures_all,
        NINTENDO_SWITCH: GlobalLibs.output_structures_nintendo_switch,
        PS3: GlobalLibs.output_structures_ps3,
        PS4: GlobalLibs.output_structures_ps4,
        PSV: GlobalLibs.output_structures_psV,
        WIIU: GlobalLibs.output_structures_wiiu,
        XBOX_ONE: GlobalLibs.output_structures_xbox_one,
        XBOX360: GlobalLibs.output_structures_xbox360
    }

    HUGE_LABEL_SIZE: int = 15
    LARGE_LABEL_SIZE: int = 11
    MEDIUM_LABEL_SIZE: int = 9
    SMALL_LABEL_SIZE: int = 7

    __singleton_exists: bool = False
    def __init__(self: Self, icon: QIcon) -> Self:
        super().__init__()
        self.setProperty("role", "window")

        # singleton
        if self.__singleton_exists: raise RuntimeError("MainWindow is a singleton and cannot be instantiated more than once")
        self.__singleton_exists = True
        
        # variables
        self.__reject_input: bool = False
        self.__curr_version_set: str|None = None
        self.__curr_structure_set: str|None = None
        self.__entry_data = EntryPointData()

        self.__log_window: LogWindow = LogWindow(self)
        self.__help_window: HelpWindow = HelpWindow(self)
        self.__logger_handler = log.LoggerHandler(xLPyBasicsPath("logger"))
        
        # set main window settings
        self.setWindowTitle(f"MC LCE Texture Converter {GlobalLibs.program_version}")
        self.setWindowIcon(icon)
        self.__grid = QGridLayout()
        iUt.change_margins(self.__grid, all=0)
        self.__grid.setRowStretch(0, 0) # title row
        self.__grid.setRowStretch(1, 1) # settings row
        self.__grid.setRowStretch(2, 0) # bar row
        self.setLayout(self.__grid)

        # title
        self.__title = QLabel()
        self.__title.setText(
            "<strong>"
            + "<span style=\"color: #373737;\">Minecraft </span>"
            + "<span style=\"color: #e70012;\">L</span>"
            + "<span style=\"color: #007c00;\">C</span>"
            + "<span style=\"color: #0071d1;\">E</span>"
            + "<span style=\"color: #373737;\"> Texture Converter</span>"
            + "</strong>"
        )
        iUt.set_font_size(self.__title, self.HUGE_LABEL_SIZE)
        self.__title.setContentsMargins(10, 10, 10, 0)
        self.__grid.addWidget(self.__title, 0, 0, 1, 1)

        # settings grid
        self.__settings_grid = QGridLayout()
        self.__settings_grid.setContentsMargins(10, 10, 10, 10)
        SET_R0HEIGHT = 20
        self.__settings_grid.setRowMinimumHeight(0, SET_R0HEIGHT) 
        self.__settings_grid.setRowStretch(0, 0) # input label
        self.__settings_grid.setRowStretch(1, 1) # input container
        SET_R2HEIGHT = 10
        self.__settings_grid.setRowMinimumHeight(2, SET_R2HEIGHT)
        self.__settings_grid.setRowStretch(2, 0) # spacer
        SET_R3HEIGHT = 20
        self.__settings_grid.setRowMinimumHeight(3, SET_R3HEIGHT) 
        self.__settings_grid.setRowStretch(3, 0) # output label
        self.__settings_grid.setRowStretch(4, 0) # output container
        SET_R5HEIGHT = 10
        self.__settings_grid.setRowMinimumHeight(5, SET_R5HEIGHT) 
        self.__settings_grid.setRowStretch(5, 1) # spacer
        self.__settings_grid.setRowStretch(6, 0) # advanced container
        self.__settings_container = QWidget()
        self.__settings_container.setLayout(self.__settings_grid)
        self.__grid.addWidget(self.__settings_container, 1, 0, 1, 1)

        # input label
        self.__input_label = QLabel("Input Settings")
        self.__input_label.setProperty("role", "label")
        iUt.set_font_size(self.__input_label, self.LARGE_LABEL_SIZE)
        self.__input_label.setFixedHeight(SET_R0HEIGHT)
        self.__settings_grid.addWidget(self.__input_label, 0, 0, 1, 1)

        # input grid rows
        self.__input_grid = QGridLayout()
        IN_R0HEIGHT = 100
        self.__input_grid.setRowMinimumHeight(0, IN_R0HEIGHT)
        self.__input_grid.setRowStretch(0, 1) # default 1
        IN_R1HEIGHT = 30
        self.__input_grid.setRowMinimumHeight(1, IN_R1HEIGHT)
        self.__input_grid.setRowStretch(1, 0)
        IN_R2HEIGHT = 30
        self.__input_grid.setRowMinimumHeight(2, IN_R2HEIGHT)
        self.__input_grid.setRowStretch(2, 0)

        # input grid columns
        IN_C0WIDTH = 50
        self.__input_grid.setColumnMinimumWidth(0, IN_C0WIDTH)
        self.__input_grid.setColumnStretch(0, 0)
        IN_C1WIDTH = 100
        self.__input_grid.setColumnMinimumWidth(1, IN_C1WIDTH)
        self.__input_grid.setColumnStretch(1, 1)
        IN_C2WIDTH = 150
        self.__input_grid.setColumnMinimumWidth(2, IN_C2WIDTH)
        self.__input_grid.setColumnStretch(2, 0)

        # input drag/drop space
        self.__input_drag = QWidget()
        self.__input_drag.setProperty("role", "drag_background")
        self.__input_drag.setProperty("state", "idle")
        self.__input_drag.setAcceptDrops(True) # must be the event holder because it's above the colored box
        self.__input_drag.dragEnterEvent = self.__handle_drag_enter
        self.__input_drag.dragLeaveEvent = self.__handle_drag_leave
        self.__input_drag.dropEvent = self.__handle_drop
        self.__input_drag.mousePressEvent = self.__handle_click
        self.__input_grid.addWidget(self.__input_drag, 0, 0, 1, 3)

        # input drag/drop space text
        self.__input_drag_text = QLabel()
        self.__input_drag_text.setProperty("role", "drag_text")
        self.__input_drag_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.__input_drag_text.setText(self.INPUT_DRAG_IDLE_STR) # default
        iUt.set_font_size(self.__input_drag_text, self.HUGE_LABEL_SIZE)
        self.__input_drag_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__input_grid.addWidget(self.__input_drag_text, 0, 0, 1, 3)

        # input path text
        self.__input_path_text = PathDisplay()
        self.__input_path_text.setProperty("role", "path")
        self.__input_path_text.textChanged.connect(self.__handle_input_path_text_changed)
        self.__input_path_text.setFixedHeight(IN_R1HEIGHT)
        self.__input_grid.addWidget(self.__input_path_text, 1, 0, 1, 2)

        # input path browse
        self.__input_path_button = QPushButton("Browse Input")
        self.__input_path_button.setProperty("role", "button")
        self.__input_path_button.clicked.connect(self.__handle_input_path_button_click)
        self.__input_path_button.setFixedHeight(IN_R1HEIGHT)
        self.__input_grid.addWidget(self.__input_path_button, 1, 2, 1, 1)

        # input type label
        self.__input_type_label = QLabel("Convert From")
        self.__input_type_label.setProperty("role", "label")
        iUt.set_font_size(self.__input_type_label, self.MEDIUM_LABEL_SIZE)
        self.__input_type_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.__input_type_label.setFixedHeight(IN_R2HEIGHT)
        self.__input_grid.addWidget(self.__input_type_label, 2, 0, 1, 1)

        # input type
        self.__input_type = QComboBox()
        self.__input_type.setProperty("role", "combo")
        self.__input_type.setToolTip("what edition of Minecraft is this texture pack from?")
        self.__input_type.addItems(GlobalLibs.input_games)
        self.__input_type.currentTextChanged.connect(self.__handle_input_type_changed)
        self.__input_type.setFixedHeight(IN_R2HEIGHT)
        self.__input_grid.addWidget(self.__input_type, 2, 1, 1, 1)

        # input version
        self.__input_version = QComboBox()
        self.__input_version.setProperty("role", "combo")
        self.__input_version.setToolTip("what version of Minecraft is this texure pack from?")
        self.__input_version.currentIndexChanged.connect(self.__handle_input_version_changed)
        self.__input_version.setFixedHeight(IN_R2HEIGHT)
        self.__input_grid.addWidget(self.__input_version, 2, 2, 1, 1)

        # input frame
        self.__input_frame = QFrame()
        self.__input_frame.setProperty("role", "frame")
        self.__input_frame.setLayout(self.__input_grid)
        self.__settings_grid.addWidget(self.__input_frame, 1, 0, 1, 1)

        # spacing row
        r2_spacer = QWidget()
        r2_spacer.setFixedHeight(SET_R2HEIGHT)
        self.__settings_grid.addWidget(r2_spacer, 2, 0, 1, 1) 

        # output label
        self.__output_label = QLabel("Output Settings")
        self.__output_label.setProperty("role", "label")
        iUt.set_font_size(self.__output_label, self.LARGE_LABEL_SIZE)
        self.__output_label.setFixedHeight(SET_R3HEIGHT)
        self.__settings_grid.addWidget(self.__output_label, 3, 0, 1, 1)

        # output grid rows
        self.__output_grid = QGridLayout()
        OUT_R0HEIGHT = 30
        self.__output_grid.setRowMinimumHeight(0, OUT_R0HEIGHT)
        self.__output_grid.setRowStretch(0, 0)
        OUT_R1HEIGHT = 30
        self.__output_grid.setRowMinimumHeight(1, OUT_R1HEIGHT)
        self.__output_grid.setRowStretch(1, 0)

        # output grid columns
        OUT_C0WIDTH = 50
        self.__output_grid.setColumnMinimumWidth(0, OUT_C0WIDTH)
        self.__output_grid.setColumnStretch(0, 0)
        OUT_C1WIDTH = 100
        self.__output_grid.setColumnMinimumWidth(1, OUT_C1WIDTH)
        self.__output_grid.setColumnStretch(1, 1)
        OUT_C2WIDTH = 150
        self.__output_grid.setColumnMinimumWidth(2, OUT_C2WIDTH)
        self.__output_grid.setColumnStretch(2, 0)

        # output path text
        self.__output_path_text = PathDisplay()
        self.__output_path_text.setProperty("role", "path")
        self.__output_path_text.textChanged.connect(self.__handle_output_path_text_changed)
        self.__output_path_text.setFixedHeight(OUT_R0HEIGHT)
        self.__output_grid.addWidget(self.__output_path_text, 0, 0, 1, 2)

        # output path browse
        self.__output_path_button = QPushButton("Browse Output")
        self.__output_path_button.setProperty("role", "button")
        self.__output_path_button.clicked.connect(self.__handle_output_path_button_click)
        self.__output_path_button.setFixedHeight(OUT_R0HEIGHT)
        self.__output_grid.addWidget(self.__output_path_button, 0, 2, 1, 1)

        # output structure label
        self.__output_structure_label = QLabel("Convert To")
        self.__output_structure_label.setProperty("role", "label")
        iUt.set_font_size(self.__output_structure_label, self.MEDIUM_LABEL_SIZE)
        self.__output_structure_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.__output_structure_label.setFixedHeight(OUT_R1HEIGHT)
        self.__output_grid.addWidget(self.__output_structure_label, 1, 0, 1, 1)

        # output structure
        self.__output_structure = QComboBox()
        self.__output_structure.setProperty("role", "combo")
        self.__output_structure.setToolTip("what version of Minecraft are you converting to?")
        self.__output_structure.currentIndexChanged.connect(self.__handle_output_structure_changed)
        self.__output_structure.setFixedHeight(OUT_R1HEIGHT)
        self.__output_grid.addWidget(self.__output_structure, 1, 1, 1, 1)

        # output open button
        self.__output_open_button = QPushButton("Open Output")
        self.__output_open_button.setProperty("role", "button")
        self.__output_open_button.setToolTip("open the output folder that you have choosen")
        self.__output_open_button.clicked.connect(self.__handle_output_open_button_click)
        self.__output_open_button.setFixedHeight(OUT_R1HEIGHT)
        self.__output_grid.addWidget(self.__output_open_button, 1, 2, 1, 1)

        # output frame
        self.__output_frame = QFrame()
        self.__output_frame.setProperty("role", "frame")
        self.__output_frame.setLayout(self.__output_grid)
        self.__settings_grid.addWidget(self.__output_frame, 4, 0, 1, 1)

        # spacing row
        r5_spacer = QWidget()
        r5_spacer.setFixedHeight(SET_R5HEIGHT)
        self.__settings_grid.addWidget(r5_spacer, 5, 0, 1, 1) 

        # advanced grid rows
        self.__advanced_grid = QGridLayout()
        FIN_LABEL_SPACING = 5
        ADV_R0HEIGHT_LABEL = 15
        ADV_R0HEIGHT_ELEMENT = 30
        ADV_R0HEIGHT = ADV_R0HEIGHT_LABEL + ADV_R0HEIGHT_ELEMENT + FIN_LABEL_SPACING
        self.__advanced_grid.setRowMinimumHeight(0, ADV_R0HEIGHT)
        self.__advanced_grid.setRowStretch(0, 0)
        ADV_R1HEIGHT = 30
        self.__advanced_grid.setRowMinimumHeight(1, ADV_R1HEIGHT)
        self.__advanced_grid.setRowStretch(1, 0)

        # advanced grid columns
        ADV_C0WIDTH = 100
        self.__advanced_grid.setColumnMinimumWidth(0, ADV_C0WIDTH)
        self.__advanced_grid.setColumnStretch(0, 0)
        ADV_C1WIDTH = 100
        self.__advanced_grid.setColumnMinimumWidth(0, ADV_C1WIDTH)
        self.__advanced_grid.setColumnStretch(1, 0)
        ADV_C2WIDTH = 100
        self.__advanced_grid.setColumnMinimumWidth(0, ADV_C2WIDTH)
        self.__advanced_grid.setColumnStretch(2, 0)

        # advanced main
        self.__advanced_collapsible = CollapsibleSection("Advanced/More Settings")
        self.__advanced_collapsible.setProperty("role", "label_collapse")
        self.__advanced_collapsible.button_font_size = self.LARGE_LABEL_SIZE
        self.__advanced_collapsible.button_height = 30
            # content | frame
        advanced_collapsible_content = QFrame()
        advanced_collapsible_content.setProperty("role", "frame")
        advanced_collapsible_content.setLayout(self.__advanced_grid)
        self.__advanced_collapsible.content = advanced_collapsible_content
        self.__settings_grid.addWidget(self.__advanced_collapsible, 6, 0, 1, 1)

        # advanced ⧼output⧽ drive
        advanced_drive_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        iUt.change_margins(advanced_drive_layout, all=0)
        advanced_drive_layout.setSpacing(FIN_LABEL_SPACING)
            # label
        advanced_drive_label = QLabel("Output Drive")
        advanced_drive_label.setProperty("role", "label")
        iUt.set_font_size(advanced_drive_label, self.MEDIUM_LABEL_SIZE)
        advanced_drive_label.setFixedHeight(ADV_R0HEIGHT_LABEL)
        advanced_drive_layout.addWidget(advanced_drive_label)
            # element
        self.__advanced_drive = QComboBox()
        self.__advanced_drive.setProperty("role", "combo")
        self.__advanced_drive.setToolTip("what drive will this texture pack live on on your console?")
        self.__advanced_drive.currentIndexChanged.connect(self.__handle_advanced_drive_changed)
        self.__advanced_drive.setFixedHeight(ADV_R0HEIGHT_ELEMENT)
        advanced_drive_layout.addWidget(self.__advanced_drive)
            # container
        advanced_drive_container = QWidget()
        advanced_drive_container.setLayout(advanced_drive_layout)
        advanced_drive_container.setFixedHeight(ADV_R0HEIGHT)
        self.__advanced_grid.addWidget(advanced_drive_container, 0, 0, 1, 1)

        # advanced build ⧼mode⧽
        self.__entry_data.build_mode = GlobalLibs.modes_build[0] # default selection
        advanced_build_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        iUt.change_margins(advanced_build_layout, all=0)
        advanced_build_layout.setSpacing(FIN_LABEL_SPACING)
            # label
        advanced_build_label = QLabel("Build Mode")
        advanced_build_label.setProperty("role", "label")
        iUt.set_font_size(advanced_build_label, self.MEDIUM_LABEL_SIZE)
        advanced_build_label.setFixedHeight(ADV_R0HEIGHT_LABEL)
        advanced_build_layout.addWidget(advanced_build_label)
            # element
        self.__advanced_build = QComboBox()
        self.__advanced_build.setProperty("role", "combo")
        self.__advanced_build.setToolTip("what texture should be placed when a texture must be resized or cropped?")
        self.__advanced_build.addItems(GlobalLibs.modes_build)
        self.__advanced_build.currentIndexChanged.connect(self.__handle_advanced_error_changed)
        self.__advanced_build.setFixedHeight(ADV_R0HEIGHT_ELEMENT)
        advanced_build_layout.addWidget(self.__advanced_build)
            # container
        advanced_error_container = QWidget()
        advanced_error_container.setLayout(advanced_build_layout)
        advanced_error_container.setFixedHeight(ADV_R0HEIGHT)
        self.__advanced_grid.addWidget(advanced_error_container, 0, 1, 1, 1)

        # advanced size ⧼mode⧽
        self.__entry_data.size_mode = 16 # default selection
        self.__entry_data.complex_processing = True # default selection
        advanced_size_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        iUt.change_margins(advanced_size_layout, all=0)
        advanced_size_layout.setSpacing(FIN_LABEL_SPACING)
            # label
        advanced_size_label = QLabel("Size Mode ")
        advanced_size_label.setProperty("role", "label")
        iUt.set_font_size(advanced_size_label, self.MEDIUM_LABEL_SIZE)
        advanced_size_label.setFixedHeight(ADV_R0HEIGHT_LABEL)
        advanced_size_layout.addWidget(advanced_size_label)
            # element
        self.__advanced_size = QComboBox()
        self.__advanced_size.setProperty("role", "combo")
        self.__advanced_size.setToolTip("what size should the texture pack come out as?")
        self.__advanced_size.addItems(GlobalLibs.modes_size)
        self.__advanced_size.currentIndexChanged.connect(self.__handle_advanced_size_changed)
        self.__advanced_size.setFixedHeight(ADV_R0HEIGHT_ELEMENT)
        advanced_size_layout.addWidget(self.__advanced_size)
            # container
        advanced_size_container = QWidget()
        advanced_size_container.setLayout(advanced_size_layout)
        advanced_size_container.setFixedHeight(ADV_R0HEIGHT)
        self.__advanced_grid.addWidget(advanced_size_container, 0, 2, 1, 1)

        # advanced ⧼show⧽ log
        self.__advanced_log_button = QPushButton("Show Log")
        self.__advanced_log_button.setProperty("role", "button")
        self.__advanced_log_button.setToolTip("show the log details of the next/current active build")
        self.__advanced_log_button.clicked.connect(self.__handle_advanced_log_button_click)
        self.__advanced_log_button.setFixedHeight(ADV_R1HEIGHT)
        self.__advanced_grid.addWidget(self.__advanced_log_button, 1, 0, 1, 1)

        # advanced clear ⧼output⧽
        self.__advanced_clear_button = QPushButton("Clear Output Folder")
        self.__advanced_clear_button.setProperty("role", "button")
        self.__advanced_clear_button.setToolTip("clears the output folder of ¡all¡ files")
        self.__advanced_clear_button.clicked.connect(self.__handle_advanced_clear_button_click)
        self.__advanced_clear_button.setFixedHeight(ADV_R1HEIGHT)
        self.__advanced_grid.addWidget(self.__advanced_clear_button, 1, 1, 1, 1)

        self.__advanced_info_button = QPushButton("Help and Info")
        self.__advanced_info_button.setProperty("role", "button")
        self.__advanced_info_button.setToolTip("see help and information about using this program")
        self.__advanced_info_button.clicked.connect(self.__handle_advanced_info_button_click)
        self.__advanced_info_button.setFixedHeight(ADV_R1HEIGHT)
        self.__advanced_grid.addWidget(self.__advanced_info_button, 1, 2, 1, 1)

        # finalized bar
        self.__finalized = QFrame()
        self.__finalized.setProperty("role", "finalized_sect")
        self.__grid.addWidget(self.__finalized, 2, 0, 1, 1)

        # finalized grid rows
        self.__finalized_grid = QGridLayout()
        self.__finalized_grid.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__finalized.setLayout(self.__finalized_grid)
        FIN_R0HEIGHT = 30
        self.__finalized_grid.setRowMinimumHeight(0, FIN_R0HEIGHT)
        self.__finalized_grid.setRowStretch(0, 0)
        FIN_R1HEIGHT = 10
        self.__finalized_grid.setRowMinimumHeight(1, FIN_R1HEIGHT)
        self.__finalized_grid.setRowStretch(1, 0)
        
        # finalized grid columns
        self.__finalized_grid.setRowStretch(0, 1)
        self.__finalized_grid.setRowStretch(1, 1)
        FIN_C2WIDTH_MIN = 150
        FIN_C2WIDTH_MAX = 400
        self.__finalized_grid.setColumnMinimumWidth(2, FIN_C2WIDTH_MIN)
        self.__finalized_grid.setRowStretch(2, 1)
        FIN_C3WIDTH = 100
        self.__finalized_grid.setColumnMinimumWidth(3, FIN_C3WIDTH)
        self.__finalized_grid.setRowStretch(3, 0)

        # loading bar
        self.__finalized_bar = StepProgressBar()
        self.__finalized_bar.setProperty("role", "progress_bar")
        self.__finalized_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.__finalized_bar.setMinimumWidth(FIN_C2WIDTH_MIN)
        self.__finalized_bar.setMaximumWidth(FIN_C2WIDTH_MAX)
        self.__finalized_bar.setFixedHeight(FIN_R0HEIGHT)
        self.__finalized_grid.addWidget(self.__finalized_bar, 0, 2, 1, 1)

        # build button
        self.__finalized_build = QPushButton("Convert")
        self.__finalized_build.setProperty("role", "button")
        self.__set_finalized_build_state(False)
        self.__finalized_build.clicked.connect(self.__handle_finalized_build_click)
        self.__finalized_build.setFixedSize(FIN_C3WIDTH, FIN_R0HEIGHT)
        self.__finalized_grid.addWidget(self.__finalized_build, 0, 3, 1, 1)

        # supported versions
        self.__finalized_supported = QLabel(f"supports {GlobalLibs.supported_versions}   •   created by {AUTHOR}")
        self.__finalized_supported.setProperty("role", "label")
        iUt.set_font_size(self.__finalized_supported, self.SMALL_LABEL_SIZE)
        self.__finalized_supported.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.__finalized_supported.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__finalized_supported.setFixedHeight(FIN_R1HEIGHT)
        self.__finalized_grid.addWidget(self.__finalized_supported, 1, 0, 1, 4)

        # set main window size 
        self.setMaximumSize(1000, 1000)
        self.resize(200, 450)

    def __set_style_of(self: Self, widget: QWidget, state_name: str, state_value: str) -> None:
        widget.setProperty(state_name, state_value)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def __select_folder(self: Self, start_directory: str|None = None) -> str|None:
        # have user select folder with native
        file_path = QFileDialog.getExistingDirectory(
            self,
            "Select a Folder",
            (start_directory if start_directory else "")
        )
        return file_path

    def __select_file_or_folder(self: Self, filter: str|None = None, start_directory: str|None = None) -> str|None:
        # create dialog
        dialog = QFileDialog()
        dialog.setWindowTitle("Select a File or Folder")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        if start_directory: dialog.setDirectory(start_directory)
        if filter: dialog.setNameFilter(filter)

        # stop dialog from opening folder when selecting and instead accept it
        dialog.accept = lambda: QDialog.accept(dialog)

        # use stacked view
        stacked_widget = dialog.findChild(QStackedWidget)
        view = stacked_widget.findChild(QListView)

        # text updates
        line_edit = dialog.findChild(QLineEdit)
        def update_line_edit():
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append(f"{index.data()}")
            line_edit.setText(str.join(" ", selected))
        view.selectionModel().selectionChanged.connect(update_line_edit)
        dialog.directoryEntered.connect(lambda: line_edit.setText(""))

        # run dialog
        dialog.exec()
        if dialog.selectedFiles():
            return dialog.selectedFiles()[0]
        return None

    def __set_input_path(self: Self, path: Path) -> None:
        path.formalize()

        # make type selection based on path ending
        if (path.getLast().endswith(self.END_MCPACK)):
            self.__entry_data.input_game = self.BEDROCK
            self.__entry_data.input_path_type = self.MCPACK
            self.__input_type.setCurrentText("bedrock .mcpack file")
        elif (path.getLast().endswith(self.END_ZIP)):
            self.__entry_data.input_game = self.JAVA
            self.__entry_data.input_path_type = self.ZIP
            self.__input_type.setCurrentText("java .zip file")
        else:
            self.__entry_data.input_path_type = "folder"
            input_type_text: str = self.__input_path_text.toPlainText()
            if (
                input_type_text != "java folder"
                and input_type_text != "bedrock folder"
            ):
                self.__input_type.setCurrentText("select a game...")
        
        # set path
        self.__input_path_text.setText(path.getPath())

    def __clear_input_path(self: Self, msg: str|None = None) -> None:
        self.__input_path_text.setText("")
        self.__entry_data.input_path = None
        if msg != None: iUt.show_popup(self, "path cleared", msg)

    def __prompt_input_path(self: Self) -> None:
        input_str: str = self.__select_file_or_folder(f"Texture Packs (‹folder› *{self.END_MCPACK} *{self.END_ZIP})")
        if input_str: self.__set_input_path(Path(input_str, isRootDirectory=True))

    def __set_input_rejection(self: Self, state: bool) -> None:
            # browse button
                # set as disabled
            if (self.__input_path_button.isEnabled() != state):
                self.__input_path_button.setEnabled(state)

            # hover event
                # set to reject all at hover
            # click drag zone
                # reject all click events
            self.__reject_input = not state

    def __handle_drag_enter(self: Self, event: QDragEnterEvent) -> None:
        mime: QMimeData = event.mimeData()

         # reject all if reject input is enabled
        if self.__reject_input:
            self.__set_style_of(self.__input_drag, "state", "reject_hover")
            self.__input_drag_text.setText(self.INPUT_DRAG_REJECTED_HOVER)
            event.ignore()
            return

        # check if any of dragged leads to files
        if (
            mime.hasUrls()
            and any([url.isLocalFile() for url in mime.urls()])
        ):
            first_file: str = next((url.toLocalFile() for url in mime.urls()), None)
            if (
                os.path.isdir(first_file)
                or first_file.endswith(self.END_ZIP)
                or first_file.endswith(self.END_MCPACK)
            ):
                # change color, accept
                self.__set_style_of(self.__input_drag, "state", "valid_hover")
                self.__input_drag_text.setText(self.INPUT_DRAG_VALID_HOVER)
                event.acceptProposedAction()
                return
        self.__set_style_of(self.__input_drag, "state", "invalid_hover")
        self.__input_drag_text.setText(self.INPUT_DRAG_INVALID_HOVER)
        event.ignore()

    def __handle_drag_leave(self: Self, event: QDragLeaveEvent) -> None:
        # set color back to idle
        self.__set_style_of(self.__input_drag, "state", "idle")
        self.__input_drag_text.setText(self.INPUT_DRAG_IDLE_STR)

    def __handle_drop(self: Self, event: QDropEvent) -> None:
        mime: QMimeData = event.mimeData()
        # must already have file data because it passed drag check

        if mime.hasUrls():
            file_names: list[str] = [url.toLocalFile() for url in mime.urls()]
            self.__set_input_path(Path(file_names[0], isRootDirectory=True))

    def __handle_click(self: Self, event: QMouseEvent) -> None:
        if self.__reject_input: return # reject all if reject input is enabled
        self.__prompt_input_path()

    def __handle_input_path_text_changed(self: Self) -> None:
        input_path: str = self.__input_path_text.toPlainText()
        if input_path:
            self.__entry_data.input_path = input_path
            self.__input_drag_text.setText(self.INPUT_DRAG_HOLDING_STR)
            self.__set_style_of(self.__input_drag, "state", "hold")
        else:
            self.__input_drag_text.setText(self.INPUT_DRAG_IDLE_STR)
            self.__set_style_of(self.__input_drag, "state", "idle")

        # check build
        self.__update_for_build_requirements()

    def __handle_input_path_button_click(self: Self) -> None:
        self.__prompt_input_path()

    def __handle_input_type_changed(self: Self, text: str) -> None:
        # clear msgs
        MODERN_CLEAR_MSG: str|None = "cleared the input path because it does not match the selected input game"
        LCE_CLEAR_MSG: str|None = None

        # button states
        MODERN_BUTTON_STATE: bool = True
        LCE_BUTTON_STATE: bool = False

        # switch modes based on selection
        input_type_text: str = self.__input_path_text.toPlainText()
        match text:
            case "select a game...":
                self.__entry_data.input_game = None
                self.__entry_data.input_path_type = None
                self.__set_versions(None)
                self.__set_structures(None)
            case "java folder":
                self.__entry_data.input_game = self.JAVA
                self.__entry_data.input_path_type = "folder"
                if (
                    input_type_text
                    and (
                        input_type_text.endswith(self.END_ZIP)
                        or input_type_text.endswith(self.END_MCPACK)
                    )
                ): self.__clear_input_path(MODERN_CLEAR_MSG)
                self.__set_input_rejection(MODERN_BUTTON_STATE)
                self.__set_versions(self.JAVA)
                self.__set_structures(self.JAVA)
            case "java .zip file":
                self.__entry_data.input_game = self.JAVA
                self.__entry_data.input_path_type = "zip"
                if (
                    input_type_text
                    and not input_type_text.endswith(self.END_ZIP)
                ): self.__clear_input_path(MODERN_CLEAR_MSG)
                self.__set_input_rejection(MODERN_BUTTON_STATE)
                self.__set_versions(self.JAVA)
                self.__set_structures(self.JAVA)
            case "bedrock folder":
                self.__entry_data.input_game = self.BEDROCK
                self.__entry_data.input_path_type = "folder"
                if (
                    input_type_text
                    and (
                        input_type_text.endswith(self.END_ZIP)
                        or input_type_text.endswith(self.END_MCPACK)
                    )
                ): self.__clear_input_path(MODERN_CLEAR_MSG)
                self.__set_input_rejection(MODERN_BUTTON_STATE)
                self.__set_versions(self.BEDROCK)
                self.__set_structures(self.BEDROCK)
            case "bedrock .mcpack file":
                self.__entry_data.input_game = self.BEDROCK
                self.__entry_data.input_path_type = "mcpack"
                if (
                    input_type_text
                    and not self.__input_path_text.toPlainText().endswith(self.END_MCPACK)
                ): self.__clear_input_path(MODERN_CLEAR_MSG)
                self.__set_input_rejection(MODERN_BUTTON_STATE)
                self.__set_versions(self.BEDROCK)
                self.__set_structures(self.BEDROCK)
            case "xbox one/nintendo switch default textures":
                self.__entry_data.input_game = "wiiu"
                self.__entry_data.input_path_type = "‹none›"
                self.__clear_input_path(LCE_CLEAR_MSG)
                self.__set_input_rejection(LCE_BUTTON_STATE)
                self.__set_versions(None)
                self.__set_structures(self.XBOX_ONE)
            case "wiiu default textures":
                self.__entry_data.input_game = "wiiu"
                self.__entry_data.input_path_type = "‹none›"
                self.__clear_input_path(LCE_CLEAR_MSG)
                self.__set_input_rejection(LCE_BUTTON_STATE)
                self.__set_versions(None)
                self.__set_structures(self.WIIU)
            case "xbox360/ps3/psV default textures":
                self.__entry_data.input_game = "wiiu"
                self.__entry_data.input_path_type = "‹none›"
                self.__clear_input_path(LCE_CLEAR_MSG)
                self.__set_input_rejection(LCE_BUTTON_STATE)
                self.__set_versions(None)
                self.__set_structures(self.XBOX360)
            case "ps4 default textures":
                self.__entry_data.input_game = "wiiu"
                self.__entry_data.input_path_type = "‹none›"
                self.__clear_input_path(LCE_CLEAR_MSG)
                self.__set_input_rejection(LCE_BUTTON_STATE)
                self.__set_versions(None)
                self.__set_structures(self.PS4)

        # check build
        self.__update_for_build_requirements()

    def __set_versions(self: Self, version: str|None) -> None:
        match version:
            case self.JAVA:
                if self.__curr_version_set != self.JAVA:
                    self.__input_version.clear()
                    self.__input_version.addItems(GlobalLibs.input_versions_java_plus)
                    self.__curr_version_set = self.JAVA
                    self.__entry_data.input_version = GlobalLibs.input_versions_java[0]
            case self.BEDROCK:
                if self.__curr_version_set != self.BEDROCK:
                    self.__input_version.clear()
                    self.__input_version.addItems(GlobalLibs.input_versions_bedrock_plus)
                    self.__curr_version_set = self.BEDROCK
                    self.__entry_data.input_version = GlobalLibs.input_versions_bedrock[0]
            case _:
                self.__input_version.clear()
                self.__curr_version_set = None
                self.__entry_data.input_version = None

    def __handle_input_version_changed(self: Self, index: int) -> None:
        if (self.__curr_version_set == "java"):
            self.__entry_data.input_version = GlobalLibs.input_versions_java[index]
        elif (self.__curr_version_set == "bedrock"):
            self.__entry_data.input_version = GlobalLibs.input_versions_bedrock[index]
        else:
            self.__entry_data.input_version = None

        # check build
        self.__update_for_build_requirements()

    def __handle_output_path_text_changed(self: Self) -> None:
        output_path: str = self.__output_path_text.toPlainText()
        if output_path:
            self.__entry_data.output_path = output_path

        # check build
        self.__update_for_build_requirements()

    def __handle_output_path_button_click(self: Self) -> None:
        output_str: str = self.__select_folder()
        if output_str: self.__output_path_text.setText(output_str)

    def __set_structures(self: Self, structure: str|None) -> None:
        # check each game type
        for game in [self.JAVA, self.BEDROCK, self.NINTENDO_SWITCH, self.PS3, self.PS4, self.PSV, self.WIIU, self.XBOX_ONE, self.XBOX360]:
            if (structure == game):
                self.__output_structure.clear()
                curr_lib = self.GAME_TO_OUTPUT_STRUCTURE_LIB[game]
                self.__output_structure.addItems(curr_lib)
                self.__curr_structure_set = game
                self.__entry_data.output_structure = curr_lib[0]
                self.__set_drives(curr_lib[0])
                break
        else:
            self.__output_structure.clear()
            self.__curr_structure_set = None
            self.__entry_data.output_structure = None
            self.__set_drives(None)

    def __handle_output_structure_changed(self: Self, index: int) -> None:
        # set entry data to the current structure set's index equal
        output_structure = None
        if self.__curr_structure_set is not None:
            output_structure: str = self.GAME_TO_OUTPUT_STRUCTURE_LIB[self.__curr_structure_set][index] # get str selection
            self.__entry_data.output_structure = output_structure 
        else:
            self.__entry_data.output_structure = None
        self.__set_drives(output_structure) # set drives ╎ set drives changes must be mirrored in __set_structures

        # check build
        self.__update_for_build_requirements()

    def __if_path_exists(
        self: Self, 
        which_path: str,
        callback: Callable[[str], None]|None = None
    ) -> None:
        # select and validate ‹which_path›
        host: QWidget|None = None
        match which_path:
            case "input": host = self.__input_path_text
            case "output": host = self.__output_path_text
            case _: raise ValueError(f"⸉{which_path}⸉ is not a valid selector")
        path: str = host.toPlainText()

        # check if path exists
        if os.path.exists(path):
            if callback is not None: 
                callback(path)
        else:
            host.setText("")
            iUt.show_popup(self, "file/folder doesn't exist", f"the specified {which_path} directory ({path}) could not be found. as a result it has been cleared")
    
    def __handle_output_open_button_click(self: Self) -> None:
        # check if folder exists
        self.__if_path_exists("output", iUt.open_in_explorer)

    def __set_drives(self: Self, output_structure: str|None) -> None:
        # helper for finalizing
        def set_entry_data() -> None: self.__entry_data.output_drive = GlobalLibs.output_drives[0]

        # wiiu
        if (
            (output_structure == "wiiu port pack (root directory)")
            or (output_structure == "wiiu modpack (sdcafiine)")
        ): 
            self.__advanced_drive.clear()
            self.__advanced_drive.addItems(GlobalLibs.output_drives)
            set_entry_data(); return

        # anything else or none
        self.__entry_data.output_drive = None
        self.__advanced_drive.clear()

    def __handle_advanced_drive_changed(self: Self, index: int|None) -> None:
        if index is not None:
            self.__entry_data.output_drive = GlobalLibs.output_drives[index]
        self.__entry_data.output_drive = None

        # check build
        self.__update_for_build_requirements()

    def __handle_advanced_error_changed(self: Self, index: int) -> None:
        self.__entry_data.build_mode = GlobalLibs.modes_build[index]
        
        # check build
        self.__update_for_build_requirements()
    
    def __handle_advanced_size_changed(self: Self, index: int) -> None:
        mode: str = GlobalLibs.modes_size[index]
        match mode:
            case "x16": 
                self.__entry_data.size_mode = 16
                self.__entry_data.complex_processing = True
            case "x32":
                self.__entry_data.size_mode = 32
                self.__entry_data.complex_processing = True
            case "x32 simple processing":
                self.__entry_data.size_mode = 32
                self.__entry_data.complex_processing = False
            case "x64 simple processing":
                self.__entry_data.size_mode = 64
                self.__entry_data.complex_processing = False

        # check build
        self.__update_for_build_requirements()

    def __set_settings_enabled(self: Self, value: bool) -> None: 
        self.__finalized_build.setEnabled(value)
        self.__settings_container.setEnabled(value)

    def __handle_advanced_log_button_click(self: Self) -> None:
        self.__log_window.show()

    def __handle_advanced_clear_button_click(self: Self) -> None:
        def clear_files(path_str: str) -> None:
            self.__set_settings_enabled(False)
            def finalize_success() -> None:
                self.__finalized_bar.stepReset()
                iUt.show_popup(self, "success", "finished clearing. files have been attempted to be sent to the recycle bin")
                self.__set_settings_enabled(True)
            def finalize_fail() -> None:
                self.__finalized_bar.stepReset()
                iUt.show_popup(self, "failed", "failed to complete clearing. some files may have been attempted to be sent to the recycle bin")
                self.__set_settings_enabled(True)

            # confirm
            result: QMessageBox.StandardButton = iUt.show_popup(
                self, 
                "please confirm", 
                f"are you sure you want to clear the contents of ⸉{path_str}⸉?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes: return

            # get files
            handler = PathHandler(xLPyBasicsPath(self.__entry_data.output_path, prepension=None))
            items: tuple[PathHandler, ...]|df.Type.Empty = handler.read_dir(Search.Settings(
                include=Search.Include.FilesAndAllDirectories,
                recursion_depth=Search.MAX_RECURSION
            ))
            if len(items) == 0: 
                finalize_success()
                return

            # ⧼bar⧽ setup
            self.__finalized_bar.setRange(0, len(items))
            self.__finalized_bar.setValue(len(items))

            # set progress bar & delete
            # another cleanup issue with runner idrc abt
            def clear_file(data: tuple[int, PathHandler]) -> None:
                item = data[1]
                item.remove(do_recycle=True)
            self.__runner = create_loop_runner(items, clear_file)
            self.__runner.on_progress.connect(lambda _: self.__finalized_bar.stepBack())
            self.__runner.on_complete.connect(finalize_success)
            self.__runner.on_exception.connect(finalize_fail)
            self.__runner.start()
        self.__if_path_exists("output", clear_files)

    def __handle_advanced_info_button_click(self: Self) -> None:
        self.__help_window.show()
        
    def __set_finalized_build_state(self: Self, state: bool) -> None:
        self.__finalized_build.setToolTip(self.BUILD_ENABLED_TOOLTIP if state else self.BUILD_DISABLED_TOOLTIP)
        self.__finalized_build.setEnabled(state)

    def __update_for_build_requirements(self: Self) -> None:
        # check input game
        if self.__entry_data.input_game is None:
            self.__set_finalized_build_state(False); return
        if (
            (self.__entry_data.input_game == self.JAVA)
            or (self.__entry_data.input_game == self.BEDROCK)
        ): 
            # check input path
            if self.__entry_data.input_path is None:
                self.__set_finalized_build_state(False); return
            
            # check version
            if self.__entry_data.input_version is None:
                self.__set_finalized_build_state(False); return
            
        # check output path
        if self.__entry_data.output_path is None:
            self.__set_finalized_build_state(False); return
        
        # check output structure
        if self.__entry_data.output_structure is None:
            self.__set_finalized_build_state(False); return
        if (
            (self.__entry_data.output_structure == "wiiu port pack (root directory)")
            or (self.__entry_data.output_structure == "wiiu modpack (sdcafiine)")
        ):
            # check output drive
            if self.__entry_data.output_drive is None:
                self.__set_finalized_build_state(False); return
            
        # check build mode
        if self.__entry_data.build_mode is None:
            self.__set_finalized_build_state(False); return

        # check size mode
        if self.__entry_data.size_mode is None:
            self.__set_finalized_build_state(False); return
        
        # if everything was fine, set build to true
        self.__set_finalized_build_state(True)

    def __handle_finalized_build_click(self: Self) -> None:
        # helper for errors when building
        def show_error(err: Exception) -> None: iUt.show_popup(self, "error when buidling", str(err))

        # helper to set None as an empty string
        def none_empty(val: None|Any) -> str|Any: return "" if val == None else val

        # finish helper to re-enable settings
        self.__set_settings_enabled(False)

        # validate input and output paths still exist
        if (
            (self.__entry_data.input_game == self.JAVA)
            or (self.__entry_data.input_game == self.BEDROCK)
        ): self.__if_path_exists("input")
        self.__if_path_exists("output")

        # reset bar
        self.__finalized_bar.stepReset()
        self.__log_window.clear_text()

        # get logger flags
        flags, invalid_flags = self.__logger_handler.get_flags()
        if invalid_flags: iUt.show_popup(self, "invalid logger flags", "the provided logger flags were invalid, using default flags instead")

        # run entry point
        entry = EntryPoint(
            errorMode=self.__entry_data.build_mode,
            processingSize=self.__entry_data.size_mode,
            useComplexProcessing=self.__entry_data.complex_processing,
            
            inputPath=none_empty(self.__entry_data.input_path),
            inputPathType=none_empty(self.__entry_data.input_path_type),
            inputGame=none_empty(self.__entry_data.input_game),
            inputVersion=none_empty(self.__entry_data.input_version),
            
            outputPath=self.__entry_data.output_path,
            outputStructure=self.__entry_data.output_structure,
            outputDrive=none_empty(self.__entry_data.output_drive),

            logging=flags,
            assoc_bar=self.__finalized_bar,
            assoc_logwindow=self.__log_window,
            on_exception=show_error
        )

        # run entry point & finish
        def finished() -> None:
            self.__finalized_bar.setValue(self.__finalized_bar.range)
            self.__set_settings_enabled(True)
        entry.start(finished)

def launch() -> None:
    # app construction 
    app = QApplication(sys.argv)
    ICON = QIcon("resources/Re.ico")
    app.setWindowIcon(ICON)
    styles_handler = PathHandler(xLPyBasicsPath(
        "light", 
        extension="css", 
        prepension=xLPyBasicsPath.get_meipass(xLPyBasicsPath.cwd()))
    )
    styles_text = styles_handler.read()
    app.setStyleSheet(styles_text)

    # set main window
    window = MainWindow(ICON)
    window.show()
    sys.exit(app.exec())
