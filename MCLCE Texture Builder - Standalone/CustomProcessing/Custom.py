from abc import ABC, abstractmethod
import CustomProcessing.Custom
import TextureLibs.Global as Global
import CodeLibs.Logger as log
from CodeLibs.Logger import print
import CustomProcessing
import importlib
import TextureLibs.TextureUtility as ut
import time
import TextureLibs.SizingImage as SizingImage
from builtins import type as typeof
from TextureLibs.SizingImage import SizingImage as Image

class Function(ABC):
    """
    Description:
        a custom function base class that is intended to be extended for each custom function
    Important:
        - Custom function (class) names with spaces must be replaced with __ (double underscore)
    """

    def __init__(self, wiiuName, type, wiiuImage, isShared=False) -> None:
        """
        Description:
            all custom functions require wiiuName, type and wiiuImage
        """
        super().__init__()
        self.wiiuName = wiiuName
        self.type = type
        self.isShared = isShared

        # special processing for wiiuImage being none
        if (wiiuImage == None): # if the image is none, try to get it from the type and wiiuName
            # WARNING: this code will break if you try to get an image which isn't abstract; rather it will return the entire sheet not a subsection of it
            # however, there is no way to actually detect this
            try:
                wiiuType = self.type[:-1] if (self.type.endswith("s")) else self.type
                self.wiiuImage = Image.open(f"{Global.getMainWorkingLoc()}\\base_textures\\{Global.getLayerGame()}_abstract\\{wiiuType}\\{wiiuName}.png")
            except FileNotFoundError:
                print(f"wiiuImage was set to none and an abstract image for the wiiuName ({wiiuName}) couldn't be found, wiiuImage will be none in this case", log.WARNING)
                self.wiiuImage = None
        else:
            self.wiiuImage = wiiuImage

    @abstractmethod
    def createImage(self):
        """
        Description:
            create function must be overriden, this is how the texture is processed. it must return an image
        """
        pass

# function to end the program if debug mode is disabled, or return an error image
def _closeProgramIfDebugFalse(name:str, message:str):
    if (Global.useErrorTexture == True):
        print(f"using error texture for texture {name}, because a function for it could not be found", log.ERROR)
        return Global.errorImage.resize(ut.size()) # resize to singular size on sheet if needed
    print(message, log.ERROR)
    Global.stopGen()

# function for getting a name with underscores
def formatName(name:str):
    """
    Description:
        formats a name with underscores
    """
    return name.replace(" ", "__")

# gets a class from CustomProcessing
def getClass(functionType:str, functionName:str):
    """
    Description:
        gets a custom class from the input (not an instance)
    ---
    Variables:
        - functionType : String <>
            - The location to find/type of custom function
            - Abstract
            - External
            - Versional
            - Shared
        - functionName : String <>
            - The name of the custom function you want to run
        - wiiuKey : String <>
            - The current wiiuName
        - type : String <>
            - The current type
        - wiiuImage : SizingImage <>
            - The current wiiuImage
    ---
    Returns:
        - A SizingImage proccessed by the respective custom function
    """
    
    # function to get the functionType module module
    def getFunctionTypeModule(root):
        match (str.lower(functionType) if isinstance(functionType, str) else functionType): # try to do .lower() on string, but if not just pass the value
            case "abstract":
                return root.Abstract
            case "external":
                return root.External
            case "versional":
                return root.Versional
            case "override":
                return root.Override
            case None | "shared":
                return root
            case _:
                Global.stopGen(f"\"{functionType}\" is not a valid functionType")
    
    # gets the game module from the function type
    def getGameModule(root):
        if (hasattr(root, "java")) or (hasattr(root, "bedrock")):
            if (Global.inputGame == "java"):
                return root.java
            elif (Global.inputGame == "bedrock"):
                return root.bedrock
            else:
                Global.stopGen("Custom > getClass > getGameModule > Global.inputGame wasn't set to a valid game name")
                return
        else: # if has no game/can't find game, return root
            return root
    
    functionNameUnderscores = formatName(functionName)
    
    # get root module for checking from
    checking_module = getGameModule(getFunctionTypeModule(CustomProcessing))

    # try to locate the specific module
    try:
        module = importlib.import_module(f"{checking_module.__name__}.{functionNameUnderscores}") # import the module and create an image with it
    except ImportError:
        return _closeProgramIfDebugFalse(functionName, f"could not find custom function file \"{functionNameUnderscores}\". There also may be an import error within the custom function file (check your imports)")

    # check if the module has the right class name
    if hasattr(module, functionNameUnderscores):
        cls = getattr(module, functionNameUnderscores)  # get the class from the module
        if (not issubclass(cls, CustomProcessing.Custom.Function)): # if the class doesn't extend custom function class
            return _closeProgramIfDebugFalse(functionName, f"class \"{functionNameUnderscores}\" doesn't extend CustomFunction")
        return cls
    else:
        return _closeProgramIfDebugFalse(functionName, f"class \"{functionNameUnderscores}\" not found in module \"{functionNameUnderscores}\"")

# runs the function internally
def _runFunction(cls_instance:Function, isPrintRecursed:bool, *args):
    """
    Description
        internal function for running functions
    """
    
    args = args[0] # fixes multi-tupling
    functionName = cls_instance.__class__.__name__

    def generateImage():
        if (cls_instance.isShared == True):
            return cls_instance.createImage(args)
        else: # is not shared
            return cls_instance.createImage()
    
    # try to generate the image while determing if timing should be used
    output = None
    if (log.isEnabled(log.CUSTOMFUNCTIONTIMING) and (isPrintRecursed != None)):
        startTime = time.perf_counter()
        output = generateImage()
        endTime = time.perf_counter()
        timeToComplete = (endTime - startTime)
        indentAmount = 0 if (timeToComplete > 0.5) else 3
        print(f"completed in {timeToComplete:.6f} seconds; function '{functionName}'", log.CUSTOMFUNCTIONTIMING, indentAmount)
    else:
        output = generateImage()
    
    # check if output was valid
    if (output == None): # if no output was given, meaning the function returned nothing
        return _closeProgramIfDebugFalse(functionName, f"the function for \"{functionName}\" returned None")
    if (isPrintRecursed != None): # none = no print
        print(f"found function for \"{functionName}\" and returned", log.CUSTOMFUNCTION if (isPrintRecursed == False) else log.CUSTOMFUNCTIONRECURSION)
    return output

# runs a function from custom processing by using the class
def runFunctionFromInstance(cls_instance:Function, isPrintRecursed:bool=False, *args):
    """
    Description:
        runs a custom function according to the input
    ---
    Variables:
        - cls_instance : CustomProcessing.Custom.Function <>
            - A class instance to run the function from
        - wiiuKey : String <>
            - The current wiiuName
        - type : String <>
            - The current type
        - wiiuImage : SizingImage <>
            - The current wiiuImage
        - isPrintRecursed : int <0>
            - Whether or not the function was called as part of a recursion
            - If set to None, then no print is made
        - *args : A list of extra arguments. These can only be included when executing a shared function
    ---
    Returns:
        - A SizingImage proccessed by the respective custom function
    """
    
    return _runFunction(cls_instance, isPrintRecursed, args)

# runs a function from custom processing by using tree/folder pathing
def runFunctionFromPath(functionType:str, functionName:str, wiiuKey:str, type:str, wiiuImage:SizingImage, isPrintRecursed:bool=False, *args):
    """
    Description:
        runs a custom function according to the input
    ---
    Variables:
        - functionType : String <>
            - The location to find/type of custom function
            - Abstract
            - External
            - Versional
            - Shared
        - functionName : String <>
            - The name of the custom function you want to run
        - wiiuKey : String <>
            - The current wiiuName
        - type : String <>
            - The current type
        - wiiuImage : SizingImage <>
            - The current wiiuImage
        - isPrintRecursed : int <0>
            - Whether or not the function was called as part of a recursion
            - If set to None, then no print is made
        - *args : A list of extra arguments. These can only be included when executing a shared function
    ---
    Returns:
        - A SizingImage proccessed by the respective custom function
    """

    cls = getClass(functionType, functionName)
    if isinstance(cls, SizingImage.SizingImage): return cls # if return is an image, return
    cls_instance = cls(wiiuKey, type, wiiuImage, isShared=(functionType.lower() == "shared"))
    return _runFunction(cls_instance, isPrintRecursed, args)
