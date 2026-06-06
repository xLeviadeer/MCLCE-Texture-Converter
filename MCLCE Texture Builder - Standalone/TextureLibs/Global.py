# IMPORTANT: all variables in global must be set at startup because they have no default value and will cause errors

from CodeLibs import LoadingBar
from CodeLibs import Logger as log
from CodeLibs.Logger import print
import os
from sys import exit
from typing import Union

# try to import Image, but if not continue running without image
try:
    from TextureLibs.SizingImage import SizingImage as Image
except ModuleNotFoundError:
    pass # this will cause the program to fail later, but only runs when installing Pillow

# --- GENERAL SETTINGS ---

# the error processing mode the program uses when an error occurs (write an error texture or replace it with the known info)
errorMode = None # replace or error

# enables or disables complex processing for specific functions like weather or kelp. using complex processing may result 
# in better and/or more "natural" looking textures but will majorly compromise on processing time
useComplexProcessing = None # true or false

# the debugging status of the program in regards to writing error textures for unknown custom functions
useErrorTexture = None # true or false

# --- INPUT SETTINGS ---

# the input path the program will use to search for convertable files
inputPath = None 

# the game the program will assume that the input textures come from
inputGame = None # java or bedrock

# the version the program will assume that the input textures come from
inputVersion = None # version number

# --- OUTPUT SETTINGS ---

# the output path the program will use to export files to
outputPath = None

# whether or not the program will use the output file structure or dump files
outputDump = None # dump or build

# the file structure (export preset) that the program will use to write files
outputStructure = None # wiiu, modpack, (etc.)
def getLayerVersion() -> Union[str, None]:
    """Gets the layer version using the outputStructure

    Returns:
        Union[str, None]: Returns a str layer version or None if it's 1.13
    """

    match outputStructure:
        case "switch" | "xboxOne":
            return "1.12"
        case "ps4":
            return "1.14"
        case _:
            return None
def getLayerGame() -> Union[str, None]:
    """Gets the layer game using the outputStructure

    Returns:
        Union[str, None]: Returns a str layer string or None if it's a 1.13 equivalent
    """

    if (outputStructure == "ps4"): return outputStructure
    else: return "wiiu"

# the usb or system location to write files to (only used if not using dump mode)
outputDrive = None # usb or system

# --- RESOURCES ----

# iter value for debugging by using some kind of global number for tracking
iter = 0

# name of the currentlty running thread
name = None

# an instance of the loading bar set from the entry point
bar = None

# the name of the type which contains miscellaneous textures. This controls which type will read from a base directory instead of a subdirectory
misc = "misc"

# a list of notExpected errors
notExpectedErrors = []

# a list of incorrectSizeErrors
incorrectSizeErrors = []

# a multidimensional dictionary containing information about the current process length 
processingLength = {}

# the working directory with slight changes based on where the program is executed from
mainLoc = None
def getMainWorkingLoc():
    if (mainLoc == None):
        return os.getcwd()
    else:
        return os.getcwd() + "\\" + mainLoc

# the notFound image
notFoundImage = None
try:
    notFoundImage = Image.open(getMainWorkingLoc() + "\\base_textures\\notFound.png") # not found image
except:
    pass # do, nothing, cannot print error without creating errors
def updateNotFoundImage(): # updates the notFoundImage location
    try:
        global notFoundImage
        notFoundImage = Image.open(getMainWorkingLoc() + "\\base_textures\\notFound.png")
    except:
        print("attempt to update the notFound image failed", log.EXIT)
        try: # attempts to close the bar, but it may not exist
            bar.close()
        except:
            exit()

# the error image
    # error image is only setup to work while in wiiuEntry, debug mode
errorImage = None
try:
    errorImage = Image.open(getMainWorkingLoc() + "\\base_textures\\error.png")
except:
    pass # this will absolutely break stuff if you try to use errorImage from programEntry

# end program helper 
def endProgram(message:str=None): # ends the program
    if (not isinstance(bar, LoadingBar.bar)):
        print(message, log.EXIT)
        exit()
    else:
        bar.close(message)