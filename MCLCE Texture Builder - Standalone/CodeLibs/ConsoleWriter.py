import TextureLibs.Global as Global
import os
from . import Logger as log
from TextureLibs.SizingImage import SizingImage as Image
from CodeLibs.Path import Path
from CodeLibs.Path import testPath
import traceback
from builtins import type as typeof

# ERRORS

class SpecialStringError(Exception):
    pass

# CLASSES

class SpecialString():
    matches = None

    def __init__(self, *matches) -> None:
        """
        Description:
            Checker for strings to see if they match an exact case of possibilities
        ---
        Arguments:
            - Strings that will be matches
        """

        matches = list(matches)

        # change all matches to lower case
        i = 0
        while i < len(matches):
            matches[i] = matches[i].lower()
            i += 1

        self.matches = matches

    def check(self, string:str, doErrorHandling:bool=True):
        """
        Description:
            Checks the input string to see if it follows the possible matches
        ---
        Arguments:
            - string : String <>
            - doErrorHandling : Boolean <True>
        ---
        Returns:
            - String: when the string matched
            - SpecialStringError: when doErrorHandling is False and the string didn't match
        """

        for match in self.matches:
            if (string.lower() == match):
                return string
        # else case
        if (doErrorHandling == True):
            for line in traceback.format_stack()[:-1]: # prints a traceback (but not the last trace)
                print(line.strip())
            Global.endProgram(f"String ({string.lower()}) could not find a match, program exited")
        else:
            raise SpecialStringError()
        
    def __str__(self) -> str:
        return self.matches

class _WriteLocation():
    def __init__(self, section:str, addon:Path, *, mipMapLevel:int=1) -> None:
        """
        Description:
            Base class for different write locations
        ---
        Arguments:
            - section : String <>
                - main
                - 122
                - title
            - addon : String <>
                - Path (class) for the extra addon path of the specific file
            - mipMapLevel : Integer <1>
                - Handling for saving MipMaps
        """

        # handle mipmaps
        if (mipMapLevel > 1):
            addon.replaceAt((addon.getLength() - 1), f"{addon.getLast()}MipMapLevel{mipMapLevel}")

        # pathing with addon and saveName
        testPath(addon) # checks if addon is a path (handles exiting)
        addon.formalize()
        self.saveName = addon.getLast()

        # finalize pathing
        self.path = Path("content", "Common", "res")
        section = self.translate(SpecialString("main", "122", "title").check(section))
        self.path.append(
            section.getPath(withFirstSlash=False), 
            addon.getPath(withFirstSlash=False)
            )

    def getPath(self):
        return self.path
    
    def getPathNoSaveName(self):
        self.path.formalize()
        return self.path.slice(0, (self.path.getLength() - 1), withFirstSlash=False)
    
    def getPathAsPath(self):
        """
        Description:
            Returns the actual Path() variable not a string
        """
        return self.path

    def translate(self, value):
        match (value):
            case "main":
                return Path()
            case "122":
                return Path("1_2_2")
            case "title":
                return Path("TitleUpdate", "res")
            case _:
                return "None"

    def getSaveName(self):
        return self.saveName

    def __str__(self) -> str:
        return self.path.getPath()

class WiiULocation(_WriteLocation):
    def __init__(self, loc:str, side:str, section:str, addon:Path, *, mipMapLevel:int=1) -> None:
        """
        Description:
            WiiU location handler
        ---
        Arguments:
            - loc : String <>
                - usb
                - sys
            - side : String <>
                - update
                - base
            - section : String <>
                - main
                - 122
                - title
            - addon : String <>
                - Path (class) for the extra addon path of the specific file
            - mipMapLevel : Integer <1>
                - Handling for saving MipMaps
        """

        super().__init__(section, addon, mipMapLevel=mipMapLevel)
        side = self.translate(SpecialString("update", "base").check(side))
        loc = self.translate(SpecialString("usb", "system").check(loc))
        self.path.prepend(
            loc.getPath(withFirstSlash=False), 
            "usr", 
            "title", 
            side.getPath(withFirstSlash=False), 
            "101d9d00"
            )

    def translate(self, value):
        superTrans = super().translate(value)
        if (superTrans != "None"): return superTrans
        match (value):
            case "update":
                return Path("0005000e")
            case "base":
                return Path("00050000")
            case "usb":
                return Path("storage_slc")
            case "system":
                return Path("storage_mlc")

class ModPackLocation(_WriteLocation):
    def __init__(self, name:str, section:str, addon:Path, *, mipMapLevel:int=1) -> None:
        """
        Description:
            Modpack location handler
        ---
        Arguments:
            - name : String <>
                - should be set to the name of input folder
            - section : String <>
                - main
                - 122
                - title
            - addon : String <>
                - Path (class) for the extra addon path of the specific file
            - mipMapLevel : Integer <1>
                - Handling for saving MipMaps
        """

        super().__init__(section, addon, mipMapLevel=mipMapLevel)
        self.path.prepend(f"{name} Modpack")

class DebugLocation(_WriteLocation):
    def __init__(self, section:str, addon:Path, *, mipMapLevel:int=1) -> None:
        """
        Description:
            Debug location; SHOULD NOT BE USED UNLESS FOR DEBUGGING
        ---
        Arguments:
            - name : String <>
                - should be set to the name of input folder
            - section : String <>
                - main
                - 122
                - title
            - addon : String <>
                - Path (class) for the extra addon path of the specific file
            - mipMapLevel : Integer <1>
                - Handling for saving MipMaps
        """

        super().__init__(section, addon, mipMapLevel=mipMapLevel)
        self.path.prepend("Debug Pack")

def generateLocation(type:str, loc:list, mipMapLevel:int=1, arg=None):
    """
    Description:
        Finds and generates a valid WriteLocation based in the input type (game type) and loc (data)
    ---
        Arguments:
        - type : String <>
            - wiiu
                - pass loc data
            - modpack
                - expects name (str) as extra arg
        - loc : List <>
            - Loc data that is specific to the type of input
        - mipMapLevel : Integer <1>
            - Handling for saving MipMaps
    ---
        Returns:
        - subclass of WriteLocation
    """

    match (type):
        case "wiiu":
            return WiiULocation(Global.outputDrive, loc[0], loc[1], Path(loc[2]), mipMapLevel=mipMapLevel)
        case "modpack":
            # arg is expected to be a name
            return ModPackLocation(arg, loc[1], Path(loc[2]), mipMapLevel=mipMapLevel)
        case _:
            # only for debugging, ensures output structures can be written even if their write type doesn't exist
            return DebugLocation(loc[1], Path(loc[2]), mipMapLevel=mipMapLevel)


class Writer():
    def __init__(self, mode:str, defaultPrepension:Path) -> None:
        """
        Description:
            Sets up a module to write files in different console structures
        ---
        Arguments:
            - mode : String <>
                - build: writes files to the specific location
                - dump: dumps all files into typed folders
            - defaultPrepension : Path <>
                - A default path that will always be prepended to all writes
        """

        self.isDumpMode = (SpecialString("dump", "build").check(mode) == "dump")
        self.defaultPrepension = defaultPrepension

    def generatePath(self, location:_WriteLocation, currType:str) -> Path:
        """
        Description:
            generates a file path leading the specified location
        ---
        Arguments:
            - image : Image <>
            - location : WriteLocation <>
                - WiiULocation
                - ModPackLocation
            - currType : str <>
                - the current wiiu type
        ---
        Returns:
            - Path (not str), leading the correct location 
        """
        # builds a path 
        #   accounts for build/dump mode
        path = None
        testPath(self.defaultPrepension) # (handles exiting)
        if (self.isDumpMode == False): # not dump mode, merge both paths
            location.getPath().merge(self.defaultPrepension)
            # set path
            path = location.getPathAsPath()
        else: # is dump, just use prepension
            # set path
            path = Path(self.defaultPrepension.getPath(withFirstSlash=False), currType, location.getSaveName())
        return path

    def writeImage(self, image:Image, location:_WriteLocation, currType:str, doDelete:bool=False):
        """
        Description:
            Writes images to their specified location and handles all related errors
        ---
        Arguments:
            - image : Image <>
            - location : WriteLocation <>
                - WiiULocation
                - ModPackLocation
            - currType : str <>
                - the current wiiu type
            - doDelete : Boolean <False>
                - Whether to delete or write the files
        """

        # generate the path
        path = self.generatePath(location, currType)
        # formalize path into no-name and name version
        path.formalize()
        pathNoName = path.slice(0, (path.getLength() - 1)).getPath(withFirstSlash=False)
        path = f"{path.getPath(withFirstSlash=False)}.png"

        # make directories to write in (if needed (not existent))
        if (not os.path.isdir(pathNoName)): # checks if the path exists yet (if not)
            try:
                os.makedirs(pathNoName) # makes dirs if it doesn't exist
            except FileNotFoundError:
                Global.endProgram("could not write to the input path. Did you use a path that both exists and can be edited?")

        # save or delete the actual image
        if (doDelete == False): # save
            image.save(path, "PNG")
        else: # delete
            if (os.path.exists(path)): # check if exists before removing
                os.remove(path)
              