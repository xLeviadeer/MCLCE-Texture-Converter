from typing import Self, Callable
from builtins import type as typeof
import zipfile
import os
import shutil

from xLPyBasics.Dependencies import compare_versions
from xLPyBasics.xQWERTILE import try_parse, repr
from xLPyBasics.Singletons import Singleton

import TextureLibs.Global as Global
from CodeLibs import Logger as log
from CodeLibs.Logger import print
from TextureLibs.SupportedTypes import supportedVersions
import TextureLibs.SizingImage as SizingImage
from InterfaceLibs import StepProgressBar, StepProgressBarProto, LogWindow, LogWindowProto
from CodeLibs.Threading import create_runner

class EntryPoint(Singleton):
    # ———CONSTRUCTOR———

    def __init__(
        self: Self,
        errorMode: str,
        processingSize: int,

        inputPath: str,
        inputPathType: str,
        inputGame: str,
        inputVersion: str,

        outputPath: str,
        outputStructure: str,
        outputDrive: str,

        useComplexProcessing: bool,
        useErrorTexture: bool = False,

        mainLoc: str|None = None,
        logging: list[log.LoggerMode]|None = None,
        isDirectPath: bool = False, # whether or not the path is exactly the path with no excess folders or not
        forceDumpMode: bool = False,

        assoc_bar: StepProgressBar|None = None,
        assoc_logwindow: LogWindow|None = None,
        on_exception: Callable[[Exception], None]|None = None
    ) -> Self:
        self.errorMode = EntryPoint.cast(str, errorMode)
        self.processingSize = EntryPoint.cast(int, processingSize)
        
        self.inputPath = EntryPoint.cast(str, inputPath)
        self.inputPathType = EntryPoint.cast(str, inputPathType)
        self.inputGame = EntryPoint.cast(str, inputGame)
        self.inputVersion = EntryPoint.cast(str, inputVersion)

        self.outputPath = EntryPoint.cast(str, outputPath)
        self.outputStructure = EntryPoint.cast(str, outputStructure)
        self.outputDrive = EntryPoint.cast(str, outputDrive)

        self.mainLoc = EntryPoint.cast(str, mainLoc, nullable=True)
        self.logging = logging # no casting on the list, logging is also not verified that items are correct
        self.isDirectPath = EntryPoint.cast(bool, isDirectPath)
        self.forceDumpMode = EntryPoint.cast(bool, forceDumpMode)

        self.on_exception = on_exception

        Global.bar = assoc_bar if assoc_bar is not None else StepProgressBarProto()
        Global.log_win = assoc_logwindow if assoc_logwindow is not None else LogWindowProto(None)
        Global.useErrorTexture = useErrorTexture
        Global.useComplexProcessing = EntryPoint.cast(bool, useComplexProcessing)

    # constructor helper for value checking
    @classmethod
    def cast[T](
        cls: type[Self], 
        type: type[T], 
        value: object, 
        nullable: bool = False
    ) -> T:
        # allow nullability
        if (
            nullable
            and (value is None)
        ): return None

        # pass if type match & fail if not string
        if isinstance(value, type): return value
        if isinstance(value, str): raise TypeError(f"value ({repr(value)}) did not match type ({repr(type)}) and was not a str")

        # return parse (allowing exceptions)
        return try_parse(value, type)

    # ———METHODS———

    # output game (index) function
    def _setOutputStructure(self: Self) -> None:
        # based on `global/` data file options
        match (self.outputStructure):
            case "wiiu dump":
                Global.outputStructure = "wiiu"
                Global.outputDump = "dump"
                Global.outputDrive = "system"
            case "wiiu port pack (root directory)": 
                Global.outputStructure = "wiiu"
                Global.outputDump = "build"
                Global.outputDrive = self.outputDrive
            case "wiiu modpack (sdcafiine)":
                Global.outputStructure = "modpack"
                Global.outputDump = "build"
                Global.outputDrive = self.outputDrive
            case "nintendo switch dump": 
                Global.outputStructure = "switch"
                Global.outputDump = "dump"
                Global.outputDrive = "system"
            case "xbox 360 dump":
                Global.outputStructure = "xbox360"
                Global.outputDump = "dump"
                Global.outputDrive = "system"
            case "xbox one dump":
                Global.outputStructure = "xboxOne"
                Global.outputDump = "dump"
                Global.outputDrive = "system"
            case "PS 3 dump":
                Global.outputStructure = "ps3"
                Global.outputDump = "dump"
                Global.outputDrive = "system"
            case "PS vita dump":
                Global.outputStructure = "psV"
                Global.outputDump = "dump"
                Global.outputDrive = "system"
            case "PS 4 dump":
                Global.outputStructure = "ps4"
                Global.outputDump = "dump"
                Global.outputDrive = "system"
            case _:
                Global.stopGen("EntryPoint's outputStructure wasn't set to a valid value")

        # check for forced dump mode
        if (self.forceDumpMode == True):
            Global.outputDump = "dump"

    # start function will take all of the collected values from init and assign them in the correct order before executing
    def start(self: Self, on_complete: Callable[[], None]|None = None) -> None:
        """
        Description:
            Starts the entry point aka runs/executes it
        """

        # set so that getMainLocWorking() works
        Global.inputPath = self.inputPath

        # logging settings
        log.disableAll(log.EXIT)
        if (self.logging != None): # logging false and logging types
            for logType in self.logging:
                log.setStatus(logType, True)

        # start 
        if (self.inputGame == "wiiu"): self.__start_wiiu(on_complete)
        else: self.__start_modern(on_complete)

    def __start_wiiu(self: Self, on_complete: Callable[[], None]|None = None) -> None:
        # set out here so other threads still have global context
        Global.inputPath = "WiiU Default"
        Global.outputPath = self.outputPath
        Global.inputGame = "wiiu"
        self._setOutputStructure()
        Global.mainLoc = self.mainLoc

        # multithreading block
        SizingImage.changeProcessingSize(self.processingSize)
        # has to be updated after printing is set so print() works
        # also has to be set after sizing image has been imported
        Global.updateNotFoundImage()
        # has to be imported down here (to ensure that files are read properly based on Global)
        import TextureLibs.TextureCreator as TextureCreator

        # set up the loading bar
        Global.processingLength = TextureCreator.getProcessingLengthDict("java")
        Global.bar.setRange(0, Global.processingLength["cumulative"])

        # create runner
        # this doesn't get cleaned up but idrc, the runner object should be tiny anyways
        self.runner = create_runner(TextureCreator.generateWiiuTextures)
        if self.on_exception is not None: self.runner.on_exception.connect(self.on_exception)
        if on_complete is not None: self.runner.on_complete.connect(on_complete)
        self.runner.start()

    @property
    def __ext_tmp_path(self: Self) -> str: 
        return f"{Global.getMainWorkingLoc()}\\extraction_temporary"

    def __start_modern(self: Self, on_complete: Callable[[], None]|None = None) -> None:
        # check of the version is within the supported window
        if (compare_versions(self.inputVersion, supportedVersions[self.inputGame]["min"], direction=False) 
            or compare_versions(self.inputVersion, supportedVersions[self.inputGame]["max"], direction=True)):
            Global.stopGen(f"version ({self.inputVersion}) too young or old; version not within the supported versions: {".".join(map(str, supportedVersions[self.inputGame]["min"]))} to {".".join(map(str, supportedVersions[self.inputGame]["max"]))}")

        # set out here so other threads still have global context
        Global.outputPath = self.outputPath
        Global.inputGame = self.inputGame
        Global.inputVersion = self.inputVersion
        Global.errorMode = self.errorMode
        self._setOutputStructure()
        Global.mainLoc = self.mainLoc

        # multithreading block
        SizingImage.changeProcessingSize(self.processingSize)
        # has to be updated after printing is set so print() works
        # also has to be set after sizing image has been imported
        Global.updateNotFoundImage()
        # has to be imported down here (to ensure that files are read properly based on Global)
        import TextureLibs.TextureCreator as TextureCreator

        # set up the loading bar
        Global.processingLength = TextureCreator.getProcessingLengthDict(Global.inputGame)
        totalLength = Global.processingLength["cumulative"]
        extractionLength = totalLength / 4
        if ((self.inputPathType == "zip") or (self.inputPathType == "mcpack")):
            totalLength += extractionLength
        Global.bar.setRange(0, totalLength)

        # create runner
        # this doesn't get cleaned up but idrc, the runner object should be tiny anyways
        def run():
            # extract stuff & start
            self.__extractionMethod(extractionLength)
            TextureCreator.translateForAllTypes()

            # remove temporary extraction path if it was made
            if (os.path.isdir(self.__ext_tmp_path)): shutil.rmtree(self.__ext_tmp_path)
        self.runner = create_runner(run)
        if self.on_exception is not None: self.runner.on_exception.connect(self.on_exception)
        if on_complete is not None: self.runner.on_complete.connect(on_complete)
        self.runner.start()

    # method which finds where input files are and extracts them
    def __extractionMethod(self: Self, extractionLength: int) -> None:
        troubleLocatingErrorMessage = "Something went wrong, please try the following before contacting support with the \"help\" button\nIs your input path incorrect?\n\nERROR: pathNotFound - "

        def fourthStep():
            Global.bar.step(extractionLength / 4)

        def extractTextures(inputPathType):
            # determine readpath
            readPath = None
            if (inputPathType == "zip"):
                readPath = "assets/minecraft/textures/"
            elif (inputPathType == "mcpack"):
                readPath = "textures/"
            fourthStep()

            # create folder
            if (os.path.isdir(self.__ext_tmp_path)): # if directory exists
                shutil.rmtree(self.__ext_tmp_path)
            os.mkdir(self.__ext_tmp_path)
            fourthStep()

            # extract to folder
            zip = zipfile.ZipFile(Global.inputPath) # get zip as a whole
            for file in zip.namelist():
                if file.startswith(readPath):
                    zip.extract(file, self.__ext_tmp_path)
            fourthStep()

            # set input path to this new location
            Global.inputPath = self.__ext_tmp_path + "\\" + readPath.replace("/", "\\")
            fourthStep()

        # determine if it's folder or pack and mount to correct location
        if (self.inputPathType == "folder"): # FOLDER
            if (self.isDirectPath == True):
                pass # exits the loop to continue normal processing with no changes
            elif (self.inputGame == "java"): # JAVA FOLDER
                # -- mount --
                found = False

                # if the file is already on point
                if (Global.inputPath.split("\\")[-1] == "textures"):
                    found = True
                else: # if the file needs to be mounted inwards
                    # for through possible options
                    inputPosibs = [
                        "assets",
                        "minecraft",
                        "textures"
                    ]
                    i = 0
                    while i < len(inputPosibs): 
                        if (os.path.isdir(Global.inputPath + "\\" + inputPosibs[i])):
                            Global.inputPath = Global.inputPath + "\\" + str.join("\\", inputPosibs[-(len(inputPosibs) - i):])
                            found = True
                            break
                        i += 1
                
                # check if the path was found
                if (found == False):
                    Global.stopGen(f"{troubleLocatingErrorMessage}JAVA_FOLDER")
            elif (self.inputGame == "bedrock"): # BEDROCK FOLDER
                # -- mount --
                found = False

                # if the file is already on point
                if (Global.inputPath.split("\\")[-1] == "textures"):
                    found = True

                # check if the folder contains textures folder
                if (os.path.isdir(Global.inputPath + "\\textures")):
                    Global.inputPath = Global.inputPath + "\\textures"
                    found = True

                # check if the path was found
                if (found == False):
                    Global.stopGen(f"{troubleLocatingErrorMessage}BEDROCK_FOLDER")

        elif (self.inputPathType == "zip"): # .ZIP
            # check if the zip contains the textures folder
            if (zipfile.Path(Global.inputPath, "assets/minecraft/textures/").is_dir() == False): # checks if it DOESN'T exist
                Global.stopGen(f"{troubleLocatingErrorMessage}ZIP")

            extractTextures("zip") # sets up the extraction temporary as the input path

        elif (self.inputPathType == "mcpack"):
            # check if the mcpack contains textures folder
            if (zipfile.Path(Global.inputPath, "textures/").is_dir() == False): # checks if it DOESN'T exist
                Global.stopGen(f"{troubleLocatingErrorMessage}MCPACK")

            extractTextures("mcpack") # sets up the extraction temporary as the input path

        else:
            Global.stopGen("Something went wrong, please contact support using the \"help\" button\n\nERROR: inputPathType")

    # global assignment for testing only
    def testAssign(self):
        """
        Description:
            simply assigns the values to Global so that the program can continue during testing
        """

        import TextureLibs.SizingImage as SizingImage

        Global.errorMode = self.errorMode
        SizingImage.changeProcessingSize(self.processingSize)
        
        Global.inputPath = self.inputPath 
        Global.inputGame = self.inputGame
        Global.inputVersion = self.inputVersion

        Global.outputPath = self.outputPath
        self._setOutputStructure()

        Global.mainLoc = self.mainLoc
        # logging
        log.disableAll(log.EXIT)
        if (self.logging != None): # logging false and logging types
            for logType in self.logging:
                log.setStatus(logType, True)
