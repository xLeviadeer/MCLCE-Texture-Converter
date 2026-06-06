from builtins import type as typeof
from CodeLibs import Logger as log
from CodeLibs.Logger import print
import TextureLibs.TextureUtility as ut
import TextureLibs.Global as Global
from CodeLibs import Logger as log
from CodeLibs import JsonHandler
from CodeLibs.Path import Path
from CustomProcessing.Custom import runFunctionFromPath
from CustomProcessing.Custom import formatName
from TextureLibs.SupportedTypes import supportedTypes
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.SizingImage as si
from PIL import Image as Sampling
import math
from copy import deepcopy
 
# --- read errors ---

class notFoundException(Exception):
    pass

class notx16Exception(Exception):
    def __init__(self, message="", image=None):
        self.image = image

        super().__init__(message)

    def getImage(self) -> Image:
        return self.image

class notExpectedException(Exception):
    def __init__(self, *args: object, size = None):
        super().__init__(*args)

        if (size == None): # default position
            self.size = (ut.singularSizeOnTexSheet,) * 2
        elif (typeof(size) is not tuple) or (len(size) != 2): # custom size error checking
            print(f"invalid syntax for position argument: {size} when position requires a tuple of length 2", log.EXIT)
            Global.bar.close()
        else: # custom size
            self.size = size
    
    def getSize(self):
        return self.size

# --- read functions ---

def patchForVersion(path, type, wiiuName, doCustomProcessing:bool=True): # does everything version_patches, no other version patches
    if (wiiuName == False or wiiuName == None): return path # nothing can be done if the wiiuName isn't passed, cannot read library
    if (type == None): return path

    variablePath = path
    # set variable path (to just path or a version patch)
    if (Global.inputVersion == None): # if the version doesn't exist
        print("attempting to run version patches but no version has been set", log.EXIT)
        Global.bar.close()
    
    # try to read the version patches
    versionPatches = None
    try:
        versionPatches = JsonHandler.readFor("\\linking_libraries\\version_patches_" + Global.inputGame, ["versions", Global.inputVersion, type])
    except:
        # this can occur if the version patch (section, not just one) that's being read for doesn't exist. In this case, the program should continue to run
        # this also always occurs for bedrock since there is no version in bedrock
        return path # skips version patch

    # if the current texture (name) is in the version patches 
    if (wiiuName in versionPatches):
        patchName = versionPatches[wiiuName] # get patchName

        # check to see if any custom processing should be done
        if (patchName == True): # if the version patch needs custom processing
            if (doCustomProcessing == False): return None # does nothing but return none as a signal it didn't work
            print(f"found version patch for {wiiuName} regarding {Global.inputVersion}", log.PATCHFUNCTION)
            # passes no wiiu image
            returnImage = runFunctionFromPath("versional", formatName(wiiuName), wiiuName, type[:-9], None) # [:-9] removes the word "abstract"
            if (returnImage == None): # if there is no function found
                print(f"(could not find) or (error while processing) patch function for \"{wiiuName}\" regarding {Global.inputVersion}", log.EXIT)
                Global.bar.close()
            print(f"found patch function for \"{wiiuName}\" and ran", log.PATCHFUNCTION, 1)
            return returnImage
        elif ((patchName == False) or (patchName == None)): # if version patch doesn't follow correct format
            print(f"invalid version patch formatting for \"{wiiuName}\" regarding {Global.inputVersion}", log.EXIT)
            Global.bar.close()

        # find prepending path section
        abstractKeyword = "_abstract"
        typeNoAbstract = ut.wiiuType(type if (not type.endswith(abstractKeyword)) else type[:-len(abstractKeyword)])
        prependingPath = Path(
            Global.inputPath, 
            typeNoAbstract if (typeNoAbstract != "misc") else None, 
            isRootDirectory=True
        )

        # combine path
        variablePath = f"{prependingPath.getPath()}\\{patchName}"
        print(f"found version patch for {wiiuName}", log.PATCHFUNCTION)
    # always return
    return variablePath

def getImage(path):
    # check if it can be found
    try: # try to read as png
        specificVariablePath = path
        if (not specificVariablePath.endswith(".png")): specificVariablePath += ".png"
        return Image.open(specificVariablePath)
    except:
        try: # try to read as tga
            specificVariablePath = path
            if (not specificVariablePath.endswith(".tga")): specificVariablePath += ".tga"
            return Image.open(specificVariablePath)
        except: # could not find, raise notFound
            raise notFoundException

def readImage(path, type, wiiuName, expectedHeight, expectedWidth=None, isAbstractRead=False):
    # base handling of ALL image reads has been transferred to this function universally

    patchType = type if (isAbstractRead == False) else f"{type}_abstract"
    variablePath = patchForVersion(path, patchType, wiiuName)
    if (typeof(variablePath) is not str): # if the return of patchForVersion is an image
        # UNSTABLE check for type, simply checks if it's not a str
        return variablePath
    image = getImage(variablePath)

    # multiplier physics & set sizes as they should be (for not expected errors)
    deconSizeOnSheet = si.deconvertInt(ut.singularSizeOnTexSheet)
    baseSize = si.baseSize if (deconSizeOnSheet >= 16) else deconSizeOnSheet
    returnSize = ((expectedWidth if (expectedWidth != None) else baseSize), expectedHeight) # happens before conversion
    returnHeight = si.convertInt(expectedHeight)
    returnWidth = si.convertInt(expectedWidth) if (expectedWidth != None) else ut.singularSizeOnTexSheet # 16

    # check width
    if (image.width != returnWidth): # width not right
        if (Global.errorMode == "error"): raise notExpectedException(size=(returnSize))
        if (Global.errorMode == "replace"):
            def resizeInContextToWidth(image):
                return image.resize((returnWidth, int(image.height * (returnWidth / image.width))), doResize=False)
            def newSize(image): # resizes a texture upwards if needed
                if (si.resizingNeeded() == False): return image # if resizing isn't needed

                i = 1
                while i <= math.log2(si.getMultiplier()):
                    if ((image.width * pow(2, i)) == returnWidth): # image width is just wrong (this check will always be false with a processing size of 16)
                        # resize the image to be the intended width
                        return resizeInContextToWidth(image)
                    i += 1
                raise notx16Exception(image=image) # not found
            image = newSize(image) # accounts for up-conversion
            if (returnWidth < image.width): # cannot be smaller if newSize was successful in resizing. Accounts for down-conversion
                image = resizeInContextToWidth(image)

    # the width must be correct at this point since there were no errors

    # check height
    if (image.height != returnHeight): # height not right
        if (Global.errorMode == "replace"): 
            if (image.height < returnHeight): # if (actual image) is smaller (than wiiu), than duplicate up
                return duplicateImageDown(image, returnWidth, returnHeight)
            elif (image.height > returnHeight): # if (actual image) is larger (than wiiu), then crop down
                return image.crop((0, 0, image.width, returnHeight), doResize=False) # crop to make sure it fits
        if (Global.errorMode == "error"): raise notExpectedException(size=(returnSize))
    
    return image # no errors found, return normally

def duplicateImageDown(startImage, expectedWidth, expectedHeight):
    image = Image.new("RGBA", (expectedWidth, expectedHeight), "#ffffff00", doResize=False) # emtpy image
                
    # go down the image, duplicating
    currPos = 0
    while (currPos < expectedHeight):
        image.paste(startImage, (0, currPos), doResize=False)

        currPos += startImage.height # iterate down
    return image

def duplicateImageRight(startImage, expectedWidth, expectedHeight):
    image = ut.blankImage(ut.size(expectedWidth, expectedHeight), doResize=False)
    
    # go to the right duplicating
    currPos = 0
    while (currPos < expectedWidth):
        image.paste(startImage, (currPos, 0), doResize=False)

        currPos += startImage.width
    return image

def readLayerLib(wiiuType:str, layerVersion:str, isAbstract:bool, extendingName:str):
    """Reads a specific portion of a layer library

    Args:
        wiiuType (str): the wiiu type
        layerVersion (str): the version of layer library to read (1.12 or 1.14)
        isAbstract (bool): determines whether to read an asbtract portion or not
        extendingName (str): what name to look for at the end of the key

    Returns:
        dict: the library or None if the library couldn't be read
    """

    # return None if layerVersion is None
    if (layerVersion == None): return None

    # try to read the removal layer (sheet)
    try:
        lib = JsonHandler.readFor(
            Path(
                "linking_libraries", 
                f"layer_{layerVersion}"
            ),
            f"{wiiuType}{"_abstract" if (isAbstract == True) else ""}_{extendingName}"
        )

        # do some type checking
        if (isAbstract == True):
            if (extendingName == "remove") and (not isinstance(lib, list)):
                Global.endProgram("abstract removals must be of format list")
            elif (extendingName == "add") and (not isinstance(lib, dict)):
                Global.endProgram("abstract additions must be of format dict")
            elif (extendingName == "replace") and (not isinstance(lib, dict)):
                if any(not isinstance(value, dict) for value in lib.values()):
                    Global.endProgram("abstract replacements must be of format dict with dictionaries as values")
        else: # not abstract
            if (extendingName == "height") and (not isinstance(lib, int)):
                Global.endProgram("height overrides must be of format int")
            elif (extendingName in ("add", "remove"))  and (not isinstance(lib, list)):
                Global.endProgram("regular removals or additions must be of format list")
            elif (extendingName == "replace") and (not isinstance(lib, dict)):
                Global.endProgram("abstract replacements must be of format dict")

        # return
        return lib
    except KeyError:
        print(f"could not find {"REG" if (isAbstract == False) else "ABSTRACT"} {extendingName.upper()} layer library associated with {layerVersion} aka {Global.outputStructure} of type {wiiuType}", log.DEBUG)
        return None

def readWiiuLibFor(type, travel):
    class wrapper:
        # scoping for wiiuLib
        wiiuLib = None

        def getWiiuLibFromWrapper(self, type, travel):
            # old method
            self.wiiuLib = False
            if (type.endswith("s")): type = type[:-1] # if there's and s at the end, get rid of it
            try:
                # extends the wiiu lib should never be read not the wiiu lib
                self.wiiuLib = JsonHandler.readFor(f"\\linking_libraries\\wiiu_" + type, deepcopy(travel))
            except Exception as err:
                print(f"{type}: could not read wiiu -> {travel}", log.DEBUG)

            # -- handle laying before returning --
            
            # get the layer version from the output structure
            layerVersion = Global.getLayerVersion()

            # deslist for checking
            if isinstance(travel, list) and (len(travel) > 0): travel = travel[0]

            # only run layering if it's not 1.13 and was found AND if it's a valid travel type
            if (
                (layerVersion != None) 
                and (self.wiiuLib != False)
                and (
                    (travel == "Abstract") 
                    or (travel == "Arr")
                )
            ):
                # library add/subtract function
                def modifyLib(lib, isAbstract, mode:str):

                    # is list check
                    isList = isinstance(lib, list)

                    # new list (if remove then empty, if add then copy of lib)
                    newLib = ([] if (isAbstract == False) else {}) if (mode == "remove") else deepcopy(self.wiiuLib)

                    # check str/int
                    def isNumber(maybeNumber):
                        return (isinstance(maybeNumber, int) or (isinstance(maybeNumber, str) and maybeNumber.isdigit()))

                    # function for adding to new lib
                    def addToNewLib(name, value=None, oldName=None):
                        # add to newLib
                        if (isAbstract == False): # list
                            if (oldName != None): # triggers replace mode
                                # find index placement
                                if isNumber(oldName): # if old name is a number
                                    index = int(oldName)
                                else: # not a number
                                    index = newLib.index(oldName) # find index from name
                                # remove/insert
                                newLib.pop(index)
                                newLib.insert(index, name)
                                return
                            else: newLib.append(name) # add
                        else: # assumes dict
                            if (oldName != None): # triggers replace mode
                                # no number processing since dictionaries are (treated as) undordered in this case
                                del newLib[oldName] # remove
                            newLib[name] = (self.wiiuLib[name] if (value == None) else value) # if value is none, default to wiiu lib value

                    # get list of names from either list or dict
                    listOfNames = lib if (isList == True) else lib.keys()

                    # remove mode
                    if (mode == "remove"):
                        # loop through the wiiu lib
                        for wiiuName in self.wiiuLib:
                            if (wiiuName not in listOfNames): # if it's NOT in the names list
                                addToNewLib(wiiuName) # add to newLib
                            elif (isAbstract == False): # pad Nones/nulls into lists
                                addToNewLib(None)
                    # add mode
                    elif (mode == "add"):
                        # loop through the list of names
                        for currName in listOfNames:
                            # check if the key is in the wiiu lib already
                            if (currName in self.wiiuLib):
                                Global.endProgram(f"layering key, '{currName}', could not be added because it's already a key in the {Global.outputStructure}_{type} -> {travel} lib")
                            # not already in lib
                            else: 
                                addToNewLib(
                                    currName,
                                    (lib[currName] if (isAbstract == True) else None)
                                    )
                    elif (mode == "replace"):
                        # loop through the list of names
                        for currName in listOfNames:
                            # check if the key is in the wiiu lib already
                            if isNumber(currName):
                                if not (0 < int(currName) < len(self.wiiuLib)):
                                    Global.endProgram(f"layering key, '{currName}', could not be replaced because the index is out of range in the {Global.outputStructure}_{type} -> {travel} lib")
                            elif isinstance(currName, str):
                                if (currName not in self.wiiuLib):
                                    Global.endProgram(f"layering key, '{currName}', could not be replaced because it's not a key in the {Global.outputStructure}_{type} -> {travel} lib")
                            
                            # get values from list or dict
                            newName = (lib[currName] if (isAbstract == False) else lib[currName]["name"])
                            newValue = (None if (isAbstract == False) else lib[currName]["value"])

                            # add
                            addToNewLib(newName, newValue, currName)
                    
                    # set wiiuLib to the new lib
                    self.wiiuLib = newLib

                # - modify libs if the associated layerLib exists exists -

                # determine abstract status
                isAbstract = (travel == "Abstract")
                wiiuType = ut.wiiuType(type)

                # for add and remove
                for mode in ("remove", "add", "replace"):
                    # read
                    layerLib = readLayerLib(wiiuType, layerVersion, isAbstract, mode)

                    # modify if it exists
                    if (layerLib != None):
                        modifyLib(layerLib, isAbstract, mode)
            # return from wrapper
            return self.wiiuLib

    # return
    return wrapper().getWiiuLibFromWrapper(type, travel)

def readLinkLibFor(game, travel):
    content = False
    try:
        content = JsonHandler.readFor("\\linking_libraries\\base_" + game, travel)
    except Exception as e:
        print(f"{game}: could not read wiiu -> {travel}", log.DEBUG)
    return content

def readImageSingular(wiiuName, pathExtension, type, expectedSize, doVersionPatches=True, doPrint=False, dox16Handling=True):
        """
        Description: 
            Runs modified handling over readImage()
        ---
        Arguments:
            - wiiuName : String <>
            - pathExtension : String <>
                - Path string that extends onto <type>
            - type : String <>
            - expectedSize : Tuple <>
                - Tuple with length of 2
            - doVersionPatches : Boolean <True>
                - Determines whether version patches should be done
            - doPrint : Boolean <False>
                - Debug variable for printing the full path
        ---
        Returns:
            - Image
        ---
        Other:
            - automatically handles x16 errors
            - lets pass notFound and notExpected errors
                - these errors should either be handled or let pass
                - if errors are passed, then the entire custom-function will fail and either result in the notFound Image or the WiiU Image
        """

        # printing
        if (doPrint == True):
            print(f"{Global.inputPath}\\{type}\\{pathExtension}<.png/.tga>", log.NOTE)

        # ignores version patches
        inputName = wiiuName
        if (doVersionPatches == False):
            inputName = None

        # read image and handle x16 errors
        image = ut.blankImage(si.convertTuple(expectedSize))
        try:
            image = readImage(f"{Global.inputPath}\\{type}\\{pathExtension}", type, inputName, expectedSize[1], expectedSize[0])
        # lets notFound exception pass
        except notx16Exception as err:
            if (dox16Handling == False):
                raise notx16Exception(image=err.getImage())
            Global.incorrectSizeErrors.append(wiiuName)
            image = err.getImage().resize(expectedSize)
        # lets notExpected exception pass
        return image

def readMulticolorGrayscale(wiiuName, type, assign, names, namePath, whitePath, expectedSize, doPrint=False):
    """
    Description:
        Reads varients of an image with multiple colors, prioritizing white. Grayscale handling is left to the user.
    ---
    Arguments:
        - wiiuName : String <>
        - type : String <>
        - assign : Function <>
            - Description:
                - Processing method for images before returning
            - Arguments
                - : Image
                - : Boolean
                    - Determines whether the image should be brightened or not
            - Returns:
                - : Image
        - names : List <>
            - A list of names that can be extended to find colored textures
            - Names farther in the list have higher "prority" for use
        - namePath : String <>
            - A path to subtend names. This path already includes the input path and the type
        - whitePath : String<>
            - A path to the white priority image. This path already includes the input path and the type
        - expectedSize : Tuple <>
            - A size to use when creating and reading images
    ---
    Returns:
        - Image
    """
    finalImage = ut.blankImage(expectedSize)
    whiteFound = True # white was found

    try: # try to read the white image first and use that
        print("------ White ------") if doPrint == True else None 
        finalImage = readImageSingular(wiiuName, Path(whitePath).getPath(withFirstSlash=False), type, expectedSize, doPrint=doPrint)
    except notFoundException:
        print("------ Colors ------") if doPrint == True else None
        # run each shulker in terms of priority until one is found that can be used
        whiteFound = False

        noneFound = True
        foundNotExpectedOnly = False
        for name in names[::-1]: # in reverse order
            try:
                finalImage = readImageSingular(wiiuName, Path(f"{namePath}{name}").getPath(withFirstSlash=False), type, expectedSize, doPrint=doPrint)
                noneFound = False
                foundNotExpectedOnly = False
                break
            except notFoundException:
                pass
            except notExpectedException:
                foundNotExpectedOnly = True

        # if only an error image was found
        if (foundNotExpectedOnly):
            finalImage = Global.notFoundImage.resize(finalImage.size)

        # if nothing was found
        if (noneFound):
            raise notFoundException # uses wiiu texture

    finalImage = assign(finalImage, (not whiteFound)) # enhance brightness if white wasn't found
    return finalImage

def readWiiuImage(inWiiuAbstract, name, doResize=True):
    name = f"{name}.png" if (not name.endswith(".png")) else name
    addition = None
    match (inWiiuAbstract):
        case True: 
            if (Global.getLayerVersion() == "1.14"): addition = "ps4_abstract"
            else: addition = "wiiu_abstract"
        case False: addition = None # exists just so what happens is obvious
        case _:
            addition = inWiiuAbstract
    image = Image.open(Path(Global.getMainWorkingLoc(), "base_textures", addition, name).getPath(withFirstSlash=False))
    
    # multiplier physics
    if (doResize == True):
        image = image.resize(image.size, Sampling.NEAREST) # multiplier is automatic

    return image
