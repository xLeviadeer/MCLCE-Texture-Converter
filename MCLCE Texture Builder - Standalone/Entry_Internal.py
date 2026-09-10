# runs input checks for running Internal

from xLPyBasics.JsonAPI import JsonHandler
from xLPyBasics.PathAPI import Path
Path.default_prepension.set(Path.cwd())

import TextureLibs.Internal as Internal
import TextureLibs.Global as Global
import os
from CodeLibs.Path import Path
from builtins import type as typeof

selections = {
    "options": [
        "version patches",
        "move assets",
        "generate color signatures",
        "generate linking library",
        "get textures",
        "separate wiiu textures",
        "check wiiu abstract texures",
        "check texture equality",
        "generate MTLocs"
    ],
    "games": [
        "java",
        "bedrock",
        "wiiu"
    ],
    "gamesNoWiiu": [
        "java",
        "bedrock"
    ],
    "gamesNoWiiuAll":
    [
        "java",
        "bedrock",
        "all"
    ],
    "wiiuSupportedTypes": [
        "block",
        "item",
        "particle",
        "entity",
        "environment",
        "misc"
    ],
    "colorSigModes": [
        "dynamic",
        "key"
    ],
    "fileWriteModes": [
        "replace",
        "skip"
    ],
    "set": [
        "UI",
        "Command"
    ],
    "versionPatchOptions": [
        "Specified Addition",
        "Dynamic Addition"
    ],
    "versionPatchDirections": [
        "equal and up", 
        "equal and down"
    ],
    "generateDifferenceTextures": [
        "library only",
        "images only"
    ],
    "derivedVersion": [
        "base wiiu textures",
        "1.14 wiiu generation"
    ]
}

def selection(chosenArr):
    print("Please select " + chosenArr)
    i = 0
    while i < len(selections[chosenArr]):
        print(str(i) + ") " + selections[chosenArr][i])
        i += 1
    selected = int(input())
    return (selected, selections[chosenArr][selected]) # 0th in array is the index selected, 1st in array is the name of the selected

def selectionVersion(loc, endingInput, includeAll:bool=False):
    ending = "_" + Global.inputGame
    if (endingInput != None): ending += endingInput

    # display verisons to choose from (from file)
    print("Please select a version")
    versions = []
    i = 0
    for file in os.scandir(Global.getMainWorkingLoc() + "\\" + loc):
        if (not file.name.endswith(ending)): continue # only files of the right game
        currVersion = file.name.replace(ending, "")
        versions.append(currVersion)
        print(str(i) + ") " + currVersion)
        i += 1
    if (includeAll == True):
        versions.append("all")
        print(f"{i}) all")

    # get choice and return
    selected = int(input())
    return versions[selected]

selectedMain = selection("options")[1]
match (selectedMain):
    case "version patches":
        Global.inputGame = selection("games")[1]
        additionType = selection("versionPatchOptions")[0]
        if (additionType == 0):
            # - get settings -
            # typeSpace
            i = 0
            typeSpaceOptions = []
            print("select a typeSpace")
            for type in JsonHandler.read_all(("linking_libraries", "Base_java")):
                print(f"{i}) {type}")
                typeSpaceOptions.append(type)
                i += 1
            typeSpace = typeSpaceOptions[int(input())]
            # key
            key = str(input("input a value string (wiiu name)\n"))
            # value
            value = input("input a value (booleans supported)\n")
            if (value.lower() == "true"):
                value = True
            elif (value.lower() == "false"):
                value = False
            # majorUpdate
            majorUpdate = int(input("input a major update\n"))
            # minorVersion
            minorVersion = input("input a minor version (none supported)\n")
            if (
                (minorVersion == None)
                or (minorVersion == "")
                or (minorVersion.lower() == "none")
            ):
                minorVersion = None
            else:
                minorVersion = int(minorVersion)
            # direction
            direction = selection("versionPatchDirections")[0]
            if (direction == 0):
                direction = True
            else:
                direction = False
            
            Internal.addToVersionPatches(typeSpace, key, value, majorUpdate, minorVersion, direction)
        else:
            Internal.generateVersionPatches()
    case "move assets":
        set = selection("set")[1]
        Internal.moveAssets(set)
    case "generate color signatures":
        Global.inputGame = selection("games")[1]
        type = None
        if (Global.inputGame == "wiiu"):
            type = selection("wiiuSupportedTypes")[1]
        if ((Global.inputGame == "java") or (Global.inputGame == "bedrock")):
            Global.inputVersion = selectionVersion("base_textures", None)
        mode = selection("colorSigModes")[1]
        Internal.generateColorSignatures(type, mode)
    case "generate linking library":
        Global.inputGame = selection("gamesNoWiiu")[1]
        Global.inputVersion = selectionVersion("color_signatures", ".json")
        Internal.generateLinkingLibrary()
    case "get textures":
        Global.inputGame = selection("games")[1]
        mode = selection("fileWriteModes")[1]
        path = input("please input a .minecraft path (out of the folder)\nOR\nplease input an MC Launcher path (out of the folder)\n")
        Internal.getTextures(path, mode)
    case "separate wiiu textures":
        type = selection("wiiuSupportedTypes")[1]
        Internal.separateWiiuSheet(type)
    case "check wiiu abstract texures":
        type = selection("wiiuSupportedTypes")[1]
        Internal.checkAbstractTextures(type)
    case "check texture equality":
        game = selection("gamesNoWiiuAll")[1]
        Global.inputGame = game # needs to be set here so that the selectionVersion will work
        version = selectionVersion("base_textures", None, includeAll=True)
        selections["wiiuSupportedTypes"].append("all") # adds all as an option for this command only
        type = selection("wiiuSupportedTypes")[1]
        keyword = input("Please enter a keyword (wiiu type) name of a texture; press enter for none (to target an override texture, please input \"wiiu_type\")\n")
        if (keyword == ""): keyword = "all"
        doUseBase = (selection("derivedVersion")[0] == 0)
        doGeneration = (selection("generateDifferenceTextures")[0] == 1) # option 1 would be "images only"
        Internal.checkTextureEquality(game, version, type, keyword, doUseBase, doGeneration)
    case "generate MTLocs":
        Internal.generateMTLocs()
    case _:
        print("You did something wrong, please try again")