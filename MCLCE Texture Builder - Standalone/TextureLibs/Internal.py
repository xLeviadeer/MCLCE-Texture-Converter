# library of building functions for back-end libraries

from TextureLibs.SizingImage import SizingImage as Image
import os
import shutil
import subprocess
from CodeLibs import JsonHandler
import TextureLibs.Global as Global
import TextureLibs.SupportedTypes as SupportedTypes
from zipfile import ZipFile
from TextureLibs.TextureUtility import singularSizeOnTexSheet
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from CustomProcessing.Custom import runFunctionFromPath
from CodeLibs.Path import Path
from builtins import type as typeof
from CodeLibs.ConsoleWriter import Writer
from CodeLibs.ConsoleWriter import WiiULocation

# moves assets to the frontend
def moveAssets(set):
    """
    Important:
        This function must be executed from within (cd'd in) the "Standalone" folder
    """

    builderPath = Global.getMainWorkingLoc() + "\\python_builder"

    # wipe everything in python_builder first
    if (os.path.isdir(builderPath) == True):
        shutil.rmtree(builderPath)
    os.mkdir(builderPath)

    # find needed version and write them
    print("finding needed versions")
    print(findNeededVersions("java"))
    JsonHandler.writeAll("\\global\\input_versions_java", findNeededVersions("java"))
    JsonHandler.writeAll("\\global\\input_versions_bedrock", findNeededVersions("bedrock"))
    print("completed; wrote needed versions")

    # --- CMD Compile Section ---

    mainFolder = "CustomProcessing"

    # set the intial command
    command = ["python", "-m", "PyInstaller", "--onedir"]
    
    # for every type, game, and file name
    for type in ["External", "Abstract", "Versional", "Override"]:
        for game in ["java", "bedrock"]:
            currDir = [mainFolder, type, game]
            for file in os.scandir(Path(Global.getMainWorkingLoc(), currDir, isRootDirectory=True).getPath()):
                if (not file.name.endswith(".py")): continue # file must end with .py
                command.extend([f"--hidden-import={".".join(currDir + [file.name])[:-3]}"]) # adds hidden import where it's a cumulative of type, game and file name with .py removed

    # for every shared file name
    for file in os.scandir(Path(Global.getMainWorkingLoc(), mainFolder, isRootDirectory=True).getPath()):
        if (not file.name.endswith(".py")): continue # file must end with .py
        command.extend([f"--hidden-import={mainFolder}.{file.name[:-3]}"]) # adds the file name with .py removed

    # adds the input location
    command.extend([f"{Global.getMainWorkingLoc()}\\Entry_Program.py"])

    # print command for testing and run
    print(command)
    subprocess.run(command) # may need to edit drive letter depending on system

    # --- Copying & Deletion Section ---

    # list of assets to move and how
        # true is a dir
        # false is a file
    assets = {
        "base_textures\\wiiu_abstract": True,
        "base_textures\\wiiu_mipmaps": True,
        "base_textures\\ps4_abstract": True,
        "base_textures\\ps4_mipmaps": True,
        "base_textures\\notFound.png": False,
        "base_textures\\error.png": False,
        "base_textures\\drop_samples.png": False,
        "linking_libraries\\Base_java.json": False,
        "linking_libraries\\Base_bedrock.json": False,
        "linking_libraries\\version_patches_java.json": False,
        "linking_libraries\\version_patches_bedrock.json": False,
        "linking_libraries\\layer_1.12.json": False,
        "linking_libraries\\layer_1.14.json": False,
        "resources\\Re.ico": False,
        "global": True
    }

    # get supportedTypes dependant files
    for game in ("wiiu", "ps4"):
        for type in SupportedTypes.supportedTypes["java"]:
            # if respective json/png files exist, copy them
            pngPath = f"base_textures\\{game}_" + type + ".png"
            jsonPath = f"linking_libraries\\{game}_" + type + ".json"
            if (os.path.exists(Global.getMainWorkingLoc() + "\\" + pngPath)):
                assets[pngPath] = False
            if (os.path.exists(Global.getMainWorkingLoc() + "\\" + jsonPath)):
                assets[jsonPath] = False

    # for through list
    for asset in assets:
        if (assets[asset] == False): # if file
            assetPathNoName = str.join("\\", str.split(asset, "\\")[:-1]) # find the asset's path without a name
            if (os.path.isdir(builderPath + "\\" + assetPathNoName) == False): # if the path without name doesn't exist, then make it
                os.makedirs(builderPath + "\\" + assetPathNoName)
            shutil.copy(Global.getMainWorkingLoc() + "\\" + asset, builderPath + "\\" + asset)
        elif (assets[asset] == True): # if dir
            shutil.copytree(Global.getMainWorkingLoc() + "\\" + asset, builderPath + "\\" + asset)
        print("--copied: " + asset)

    # delete and move stuff
    buildPath = Global.getMainWorkingLoc() + "\\build"
    if os.path.exists(buildPath): shutil.rmtree(buildPath)
    specPath = Global.getMainWorkingLoc() + "\\Entry_Program.spec"
    if os.path.exists(specPath): os.remove(specPath)
    internalPath = Global.getMainWorkingLoc() + "\\dist\\Entry_Program\\_internal"
    if os.path.exists(internalPath): shutil.move(internalPath, builderPath)
    programPath = Global.getMainWorkingLoc() + "\\dist\\Entry_Program\\Entry_Program.exe"
    if os.path.exists(programPath): shutil.move(programPath, builderPath)
    distPath = Global.getMainWorkingLoc() + "\\dist"
    if os.path.exists(distPath): shutil.rmtree(distPath)

    # copy to a specific location?
    location = f"{Global.getMainWorkingLoc()[0]}:\\Coding\\B- LeRe\\MCWiiU-Texture-Builder\\MCWiiU Texture Builder - Frontend\\bin\\" + set + "\\net8.0-windows"
    print("--removing: old python_builder")
    if (os.path.isdir(location + "\\python_builder") == True):
        shutil.rmtree(location + "\\python_builder")
    print("--copying: new python_builder")
    shutil.copytree(Global.getMainWorkingLoc() + "\\python_builder", location + "\\python_builder")

# export wiiu sheet as singular images
def separateWiiuSheet(type):
    Global.outputPath = Global.getMainWorkingLoc() + "\\output" # path
    
    # change the size of singular textures based on the type
    if (type == "particle"):
        singularTexSizeOnSheet = 8
    else:
        singularTexSizeOnSheet = 16

    wiiuSheet = JsonHandler.readFor("\\linking_libraries\\wiiu_" + type, "Arr")
    wiiuImage = Image.open(Global.getMainWorkingLoc() + "\\base_textures\\wiiu_" + type + ".png")
    currPos = [0, 0]
    number = [1]

    # loop section
    def cont():
        currPos[0] += singularTexSizeOnSheet
        if (currPos[0] >= wiiuImage.size[0]): currPos[1] += singularTexSizeOnSheet; currPos[0] = 0
        number[0] += 1

    for currTex in wiiuSheet: # for everything in wiiuSheet
        if (currTex == None): # if the wiiulib has a none, just skip it
            print("WAS NONE")
            cont()
            continue
        print(str(currTex) + " " + str(currPos))

        # crop and save
        cropImage = wiiuImage.crop((currPos[0], currPos[1], currPos[0] + singularTexSizeOnSheet, currPos[1] + singularTexSizeOnSheet))
        cropImage.save(Global.outputPath + "\\" + str(number[0]) + " " + currTex + ".png")

        # must be last
        cont()

# check the existence of abstract textures of a type
def checkAbstractTextures(type):
    wiiuLib = JsonHandler.readFor("\\linking_libraries\\wiiu_" + type, "Abstract")
    dirLib = os.listdir(Global.getMainWorkingLoc() + "\\base_textures\\wiiu_abstract")

    notFound = []
    for currKey in wiiuLib:
        found = False
        for currDir in dirLib:
            if (currKey == (currDir if (not currDir.endswith(".png")) else currDir[:-4])):
                found = True
        if (not found):
            notFound.append(f"{currKey}") # didn't find
    
    if (len(notFound) == 0):
        print("---all textures were found")
    else:
        print(f"---the following textures weren't found: \n{notFound}")

# finds the needed versions for the frontend (versions with changes)
def findNeededVersions(game):
    # read version patches
    if not (os.path.isfile(Global.getMainWorkingLoc() + "\\linking_libraries\\version_patches_" + game + ".json")):
        Global.endProgram(f"version patches don't exist (for {game}), cannot run findNeededVersions")
    versionPatches = JsonHandler.readFor("\\linking_libraries\\version_patches_" + game, ["versions"])
    # sort version patches
    versionPatches = dict(sorted(versionPatches.items(), key=lambda item: [int(x) for x in item[0].split('.')]))
    neededVersions = [ # starts with min version
        ".".join( # join together with .
            [str(num) for num in SupportedTypes.supportedVersions[game]["min"]] # cast nums to string
        )
    ] 

    previousData = None
    # for every version
    for version, data in versionPatches.items():
        if (previousData == None) or (previousData != data):
            neededVersions.append(version)
        previousData = data

    return neededVersions

# generate the version patches file
    # version patches only check for changes based on the file name; use equality checks for texture based differences
def generateVersionPatches():
    versionPatches = {}
    differences = {}
    prexistingVersionPatches = None
    if (os.path.isfile(Global.getMainWorkingLoc() + "\\linking_libraries\\version_patches_" + Global.inputGame + ".json")):
        prexistingVersionPatches = JsonHandler.readFor("\\linking_libraries\\version_patches_" + Global.inputGame, ["versions"])

    # for every version
    path = Global.getMainWorkingLoc() + "\\base_textures"
    processingLength = len(list(filter(lambda file : file.endswith(f"_{Global.inputGame}"), os.listdir(path))))
    count = 0
    for dir in os.scandir(path): # for every version (with the if) [versions]
        if ((not os.path.isdir(path + "\\" + dir.name)) or (not dir.name.endswith(Global.inputGame))): continue # must end with link name and be directory to continue
        currVersion = None
        if (Global.inputGame == "java"):
            currVersion = dir.name[:-5]
            if (int(currVersion.split(".")[1]) == 13):
                continue
        elif (Global.inputGame == "bedrock"):
            currVersion = dir.name[:-8]
        print(f"({count}/{processingLength}) running version {dir.name}")

        for type in SupportedTypes.supportedTypes[Global.inputGame]: # [version > types]
            print(f"-running type: {type}")

            # type specific variables
            typeAbstract = type + "_abstract"
            linkArr = rd.readLinkLibFor(Global.inputGame, type)
            linkAbstract = rd.readLinkLibFor(Global.inputGame, typeAbstract)

            # function to find differences (functionized to save space in file)
            def addMissingToVersionPatches(arr, arrType):
                for wiiuTex in arr: # for every texture file in the current type [version > type > texture names]
                    linkTex = arr[wiiuTex]
                    if (linkTex == True or linkTex == False): continue # has to be string
                    
                    def checkDirectory(currPath, additionalDir = None):
                        path = currPath if (additionalDir == None) else (f"{currPath}\\{additionalDir}") # creates a temporary path value for checking this directory (without actually combining values)
                        for file in os.scandir(path): # [version > type > file names] (and subdirectories)
                            namePath = file.name if (additionalDir == None) else f"{additionalDir}\\{file.name}"
                            if (os.path.isdir(f"{path}\\{file.name}")): # check if the file is a directory
                                if (checkDirectory(currPath, namePath)): # add to additionalDir and recurse (returns true if checkDirectory returns true, if false, do nothing)
                                    return True
                            elif ((namePath == linkTex + ".png") or (namePath == linkTex + ".tga")):
                                return True
                        if (additionalDir == None): # this check ensures that false is only returned once the top-level directory has been completed and not subdirectories
                            return False

                    # if it doesn't exist, then add it to version patches
                    found = checkDirectory((path + "\\" + dir.name + (f"\\{type}" if (type != Global.misc) else "")))
                    if (found == False):
                        addition = None

                        # if it already exists, use the existing value
                        if (prexistingVersionPatches != None): # make sure the version patch exists in the first place
                            if (currVersion in prexistingVersionPatches):
                                if (arrType in prexistingVersionPatches[currVersion]):
                                    if (wiiuTex in prexistingVersionPatches[currVersion][arrType]):
                                        addition = prexistingVersionPatches[currVersion][arrType][wiiuTex]

                        if (addition == None): # if addition couldn't be found
                            print(f"--NEW couldn't find: {linkTex}")
                            # add wiiuName and version to the differences dict
                            if (wiiuTex not in differences): # doesn't exist yet, add
                                differences[wiiuTex] = currVersion
                            else: # exists, check earlier version
                                if ut.compareVersions(currVersion, differences[wiiuTex], direction=True):
                                    differences[wiiuTex] = currVersion

                        # checks for creating version patches sections originally
                        if (currVersion not in versionPatches): 
                            versionPatches[currVersion] = {}
                        if (arrType not in versionPatches[currVersion]):
                            versionPatches[currVersion][arrType] = {}

                        # add to versionPatches
                        versionPatches[currVersion][arrType][wiiuTex] = addition

            # if arr exists
            if (linkArr != False):
                addMissingToVersionPatches(linkArr, type)
                
            # if abstract exists
            if (linkAbstract != False):
                addMissingToVersionPatches(linkAbstract, typeAbstract)
        count += 1

    # save
    JsonHandler.writeAll("\\linking_libraries\\version_patches_" + Global.inputGame, {"versions": versionPatches})
    JsonHandler.writeAll("\\linking_libraries\\new_patches_" + Global.inputGame, differences)

# add to the version patches
def addToVersionPatches(typeSpace, key, value, majorUpdate, minorVersion=None, direction=True):    
    prexistingVersionPatches = None
    if (os.path.isfile(Global.getMainWorkingLoc() + "\\linking_libraries\\version_patches_" + Global.inputGame + ".json")):
        prexistingVersionPatches = JsonHandler.readFor("\\linking_libraries\\version_patches_" + Global.inputGame, ["versions"])
    else:
        print("---version patches do not exist, please generate version patches before using this option"); exit()

    # get a list of versions (from the base_textures directory)
    versions = [string.name.replace(f"_{Global.inputGame}", "") 
       for string 
       in os.scandir(Path(Global.getMainWorkingLoc(), "base_textures", isRootDirectory=True).getPath()) 
       if (string.name.endswith(f"_{Global.inputGame}"))]

    # add into every version
    for version in versions: # for every version
        if (ut.compareVersions(version, [1, majorUpdate, (minorVersion if (minorVersion != None) else 0)], direction=direction, inclusive=True) == True):
            # if it already exists, use the existing value
            if (version not in prexistingVersionPatches): # create version if doesn't exist
                prexistingVersionPatches[version] = {}
            if (typeSpace not in prexistingVersionPatches[version]): # create typespace if doesn't exist
                prexistingVersionPatches[version][typeSpace] = {}
            prexistingVersionPatches[version][typeSpace][key] = value # always overwrites value

    # write
    JsonHandler.writeAll(f"\\linking_libraries\\version_patches_{Global.inputGame}", {"versions": prexistingVersionPatches})

# generate color signatures between all versions of the game
def generateColorSignatures(type, mode):
    signaturesList = {}

    def buildSignature(image): # is this right?
        image = image.convert("RGBA") # convert to RGBA before anything
        rgba = [0, 0, 0, 0]

        # loop for getting through each image
        vertPos = 0
        while vertPos < image.height:
            horiPos = 0
            while horiPos < image.width:
                currPixel = image.getpixel((horiPos, vertPos))

                # add pixels together
                if ((currPixel[3] <= 10)): horiPos += 1; continue # if the alpha pixel is is 0
                rgba[0] += currPixel[0]
                rgba[1] += currPixel[1]
                rgba[2] += currPixel[2]
                rgba[3] += currPixel[3]

                horiPos += 1
            vertPos += 1
        return rgba

    # -- WiiU --
    if (Global.inputGame == "wiiu"): # type in only needed for the wiiu build (because the wiiu build is type specific)
        wiiuSheet = rd.readWiiuLibFor(type, "Arr")
        wiiuAbstract = rd.readWiiuLibFor(type, "Abstract")

        if (wiiuSheet != False):
            # reg loop section
            wiiuImage = Image.open(Global.getMainWorkingLoc() + "\\base_textures\\wiiu_" + type + ".png")
            currPos = [0, 0]
            
            # regular loop section
            def cont():
                currPos[0] += singularSizeOnTexSheet
                if (currPos[0] >= wiiuImage.size[0]): currPos[1] += singularSizeOnTexSheet; currPos[0] = 0

            for wiiuName in wiiuSheet: # for everything in wiiuSheet
                if (wiiuName == None): # if the wiiulib has a none, just skip it
                    print("WAS NONE")
                    cont()
                    continue
                print(str(wiiuName) + " " + str(currPos))

                # build color signature and add to final
                cropImage = wiiuImage.crop((currPos[0], currPos[1], currPos[0] + singularSizeOnTexSheet, currPos[1] + singularSizeOnTexSheet))
                signaturesList[wiiuName] = buildSignature(cropImage)

                # must be last
                cont()

        if (wiiuAbstract != False):
            # abstract loop section
            for wiiuName in wiiuAbstract:
                print(str(wiiuName))

                wiiuNameKey = wiiuName # else equals wiiuName (key)
                if (mode == "dynamic"): # this determines whether the wiiuKey is gotten dynamically or by the wiiuKey
                    wiiuNameKey = str.split(wiiuAbstract[wiiuName][2], "\\")
                    wiiuNameKey = wiiuNameKey[len(wiiuNameKey) - 1]
                wiiuImage = Image.open(Global.getMainWorkingLoc() + "\\base_textures\\wiiu_abstract\\" + wiiuNameKey + ".png") # this can run because we know they exist
                
                # build color signature and add to final
                signaturesList[wiiuName] = buildSignature(wiiuImage)

        # save the final
        JsonHandler.writeAll("\\color_signatures\\wiiu_" + type, signaturesList)
    # -- Java/Bedrock --
    def checkDirectory(currPath, type, additionalDir = None):
        path = currPath if (additionalDir == None) else (f"{currPath}\\{additionalDir}")
        for file in os.scandir(path): # for every file in the current version of the game for the type
            if (os.path.isdir(f"{path}\\{file.name}")): # check if the file is a directory
                additionalDirAndFileName = f"{additionalDir}\\{file.name}"
                print(f"{(file.name if (additionalDir == None) else additionalDirAndFileName)} is a directory, recursing")
                checkDirectory(currPath, type, file.name if (additionalDir == None) else f"{additionalDir}\\{file.name}") # add to additionalDir and recurse
                
            if ((not file.name.endswith(".png")) and (not file.name.endswith(".tga"))): continue # must be a png
            #print(str(file.name)) # removed bc it creates too many prints
            image = Image.open(path + "\\" + file.name) # open image

            # build color signature and add to final
            fileNameShortened = (file.name.replace(".png", "").replace(".tga", ""))
            signaturesList[type][fileNameShortened if (additionalDir == None) else (f"{additionalDir}\\{fileNameShortened}")] = buildSignature(image)

    if ((Global.inputGame == "java") or (Global.inputGame == "bedrock")):
        for type in SupportedTypes.supportedTypes[Global.inputGame]: # for every type
            signaturesList[type] = {} # ensure type in in the array
            currPath = Global.getMainWorkingLoc() + "\\base_textures\\" + Global.inputVersion + "_" + Global.inputGame + "\\" + type
            checkDirectory(currPath, type)

        # save the final
        JsonHandler.writeAll("\\color_signatures\\" + Global.inputVersion + "_" + Global.inputGame, signaturesList)

# create a linking library
def generateLinkingLibrary():
    linkLib = {}
    
    for type in SupportedTypes.supportedTypes[Global.inputGame]: # for all supported types
        # type specific variables
        wiiuType = type
        if (type.endswith("s")): wiiuType = type[:-1] # if there's and s at the end, get rid of it
        typeAbstract = type + "_abstract"
        wiiuSigs = JsonHandler.readAll("\\color_signatures\\wiiu_" + wiiuType)
        linkSigs = JsonHandler.readFor("\\color_signatures\\" + Global.inputVersion + "_" + Global.inputGame, type)
        wiiuLib = JsonHandler.readAll("\\linking_libraries\\wiiu_" + wiiuType)

        linkLib[type] = {} # ensure type is in linkLib
        linkLib[typeAbstract] = {}
        for wiiuSig in wiiuSigs: # for every wiiu signature
            # find which sigs match
            found = None
            for linkSig in linkSigs: # for every link signature
                if (wiiuSigs[wiiuSig] == linkSigs[linkSig]): # if exact match
                    found = linkSig
                    break
            # check which array/abstract the matching sigs belong in
            if ("Arr" in wiiuLib):
                if (wiiuSig in wiiuLib["Arr"]): # if it's in the wiiu arr
                    linkLib[type][wiiuSig] = found
            if ("Abstract" in wiiuLib):
                if (wiiuSig in wiiuLib["Abstract"]): # not in the wiiu arr
                    linkLib[typeAbstract][wiiuSig] = found
    
    # save whole linkLib
    JsonHandler.writeAll("\\linking_libraries\\" + Global.inputVersion + "_" + Global.inputGame, linkLib)

# get the java texture packs that are on the system for above the version
def getTextures(path, mode):
    if (Global.inputGame == "java"):
        varPath = path + "\\.minecraft\\versions"
        baseVersion = 13

        for file in os.scandir(varPath):
            if (not file.is_dir()): continue # if the file isn't a directory
            if (not file.name.replace(".", "").isnumeric()): continue # check if the directory only has a number
            if (int(file.name.split(".")[1]) < baseVersion): continue # if the file isn't more or equal to the base version
            varPathExt = varPath + "\\" + file.name + "\\" + file.name + ".jar"
            if (not os.path.isfile(varPathExt)): continue # check if the .jar file exists
            if (os.path.isdir(Global.getMainWorkingLoc() + "\\base_textures\\" + file.name + "_java")): # check if the folder already exists in base_textures
                if (mode == "skip"): # only if it's skip mode
                    print("--skipped version " + file.name)
                    continue 
                else: # otherwise, replace all (delete folders)
                    shutil.rmtree(Global.getMainWorkingLoc() + "\\base_textures\\" + file.name + "_java")

            # extraction
            print("--running for " + file.name)
            with ZipFile(varPathExt, "r") as zip: # open the zipfile
                for zipFile in zip.namelist(): # check for only the right files
                    if (zipFile.startswith("assets/minecraft/textures/")):
                        zip.extract(zipFile, Global.getMainWorkingLoc() + "\\output") # extract each one
            
            # move the incorrect export files to base_textures
            shutil.move(Global.getMainWorkingLoc() + "\\output\\assets\\minecraft\\textures", Global.getMainWorkingLoc() + "\\base_textures\\" + file.name + "_java")
        # delete output traces
        shutil.rmtree(Global.getMainWorkingLoc() + "\\output\\assets")
    elif (Global.inputGame == "bedrock"):
        varPath = path + "\\MCLauncher"
        baseVersion = 6

        for file in os.scandir(varPath):
            if (not file.is_dir()): continue # if the file isn't a directory
            if (not file.name.replace("Minecraft-", "").replace(".", "").isnumeric()): continue # check if the directory only has a number
            if (int(file.name.split(".")[1]) < baseVersion): continue # if the file isn't more or equal to the base version
            varPathExt = varPath + "\\" + file.name + "\\data\\resource_packs\\vanilla.zip"
            if (not os.path.isfile(varPathExt)): continue # check if the .zip file exists
            if (os.path.isdir(Global.getMainWorkingLoc() + "\\base_textures\\" + file.name + "_bedrock")): # check if the folder already exists in base_textures
                if (mode == "skip"): # only if it's skip mode
                    print("--skipped version " + file.name)
                    continue 
                else: # otherwise, replace all (delete folders)
                    shutil.rmtree(Global.getMainWorkingLoc() + "\\base_textures\\" + file.name + "_bedrock")

            # extraction
            print("--running for " + file.name)
            with ZipFile(varPathExt, "r") as zip: # open the zipfile
                for zipFile in zip.namelist(): # check for only the right files
                    if (zipFile.startswith("textures/")):
                        zip.extract(zipFile, Global.getMainWorkingLoc() + "\\output") # extract each one
            
            # move the incorrect export files to base_textures
            shutil.move(Global.getMainWorkingLoc() + "\\output\\textures", Global.getMainWorkingLoc() + "\\base_textures\\" + file.name.replace("Minecraft-", "") + "_bedrock")

def _getVersionFromFolderName(folderName:str):
    games = [
        "java",
        "bedrock"
    ]
    for game in games:
        gameUnderscore = f"_{game}"
        if (folderName.endswith(gameUnderscore)): 
            return folderName.replace(gameUnderscore, "")
    print(f"When converting folderName ({folderName}) to version, could not find game")
    exit()

# checks the texture equality
def checkTextureEquality(gameInput:str, versionInput:str, typeInput:str, keyword:str, doUseBaseTextures:bool, doGeneration:bool=False):
    """
    IMPORTANT NOTES:
        - when inequalities are bypassed, it works for ALL versions. Meaning that version based changes are NOT detected for textures in the bypass. These should either be manually handled or determined by the major versions changes (like 1.14 changing villagers)
    """

    path = Path(Global.getMainWorkingLoc(), "base_textures", isRootDirectory=True)
    path.formalize()

    # function to handle reading wiiu textures either by their base_texture location or 1.14 wiiu generation location
    def readWiiuImage(game, inWiiuAbstract:bool, name:str):
        if (doUseBaseTextures == True): # read normally
            return rd.readWiiuImage(inWiiuAbstract, name)
        else:
            name = f"{name}.png" if (not name.endswith(".png")) else name
            image = Image.open(Path(Global.getMainWorkingLoc(), "equality_libraries", "1.14_wiiu", game, name).getPath(withFirstSlash=False))
            return image

    # function to save images to output location
    def writeImage(image:Image, game:str, version:str, type:str, name:str):
        path = Path(Global.getMainWorkingLoc(), "equality_libraries", game, version, type, f"{name}.png", isRootDirectory=True)
        path.formalize()
        folderPath = path.slice(end=(path.getLength() - 1)) # gets path without name
        if (not os.path.isdir(folderPath.getPath())): # checks if the path exists yet
            os.makedirs(folderPath.getPath())
        image.save(path.getPath(), "PNG")

    # function to check if or all
    def checkIfOrAll(value:str, checkValue:str, allValue:str="all"):
        value = value.lower()
        if (value == allValue.lower()): # if value equals the all value
            return True
        if (value == checkValue.lower()): # if the value equals the specific check value
            return True
        return False

    # function for checking equality of an image (returns true or false if the image is equal)
    def checkEquality(imageOne:Image, imageTwo:Image, doTextureGeneration:bool=False, doPrint:bool=False):
        # IMPORTANT: alpha pixel differences (aka invisible pixels) aren't detected
        
        # gets the largest size of the two images combined
        width = imageOne.width if (imageOne.width > imageTwo.width) else imageTwo.width
        height = imageOne.height if (imageOne.height > imageTwo.height) else imageTwo.height
        # blank image from largest sizes if needed
        newImage = None
        if (doTextureGeneration == True):
            newImage = ut.blankImage(width, height)
        # convert images
        imageOne = imageOne.convert("RGBA")
        imageTwo = imageTwo.convert("RGBA")

        # function to convert alpha pixels to full 0
        def formatAlpha(pixel):
            if (pixel[3] == 0):
                pixel = list(pixel)
                # sets whole pixel to 0
                i = 0
                while i < len(pixel):
                    pixel[i] = 0
                    i += 1
                pixel = tuple(pixel)
            return pixel

        # loop throught the largest image
        i = 0
        while i < width:
            j = 0
            while j < height:
                # assumes pixels out of each other's size are equal
                if ( # out of bounds check
                    (i < 0) # too small
                    or (j < 0)
                    or (i >= imageOne.width) # too big one
                    or (j >= imageOne.height)
                    or (i >= imageTwo.width) # too big two
                    or (j >= imageTwo.height)
                    ):
                    j += 1
                    continue
                
                # read pixels
                pixelOne = formatAlpha(imageOne.getpixel((i, j)))
                pixelTwo = formatAlpha(imageTwo.getpixel((i, j)))

                # check equality of pixels
                if (pixelOne != pixelTwo):
                    if (doTextureGeneration == True): # mark the texture on the image and continue
                        # red pixel generation
                        newPixel = []
                        p = 0
                        while p < len(pixelOne) - 1: # -1 stops it from changing the pixels alpha/transparency
                            newPixel.append(int(pixelOne[p] * 0.6))
                            p += 1
                        newPixel[0] = 255 # adds red shade
                        if (pixelOne[3] == 0): # if the pixel to be set is alpha
                            newPixel.append(255)
                            newPixel[2] = 255 # adds green shade
                        newPixel = tuple(newPixel) # converts to tuple so it can be used in putpixel
                        newImage.putpixel((i, j), newPixel)
                    else: # return false (the image ISN'T equal)
                        return False
                elif (doTextureGeneration == True): # if texture is generated, always copy over the regular pixels
                    # image is derived from the first image
                    newImage.putpixel((i, j), pixelOne)
                j += 1
            i += 1
        # cases where the image is equal or if the image needs to be returned
        if (doTextureGeneration == True): # return the image
            return newImage
        else: # return true (the image is equal)
            return True

    # inequality bypass reading
    bypass = JsonHandler.readAll(Path("equality_libraries", "inequality_bypass").getPath())

    inequalities = {}
    # function for handling adding to inequalities
    def addInequality(value, game, version, type):
        if (doGeneration == True): return # dont run if generating images

        derivedVersion = "base_wiiu" if (doUseBaseTextures == True) else "1.14_wiiu"
        try:
            if (value in bypass[game][derivedVersion][type]): # check if it's in the list
                return # found
        except: # not found
            pass # continue

        if (game not in inequalities):
            inequalities[game] = {}
        if (version not in inequalities[game]):
            inequalities[game][version] = {}
        if (type not in inequalities[game][version]):
            inequalities[game][version][type] = []
        inequalities[game][version][type].append(value)

    # list of games
    games = [
        "java",
        "bedrock"
    ]

    # for all games
    for game in games:
        if (not checkIfOrAll(gameInput, game)): continue # must be a the chosen game to continue
        Global.inputGame = game # set uiInput game temporarily for this run
        print(f"{game}")

        # for all version folders of the game
        for dir in os.scandir(path.getPath()):
            if ((not os.path.isdir(path.getPathAppendTemp(dir.name))) or (not dir.name.endswith(game))): continue # must end with the current game name and be directory to continue
            version = _getVersionFromFolderName(dir.name)
            if (not checkIfOrAll(versionInput, version)): continue
            Global.inputVersion = version # temp sets version for this run
            if (doUseBaseTextures == False) and (ut.checkVersion(13, 2, direction=False)): continue # skips versions 1.13.2 or earlier if the base textures aren't being used
            print(f"-{version}")

            # for each type for the game
            for type in SupportedTypes.supportedTypes[game]:
                wiiuType = type if (not type.endswith("s")) else type[:-1] # if there's and s at the end, get rid of it
                if (not checkIfOrAll(typeInput, wiiuType)): continue
                print(f"--{type}")

                # sizing
                singularSize = 16
                if (wiiuType == "particle"):
                    singularSize = 8

                # sheet and override reads
                wiiuArr = rd.readWiiuLibFor(wiiuType, "Arr")
                wiiuOverride = rd.readLinkLibFor(game, f"{wiiuType}_override")
                wiiuLoc = rd.readWiiuLibFor(wiiuType, "Loc")

                # OVERRIDE
                doSheetProcessing = True
                if (wiiuOverride != False):
                    print("   override found")

                    # read images
                    wiiuName = f"wiiu_{wiiuType}"
                    if (checkIfOrAll(keyword, wiiuName)): # checks for keyword match
                        wiiuImage = readWiiuImage(game, False, wiiuName)
                        Global.inputPath = path.getPathAppendTemp(f"{version}_{game}") # needs to be set so that override can read
                        linkImage = runFunctionFromPath("override", wiiuOverride, "particles", type, wiiuImage)
                        if (linkImage != False): # only if an image was found
                            doSheetProcessing = False # skips sheet processing

                            # equality check
                            value = checkEquality(wiiuImage, linkImage, doTextureGeneration=doGeneration)
                            if (typeof(value) is bool):
                                if (value == False):
                                    # add to inequalities list
                                    addInequality(f"{wiiuOverride} (override texture)", game, version, wiiuType)
                            else: # must be image
                                # save image
                                writeImage(value, game, version, wiiuType, wiiuLoc[2]) # uses the wiiu sheet name

                # SHEET
                if (wiiuArr != False) and (doSheetProcessing == True):
                    print("   sheet found")

                    # read wiiu image and link arr
                    wiiuImage = readWiiuImage(game, False, f"wiiu_{wiiuType}")
                    linkArr = rd.readLinkLibFor(game, type)
                    reconstructedImage = ut.blankImage(wiiuImage.size)
                    
                    # loop through textures on the sheet
                    currPos = [0, 0]
                    doSave = False
                    def cont(): # continues the sheet movement
                        currPos[0] += singularSize
                        if (currPos[0] >= wiiuImage.size[0]): 
                            currPos[1] += singularSize
                            currPos[0] = 0
                    def getWiiuImageForCurrTex(): # function that will get the current texture sheet position's texture 
                        wiiuSheetLoc = (currPos[0], currPos[1], currPos[0] + singularSize, currPos[1] + singularSize)
                        return wiiuImage.crop(wiiuSheetLoc)
                    for wiiuName in wiiuArr:
                        if (wiiuName == None): cont(); continue # skip if wiiu arr is none
                        if (checkIfOrAll(keyword, wiiuName)): # checks for keyword match
                            linkName = linkArr[wiiuName] # translate
                            if (linkName == True) or (linkName == False): cont(); continue # skip if link arr is a boolean

                            # read (and version patch if needed) linkImage
                            patchPath = path.copy()
                            patchPath.append(dir.name, (type if (wiiuType != Global.misc) else None), linkName)
                            patchPath = rd.patchForVersion(patchPath.getPath(), type, wiiuName, doCustomProcessing=False) # turns into a string here
                            if (patchPath == None): cont(); continue # if the path uses custom processing
                            try:
                                linkImage = rd.getImage(patchPath)
                            except (rd.notFoundException):
                                print(f"      forced to skip {wiiuName} ({linkName})")
                                continue

                            # equality check
                            value = checkEquality(getWiiuImageForCurrTex(), linkImage, doTextureGeneration=doGeneration)
                            if (typeof(value) is bool):
                                if (value == False):
                                    # add to inequalities list
                                    addInequality(wiiuName, game, version, wiiuType)
                            else: # must be image
                                # save image
                                doSave = True
                                reconstructedImage.paste(value, tuple(currPos))

                        # final
                        cont()

                    # write image reconstruction
                    if (doSave == True):
                        writeImage(reconstructedImage, game, version, wiiuType, wiiuLoc[2]) # uses the wiiu sheet name

                # ABSTRACT
                wiiuAbstract = rd.readWiiuLibFor(wiiuType, "Abstract")
                if (wiiuAbstract != False):
                    print("   abstract found")

                    # read link arr
                    linkAbstract = rd.readLinkLibFor(game, f"{type}_abstract")

                    # loop through textures in the abstract list
                    for wiiuName in wiiuAbstract:
                        if (wiiuName == None): cont(); continue # skip if wiiu arr is none
                        if (checkIfOrAll(keyword, wiiuName)): # checks for keyword match
                            linkName = linkAbstract[wiiuName] # translate
                            if (linkName == True) or (linkName == False): cont(); continue # skip if link arr is a boolean
                            wiiuLoc = wiiuAbstract[wiiuName]
                            wiiuFileName = ut.getWiiuNameFromAbstract(wiiuAbstract[wiiuName][2])

                            # read images (and version patch if needed)
                            wiiuImage = readWiiuImage(game, True, Path(wiiuType, wiiuFileName).getPath(withFirstSlash=False))

                            patchPath = path.copy()
                            patchPath.append(dir.name, (type if (wiiuType != Global.misc) else None), linkName)
                            patchPath = rd.patchForVersion(patchPath.getPath(), f"{type}_abstract", wiiuName, doCustomProcessing=False) # turns into a string here
                            if (patchPath == None): cont(); continue # if the path uses custom processing
                            try:
                                linkImage = rd.getImage(patchPath)
                            except (rd.notFoundException):
                                print(f"      forced to skip {wiiuName} ({linkName})")
                                continue

                            # equality check
                            value = checkEquality(wiiuImage, linkImage, doTextureGeneration=doGeneration)
                            if (typeof(value) is bool):
                                if (value == False):
                                    # add to inequalities list
                                    addInequality(wiiuName, game, version, wiiuType)
                            else: # must be image
                                # save image
                                writeImage(value, game, version, wiiuType, wiiuFileName) # uses the wiiu sheet name

        # magic with when pinpointing version of differences
        #   will print the earliest version of the change
        if (game in inequalities): # game must be in inequalities for it to work
            if (len(inequalities[game]) > 1): # only runs if multiple versions were checked
                # for each version
                earliestVersion = [100, 100, 100]
                for version in inequalities[game]:
                    # format version as an array
                    versionArr = str.split(version, ".")
                    if (len(versionArr) == 2): versionArr.append(0)
                    # convert array to all ints
                    i = 0
                    while i < 3:
                        versionArr[i] = int(versionArr[i])
                        i += 1
                    # go through array and find smallest value by left to right
                    i = 0
                    while i < 3:
                        oldNum = earliestVersion[i]
                        newNum = versionArr[i]
                        if (newNum < oldNum): # if smaller than update earliest
                            earliestVersion = versionArr
                            break
                        i += 1
                # convert int array back to string
                i = 0
                while i < 3:
                    earliestVersion[i] = str(earliestVersion[i])
                    i += 1
                earliestVersion = str.join(".", earliestVersion)
                print(f"Earliest version: {earliestVersion} ({game})")

    # save the inequalities list to a file
    if (doGeneration == True): return # dont run if generating images
    JsonHandler.writeAll(Path("equality_libraries", "inequalities").getPath(), inequalities)

# generates the MT Locs
def generateMTLocs():
    # output text
    hierarchy = {
        "Base Game": {
            "Main/None": {
                "Steve Skins": "mob\\."
            },
            "1_2_2": {},
            "TitleUpdate": {
                "Alex Skins": "mob\\."
            }
        },
        "Update": {
            "Main/None": {},
            "1_2_2": {},
            "TitleUpdate": {
                "Dev Skins": "mob\\."
            }
        }
    }
    lst = ["----- Textures as a List of File Locations -----\n"]
    lst.append("Dev Skins are located at: storage_mlc\\usr\\title\\0005000e\\101d9d00\\content\\Common\\res\\TitleUpdate\\res\\mob\\")
    lst.append("Steve Skins are located at: storage_mlc\\usr\\title\\00050000\\101d9d00\\content\\Common\\res\\mob\\")
    lst.append("Alex Skins are located at: storage_mlc\\usr\\title\\00050000\\101d9d00\\content\\Common\\res\\TitleUpdate\\res\\mob\\")
    lst.append("") # empty makes a new line

    # writer
    writer = Writer("build", Path())

    # for each type (depends on java)
    for type in SupportedTypes.supportedTypes["java"]:
        # wiiu reads
        wiiuAbstract = rd.readWiiuLibFor(type, "Abstract")
        wiiuLoc = rd.readWiiuLibFor(type, "Loc")

        # if there is a sheet
        if (wiiuLoc != False):
            wiiuName = ut.getWiiuNameFromAbstract(wiiuLoc[2])
            print(f"found sheet: {wiiuName}")
            # list
            path = writer.generatePath(WiiULocation("system", wiiuLoc[0], wiiuLoc[1], Path(wiiuLoc[2])), type)
            lst.append(f"{wiiuLoc[2]}: {path.getPath(withFirstSlash=False)}.png")
            # hierarchy
            side = "Base Game" if (wiiuLoc[0] == "base") else "Update"
            section = "Main/None" if (wiiuLoc[1] == "main") else ("1_2_2" if (wiiuLoc[1] == "122") else "TitleUpdate")
            addon = wiiuLoc[2]
            hierarchy[side][section][wiiuName] = f"{addon}.png"

        # if there is an abstract
        if (wiiuAbstract != False):
            # for every key, value in the dict
            for wiiuName, location in wiiuAbstract.items():
                print(f"found abstract: {wiiuName}")
                # list
                path = writer.generatePath(WiiULocation("system", location[0], location[1], Path(location[2])), type)
                lst.append(f"{wiiuName}: {path.getPath(withFirstSlash=False)}.png")
                # hierarchy
                side = "Base Game" if (location[0] == "base") else "Update"
                section = "Main/None" if (location[1] == "main") else ("1_2_2" if (location[1] == "122") else "TitleUpdate")
                addon = location[2]
                hierarchy[side][section][wiiuName] = f"{addon}.png"

    # write MTLocs
    JsonHandler.writeAll("\\Info\\MTLocs.json", hierarchy)
    with open(f"{Global.getMainWorkingLoc()}\\Info\\MTLocs.txt", 'w') as MTLocs:
        MTLocs.write("\n".join(lst))
        