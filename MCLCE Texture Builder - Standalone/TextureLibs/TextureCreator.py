# previous "main" file for building the actual image systematically

# instructions for adding to the base libraries
    # null will create an issue and exit the program
    # true will mean an abstract or external is used
    # false will mean the old texture is used

from xLPyBasics.JsonAPI import JsonHandler

from CodeLibs import Logger as log
from CodeLibs.Logger import print
import CustomProcessing.Custom
from TextureLibs.SizingImage import SizingImage as Image
from builtins import type as typeof
import os
import shutil
import TextureLibs.SupportedTypes as SupportedTypes
import TextureLibs.Global as Global
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
import TextureLibs.SizingImage as si
from TextureLibs.ConsoleWriter import Writer, generateLocation
from CodeLibs.Path import Path
import CustomProcessing
import math

def getProcessingLengthDict(game):    
    print(f"process length", log.SECTION)

    length = {
        "cumulative": 0,
        "type": {}
    }
    for type in SupportedTypes.supportedTypes[game]:
        # add to length.type
        length["type"][type] = 0
        length["type"][f"{type}_abstract"] = 0

        # all of this code is for checking to make sure each part exists to begin with
        wiiuArr = rd.readWiiuLibFor(type, "Arr")
        wiiuAbstract = rd.readWiiuLibFor(type, "Abstract")
        
        if (wiiuArr != False):
            for value in wiiuArr:
                if value != None:
                    length["cumulative"] += 1
                    length["type"][type] += 1
        if (wiiuAbstract != False):
            for value in wiiuAbstract:
                if value != None:
                    length["cumulative"] += 1
                    length["type"][f"{type}_abstract"] += 1
    return length

_errorTxtPath = f"{Global.outputPath}\\errors.txt"
def _deleteIfErrorsTxtExists():
    if (os.path.exists(_errorTxtPath)):
        os.remove(_errorTxtPath)

_modPackName = None
if (Global.outputStructure == "modpack"): # only time modPackName will be used
    # gets the last bit of inputpath
    _modPackName = Path(Global.inputPath)
    _modPackName.formalize()
    _modPackName = _modPackName.getLast()
    # capitalization
    _modPackName = list(_modPackName) # convert to list (for 'char' reassingment)
    i = 0
    while i < len(_modPackName):
        if (i == 0): 
            _modPackName[0] = _modPackName[0].upper()
            i += 1
            continue
        if (_modPackName[i - 1] == " "):
            _modPackName[i] = _modPackName[i].upper()
        i += 1
    _modPackName = str.join("", _modPackName) # convert to string
            
writer = Writer(
        Global.outputDump,
        Path(Global.outputPath)
    )

# mipmap writes
def _writeMipMaps(image, type, wiiuLoc):
    # get wiiu type from type
    wiiuType = type
    if (type.endswith("s")): wiiuType = type[:-1] # if there's and s at the end, get rid of it

    # checks if there are errors and replace mode status to verify that mipmaps can be written or not
    writeMode = True # deafult: if there's errors or it's not replace mode
    if (Global.errorMode == "replace" or len(Global.notExpectedErrors) == 0): # if there's no errors or it's replace mode 
        writeMode = False

    # gets the multiplier as an incrementable power value
    multiplier = 0
    if (wiiuType == "block"):
        multiplier += 2 # makes sure to always give block 2 mipmaps
    if (wiiuType == "particle"):
        multiplier -= 1 # particles always get 1 less mipmap because they are smaller
    multiplier += math.log2(si.getMultiplier())# account for any sizing differences
    i = 1 # starts on one to make sure the original textures aren't re-written
    while i <= multiplier:
        # gets the denominator for division
        denominator = pow(2, i)

        # resize the image to the correct size
        imageCopy = image.resize((int(image.width / denominator), int(image.height / denominator)), doResize=False)

        # write a map
        writer.writeImage(
            imageCopy,
            generateLocation(Global.outputStructure, wiiuLoc, mipMapLevel=i+1, arg=_modPackName),
            type,
            doDelete=writeMode
        )

        # increment
        i += 1
    
    # deletes any extra existing mipMaps (that are larger from previous generations)
        # i starts where it left off
    while (i > multiplier) and (i <= 6):
        writer.writeImage(
            ut.blankImage(), # actual image doesn't matter
            generateLocation(Global.outputStructure, wiiuLoc, mipMapLevel=i+1, arg=_modPackName),
            type,
            doDelete=True
        )

        # increment
        i += 1

def translateForAllTypes():
    """
    Description:
        Runs the main algorithm to construct images
    ---
    Arguments:
        - debugMode : Boolean <False>
            - False: runs normally
            - True: allows the algorithm to continue even when custom functions return no image
    """
    # function variables
    anyTexturesFound = False

    # if storage_<loc> already exists, delete it
    storageLoc = None
    if (Global.outputDrive == "usb"): # if it's usb mode
        storageLoc = "s"
    elif (Global.outputDrive == "system"): # if it's sys mode
        storageLoc = "m"
    if (
        (storageLoc != None)
        and (os.path.isdir(Global.outputPath + "\\storage_" + storageLoc + "lc") == True)
    ): shutil.rmtree(Global.outputPath + "\\storage_" + storageLoc + "lc")

    _deleteIfErrorsTxtExists()
        
    # for the supported type of the selected game
    for type in SupportedTypes.supportedTypes[Global.inputGame]:
        print(f"{type} processing", log.SECTION)
        wiiuType = type
        if (type.endswith("s")): wiiuType = type[:-1] # if there's and s at the end, get rid of it

        # change the size of singular textures based on the type
        if (wiiuType == "particle"):
            ut.changeSingularSize(8)
        else:
            ut.changeSingularSize(16)

        # set base directory reads
        readFromBaseDirectory = False
        if (type == Global.misc):
            # there is no support for misc sheets or overrides because the idea of a misc sheet or override doesn't make any sense
            readFromBaseDirectory = True
        
        # type dependant variables
        wiiuArr = rd.readWiiuLibFor(wiiuType, "Arr")
        wiiuAbstract = rd.readWiiuLibFor(wiiuType, "Abstract")
        wiiuOverride = rd.readLinkLibFor(Global.inputGame, wiiuType + "_override")
        doOverride = False

        # --- WiiU Override ---
        if (wiiuOverride != False):
            # override doesn't support variable height via layer libraries

            print(f"library override reference found: {type}", log.LOG)
            print("checking for wiiu override texture...", log.LOG, 1)
            wiiuImage = rd.readWiiuImage(False, f"{Global.getLayerGame()}_{wiiuType}")

            overrideImage = Image.new("RGBA", ut.size(ut.singularSizeOnTexSheet), "#ffffff00") # scoping
            try:
                # override file name is based on the name in the lib for wiiuOverride
                # the wiiuName is the same file name value
                # type passed is the base type
                # no wiiu image is passed
                overrideImage = CustomProcessing.Custom.runFunctionFromPath("override", wiiuOverride, wiiuOverride, type, None)
                if (overrideImage != False):
                    anyTexturesFound = True
            except rd.notFoundException: # use wiiu image
                print(f"using wiiu texture for override: {wiiuOverride}", log.WARNING, 1)
                overrideImage = wiiuImage
            except rd.notx16Exception as err: # resize the image
                Global.incorrectSizeErrors.append(wiiuType)
                overrideImage = err.getImage().resize(wiiuImage.size, doResize=False)
                anyTexturesFound = True
            except rd.notExpectedException: # place error image
                Global.notExpectedErrors.append(wiiuType)
                overrideImage = Global.notFoundImage.resize(wiiuImage.size, doResize=False)
                anyTexturesFound = True

            if (overrideImage != False): # if an override will occur (do override, else just continue normally)
                print("override texture found, texture compensated", log.LOG, 1)
                doOverride = True

                # compensate for the missing textures from the override
                # save image
                wiiuLoc = rd.readWiiuLibFor(wiiuType, "Loc")
                writer.writeImage( # must write original texture here
                    overrideImage,
                    generateLocation(Global.outputStructure, wiiuLoc, arg=_modPackName),
                    type
                )
                # block mipmaps (probably useless code since block has no overrides)
                _writeMipMaps(overrideImage, type, wiiuLoc)
                
                Global.bar.step(Global.processingLength["type"][type]) # compensates the movement of the bar for this section
            else:
                print("no override texture found, continuing normally", log.LOG, 1)

        # --- WiiU Sheet ---
        if ((wiiuArr != False) and (doOverride != True)):
            # specific arr variables
            wiiuImage = rd.readWiiuImage(False, f"{Global.getLayerGame()}_{wiiuType}")
            linkArr = JsonHandler.read_for("\\linking_libraries\\Base_" + Global.inputGame, type)
            currPos = [0, 0]

            # constructed image and height
            layerLibHeight = rd.readLayerLib(wiiuType, Global.getLayerVersion(), isAbstract=False, extendingName="height")
            sheetHeight = ut.size(wiiuImage.width, si.convertInt(layerLibHeight)) if (layerLibHeight != None) else wiiuImage.size
            constructedImage = Image.new("RGBA", si.deconvertTuple(sheetHeight), "#ffffff00")

            def getWiiuImageForCurrTex(): # function that will get the current texture sheet position's texture 
                wiiuSheetLoc = (currPos[0], currPos[1], currPos[0] + ut.singularSizeOnTexSheet, currPos[1] + ut.singularSizeOnTexSheet)
                return wiiuImage.crop(wiiuSheetLoc, doResize=False)

            def cont(): # continues the sheet movement
                currPos[0] += ut.singularSizeOnTexSheet
                if (currPos[0] >= sheetHeight[0]): 
                    currPos[1] += ut.singularSizeOnTexSheet
                    currPos[0] = 0
                
            for currTex in wiiuArr: # for everything in wiiuSheet
                # wiiuLib checks
                if (currTex == None): # if the wiiulib has a none, just skip it
                    cont()
                    continue

                # translate 
                translatedTex = linkArr[currTex] # translate

                # try/except for throwing readErrors
                finalImage = None # scoping
                try: # run checks on translatedTex
                    if (translatedTex == True): # run an external function
                        finalImage = CustomProcessing.Custom.runFunctionFromPath("external", CustomProcessing.Custom.formatName(currTex), currTex, type, getWiiuImageForCurrTex())
                        if (currTex != "shine"): 
                            # shine is not allowed to contribute to the anyTexturesFound state because it must return a specially sized, external wiiuImage when it fails
                            anyTexturesFound = True
                    elif (translatedTex == False): # get wiiu texture
                        print(f"using wiiu texture: {currTex}", log.LOG)
                        finalImage = getWiiuImageForCurrTex()
                        # if wiiu texture is used, then any textures found is false
                    else: # normal, text
                        finalImage = rd.readImage(Global.inputPath + "\\" + type + "\\" + translatedTex, type, currTex, si.deconvertInt(ut.singularSizeOnTexSheet))
                        anyTexturesFound = True
                
                # run checks on finalImage
                except rd.notFoundException: # use wiiu image instead
                    print(f"using wiiu texture: {currTex}", log.WARNING)
                    finalImage = getWiiuImageForCurrTex()
                except rd.notx16Exception as err: # isn't to size, resize
                    # determine final image by getting the image that the program error'd on (err.getImage()) then,
                    finalImage = err.getImage().resize(si.deconvertTuple((ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet))) # resize the image as the correct size
                    Global.incorrectSizeErrors.append(currTex)
                    anyTexturesFound = True
                except rd.notExpectedException as err: # (only happens in error mode) place error texture
                    finalImage = Global.notFoundImage.resize(getWiiuImageForCurrTex().size, doResize=False)
                    Global.notExpectedErrors.append(currTex)
                    anyTexturesFound = True

                # finalize image and add to constructed image
                finalImage = finalImage.convert("RGBA")
                constructedImage.paste(finalImage, si.deconvertTuple((currPos[0], currPos[1])))

                # must be last
                cont()
                Global.bar.step() # step the bar

            # save image
            wiiuLoc = rd.readWiiuLibFor(wiiuType, "Loc")
            writer.writeImage( # must write original texture here
                constructedImage,
                generateLocation(Global.outputStructure, wiiuLoc, arg=_modPackName),
                type
            )
            # block mipmaps
            _writeMipMaps(constructedImage, type, wiiuLoc)

        # --- WiiU Abstract ---
        if (wiiuAbstract != False):
            # specific abstract variables
            linkAbstract = JsonHandler.read_for("\\linking_libraries\\Base_" + Global.inputGame, type + "_abstract")

            # for wiiu abstract lib
            for wiiuName in wiiuAbstract:
                # wiiuImage reads from the loc addon name to find the file
                wiiuImage = rd.readWiiuImage(True, f"{wiiuType}\\{ut.getWiiuNameFromAbstract(wiiuAbstract[wiiuName][2])}")
                wiiuLoc = wiiuAbstract[wiiuName]
                linkName = linkAbstract[wiiuName]

                # dump name handling (wiiuLoc length of 4)
                if (len(wiiuLoc) == 4): # use wiiu abstract file for custom name
                    wiiuImage = rd.readWiiuImage(True, Path(wiiuType, wiiuLoc[3]).getPath(withFirstSlash=False))
                    if (Global.outputDump == "dump"): # write into dump pack with custom name
                        path = Path(wiiuLoc[2])
                        path.formalize()
                        path.replaceAt((path.getLength() - 1), wiiuLoc[3])
                        wiiuLoc[2] = path.getPath(withFirstSlash=False)                    
                
                # try/except for throwing readErrors
                try: # run checks on linkLib
                    linkImage = None # scoping
                    if (linkName == True): # run abstract manageImgs
                        linkImage = CustomProcessing.Custom.runFunctionFromPath("abstract", CustomProcessing.Custom.formatName(wiiuName), wiiuName, type, wiiuImage)
                        anyTexturesFound = True
                    elif (linkName == False): # use wiiu texture
                        linkImage = wiiuImage
                        print(f"using wiiu texture: {wiiuName}", log.LOG)
                        # if wiiu texture is used, then any textures found is false
                    else:
                        path = None
                        if (readFromBaseDirectory == True): # base directory path
                            path = Global.inputPath + "\\" + linkName
                        else: # normal path
                            path = Global.inputPath + "\\" + type + "\\" + linkName
                        linkImage = rd.readImage(
                            path, 
                            type, 
                            wiiuName, 
                            si.deconvertInt(wiiuImage.height), 
                            si.deconvertInt(wiiuImage.width),
                            isAbstractRead=True)
                        anyTexturesFound = True

                # run checks errors on linkImage
                except rd.notFoundException: # use wiiu image instead
                    linkImage = wiiuImage
                    print(f"using wiiu texture: {wiiuName}", log.WARNING)
                except rd.notx16Exception as err:
                    # get the image and resize or crop
                    linkImage = err.getImage().resize(wiiuImage.size, doResize=False)
                except rd.notExpectedException as err: # place error texture (built)
                    size = wiiuImage.size
                    linkImage = Image.new("RGBA", size, "#00000000")
                    toleranceWidth = size[0] + int(size[0] / 8) # 1/8th margin of difference accounted for
                    if (size[1] > toleranceWidth): # if height is greater than width
                        linkImage = rd.duplicateImageDown(Global.notFoundImage.resize(ut.size(size[0], ut.singularSizeOnTexSheet), doResize=False), size[0], size[1])
                    elif (toleranceWidth < size[1]): # if width is greater than height
                        linkImage = rd.duplicateImageRight(Global.notFoundImage.resize(ut.size(ut.singularSizeOnTexSheet, size[1]), doResize=False), size[0], size[1])
                    else: # they are equal or within the tolerance range
                        linkImage = Global.notFoundImage.resize(size, doResize=False)
                    Global.notExpectedErrors.append(wiiuName)
                    anyTexturesFound = True

                # save
                linkImage = linkImage.convert("RGBA")
                writer.writeImage(
                    linkImage,
                    generateLocation(Global.outputStructure, wiiuLoc, arg=_modPackName),
                    type
                )
            
                Global.bar.step() # step the bar

        # write errors if they exist
        if (len(Global.notExpectedErrors) != 0) or (len(Global.incorrectSizeErrors) != 0):
            with open(_errorTxtPath, 'w') as writeFile: # write notExpectedErrors file
                if (Global.errorMode == "error"):
                    writeFile.write(
                        "The following textures were \"not found\" by the Texture Builder but still exist in this texture packs files and will need to be manually added to the image if you wish to use them in game\n" + 
                        "(don't like this output? change to replace mode)\n" + 
                        "\n- " + 
                        str.join("\n- ", Global.notExpectedErrors)
                    )
                elif (Global.errorMode == "replace"):
                    writeFile.write(
                        "The following textures were \"incorrectly sized\" in this texture pack but still exist in this texture packs files and will need to be manually added to the image if you wish to use them in game\n" + 
                        "(this is generated specifically for transparency in replace mode)\n" + 
                        "\n- " +
                        str.join("\n- ", Global.incorrectSizeErrors)
                    )
                
    # no found textures error
    if (anyTexturesFound == False):
        Global.stopGen("no textures could be found using this file directory\nIt *is* a valid directory, but no textures could be located inside of it")
    print("build completed successfully", log.NOTE)

def generateWiiuTextures():
    _deleteIfErrorsTxtExists()

    # runs for every type in terms of java
    for type in SupportedTypes.supportedTypes["java"]:
        print(type, log.SECTION)

        # variables 
        wiiuAbstract = rd.readWiiuLibFor(type, ["Abstract"])
        wiiuLoc = rd.readWiiuLibFor(type, ["Loc"])
        cropHeight = rd.readLayerLib(ut.wiiuType(type), Global.getLayerVersion(), isAbstract=False, extendingName="height")
        fullSheetHeight = None

        def croppedSheet(sheet:Image):
            if (cropHeight != None):
                sheet = sheet.crop((0, 0, si.deconvertInt(sheet.width), int((cropHeight / fullSheetHeight) * sheet.height)))
            return sheet
        # WiiU Arr (sheet) processing
        try:
            wiiuSheet = rd.readWiiuImage(False, f"{Global.getLayerGame()}_{type}")
            fullSheetHeight = wiiuSheet.height
            wiiuSheet = croppedSheet(wiiuSheet)
        except FileNotFoundError:
            # not found files are allowed for sheets
            print(f"{Global.getLayerGame()}_{type}: NOT found sheet", log.DEBUG, 1)
        else:
            print(f"{Global.getLayerGame()}_{type}: found sheet", log.DEBUG, 1)
            writer.writeImage( # write orignal
                wiiuSheet,
                generateLocation(Global.outputStructure, wiiuLoc, arg=_modPackName),
                type
            )

            # mipmap writing and generation
            # custom handling for block mipMaps since they can be copied instead of generated sometimes 
            if (type == "block") and (si.processingSize == 32): # shift mipmaps up (still use mipmap2)
                    writer.writeImage(
                        croppedSheet(
                            rd.readWiiuImage(f"{Global.getLayerGame()}_mipmaps", f"{Global.getLayerGame()}_{type}2")
                        ), 
                        generateLocation(Global.outputStructure, wiiuLoc, mipMapLevel=3, arg=_modPackName), 
                        type
                    )
                    writer.writeImage(
                        croppedSheet(
                            rd.readWiiuImage(f"{Global.getLayerGame()}_mipmaps", f"{Global.getLayerGame()}_{type}3")
                        ), 
                        generateLocation(Global.outputStructure, wiiuLoc, mipMapLevel=3, arg=_modPackName), 
                        type
                    )
                    writer.writeImage(
                        wiiuSheet.resize((int(wiiuSheet.width / 8), int(wiiuSheet.height / 8)), doResize=False), 
                        generateLocation(Global.outputStructure, wiiuLoc, mipMapLevel=4, arg=_modPackName), 
                        type
                    )
            elif (type == "block") and (si.processingSize == 16): # use original mipmaps
                    writer.writeImage(
                        croppedSheet(
                            rd.readWiiuImage(f"{Global.getLayerGame()}_mipmaps", f"{Global.getLayerGame()}_{type}2")
                        ), 
                        generateLocation(Global.outputStructure, wiiuLoc, mipMapLevel=2, arg=_modPackName), 
                        type
                    )
                    writer.writeImage(
                        croppedSheet(
                            rd.readWiiuImage(f"{Global.getLayerGame()}_mipmaps", f"{Global.getLayerGame()}_{type}3")
                        ), 
                        generateLocation(Global.outputStructure, wiiuLoc, mipMapLevel=3, arg=_modPackName), 
                        type
                    )
            else: # generate mipmaps
                _writeMipMaps(wiiuSheet, type, wiiuLoc)

            Global.bar.step(Global.processingLength["type"][type]) # compensates the movement of the bar for this section

        # WiiU Abstract processing
        for wiiuName in wiiuAbstract:
            currLoc = wiiuAbstract[wiiuName]

            # dump name handling (wiiuLoc length of 4)
            if isinstance(currLoc, list) and (len(currLoc) == 4): # use wiiu abstract file for custom name
                wiiuImage = rd.readWiiuImage(True, Path(type, currLoc[3]).getPath(withFirstSlash=False))
                if (Global.outputDump == "dump"): # write into dump pack with custom name
                    path = Path(currLoc[2])
                    path.formalize()
                    path.replaceAt((path.getLength() - 1), currLoc[3])
                    currLoc[2] = path.getPath(withFirstSlash=False)

            try:
                wiiuImage = rd.readWiiuImage(True, f"{type}\\{ut.getWiiuNameFromAbstract(currLoc[2])}")
            except FileNotFoundError:
                print(f"Error for texture: {wiiuName}", log.EXIT)
                Global.stopGen("A core program file could not be found or read correctly.\nPlease contact support")
            else:
                print(f"{wiiuName}: found abstract", log.DEBUG, 1)
                writer.writeImage(
                    wiiuImage,
                    generateLocation(type=Global.outputStructure, loc=currLoc, arg=_modPackName),
                    type
                    )
                Global.bar.step()
    print("build completed successfully", log.NOTE)
