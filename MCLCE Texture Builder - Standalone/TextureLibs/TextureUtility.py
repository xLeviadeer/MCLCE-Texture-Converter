from xLPyBasics.Dependencies import compare_versions

from builtins import type as typeof
import TextureLibs.Global as Global
import TextureLibs.Global as Global
from CodeLibs import Logger as log
from CodeLibs.Logger import print

# try to import image
try:
    from TextureLibs.SizingImage import SizingImage as Image
    import TextureLibs.SizingImage as si
except ModuleNotFoundError:
    pass # this will cause the program to fail later, but only runs when installing Pillow

# --- utility variables --- 

singularSizeOnTexSheet = 16
mobside = 64
mobsideHalf = int(mobside / 2)
mobsize = (mobside, mobside)

# --- library of utility functions ---

def test(func):
    """
    Decorator for marking functions as test functions not to be used in a final result
    """
    
    func.is_test = True
    return func

def blankImage(size=singularSizeOnTexSheet, height=None, color=(0, 0, 0, 0), doResize=True):
    """
    Description:
        Generates a blank image of the input size
    ---
    Arguments:
        - size : Integer <singularTexSizeOnSheet>
            - X size
        - height : Integer <size>
            - Y size
        - color : Tuple <(0, 0, 0, 0)>
            - Determines the color of the blank image
    ---
    Returns:
        - Image
    """
    # function will account for tuples as size, only 1 value as size, having no size, too many size provided
        # all values must at least have the right type of value provided (integers)
    return Image.new("RGBA", ((((size,) * 2) if (not height) else (size, height))) if (typeof(size) is not tuple) else (size[:2] if (len(size) > 1) else size), color, doResize=doResize)

def size(size=singularSizeOnTexSheet, height=None):
    """
    Description:
        Creates a tuple that works as a size
    ---
    Arguments:
        - size : Integer <singularTexSizeOnSheet>
            - X size
        - height : Integer <size>
            - Y size
    ---
    Returns:
        - Tuple : length of 2
    """
    return (int(size),) * 2 if (not height) else (int(size), int(height))

def checkVersion(majorUpdate:int, minorVersion:int=0, subVersion:int=0, direction:bool=True) -> bool:
    """
    Description: 
        Checks the current version against the input version, inclusive
    ---
    Arguments:
        - majorUpdate : Integer <>
        - minorVersion : Integer <0>
            - If left empty, checks against all (the latest possible) minor version 
        - subVersion : Integer <0>
            - If left empty, checks against all (the latest possible) sub version
        - direction : Boolean <True>
            - True: checks current version is equal or higher than input
            - False: checks current version is equal or lower than input
    ---
    Returns:
        - Boolean
    """
    minorVersion = 0 if (minorVersion == None) else minorVersion # change minorVersion None to 0
    return compare_versions(Global.inputVersion, [1, majorUpdate, minorVersion, subVersion], direction, inclusive=True)

def grayscale(image, enhanceBrightness=False):
    """
    Description:
        Turns an image to grayscale
    ---
    Arguments:
        - image : Image <>
        - enhanceBrightness : Boolean <False>
            - determines whether the image should be brighened after being turned grayscale
    ---
    Returns:
        - Image
    """
    image = image.convert("RGBA")

    i = 0
    while (i < image.width):
        j = 0
        while (j < image.height):
            currPixel = image.getpixel((i, j))
            if (currPixel[3] == 0):
                j += 1
                continue
            lightness = int(currPixel[0] * 299/1000 + currPixel[1] * 587/1000 + currPixel[2] * 114/1000)
            if (enhanceBrightness):
                lightness = (lightness + 50) if ((lightness + 50) < 255) else 255 # add 50 to lightness or max it out if it's too bright
            image.putpixel((i, j), (lightness, lightness, lightness, currPixel[3])) # add them to the color image
            j += 1
        i += 1
    return image

def getOpacityTexture(image, getOpacityPortion, *, levelOfDetection = 10, doZeroDetection=False):
    """
    Description:
        Returns either the opacity portion or inverse-opacity portion of the input image
    ---
    Arguments:
        - image : Image <>
            - the input image
        - getOpacityPortion : Boolean <>
            - True: returns the opacity (clear) portion of the image
            - False: returns the inverse-opacity (visible) portion of the image
        - levelOfDetection : Integer <10>
            - the level of alpha detection up from 0 to include when defining portions of the image
        - doZeroDetection : Boolean <False>
            - determines whether invisible pixels are used when determining the opacity texture
            - using this will mean all invisible pixels are turned to white, but this also means all pixels will be accounted for, even completely invisible ones
    ---
    Returns:
        - Image
    """
    finalImage = blankImage(image.size, doResize=False)

    i = 0
    while (i < image.width):
        j = 0
        while (j < image.height):
            currPixel = image.getpixel((i, j))
            if (currPixel[3] == 0) and (doZeroDetection == False): # if pixel is alpha
                j += 1
                continue
            elif ((currPixel[3] < levelOfDetection) and (getOpacityPortion)): # if the pixel is very clear, but not invisible (true for getting opacity portion)
                finalImage.putpixel((i, j), (currPixel[0], currPixel[1], currPixel[2], 255)) # add the pixel, but with no opacity
            elif ((currPixel[3] > levelOfDetection) and (not getOpacityPortion)): # add the opposite (easily visible) pixels (if false)
                finalImage.putpixel((i, j), (currPixel[0], currPixel[1], currPixel[2], 255)) # add the pixel, but with no opacity

            j += 1
        i += 1

    return finalImage

def getImageNoOpacity(image, *, doZeroDetection=False):
    """
    Description:
        Takes the input image and returns it with no opacity
    ---
    Arguments:
        - image : Image <>
        - doZeroDetection : Boolean <False>
            - determines whether invisible pixels are used when determining the texture
            - using this will mean all invisible pixels are turned to white, but this also means all pixels will be accounted for, even completely invisible ones
    ---
    Returns:
        - Image
    """
    image = Image.convert(image, "RGBA")
    i = 0
    while i < image.width:
        j = 0
        while j < image.height:
            currPixel = image.getpixel((i, j))
            if (currPixel[3] == 0) and (doZeroDetection == False):
                j += 1
                continue
            image.putpixel( (i, j), tuple(list(currPixel)[:3] + [255]) ) # converts pixel to list and slices it then appends a 255 (no opacity) value to it and converts it back to a tuple and pastes it back to the current pixel
            j += 1
        i += 1
    return image

def changeSingularSize(num: int):
    if (si.verifyPowerOfTwo(num, "sigularSizeOnTexSheet", overrideMinimum=8) == True): # verifies power of two and allows min of 8
        global singularSizeOnTexSheet
        singularSizeOnTexSheet = si.convertInt(num)

def getWiiuNameFromAbstract(locAddon):
    """
    Description:
        Picks the wiiu file name out of the loc addon path
    ---
    Arguments:
        - locAddon : String <>
    """
    wiiuNameKey = str.split(locAddon, "\\")
    return wiiuNameKey[len(wiiuNameKey) - 1]

def forEveryPixel(image, function, useExistingImage: bool=False, imageConversionMode: str="RGBA", arguments: tuple=None):
    """
    Description:
        Do a certain function for every pixel in an image
    ---
    Arguments:
        - image : Image <>
        - function : Function <>
            - Description:
                - Function that will be ran for each pixel of the image
            - Arguments:
                - "pixel" : Tuple
                - "x" : Integer
                - "y" : Integer 
                - "image" : Image
                - "args" : Tuple
            - Returns:
                - Tuple, pixel to set to image
                - None, do not set pixel
        - useExistingImage : Boolean <False>
            - True: pastes changes onto a copy of the exisitng image
            - False: pastes changes onto an empty image
        - imageConversionMode : String <RGBA>
            - Sets the conversion mode for the image before it is processed
        - arguments : Tuple <>
            - A tuple for sending arguments into the program to be bassed to the function
    ---
    Returns:
        - Image
    """
    newImage = blankImage(image.size, doResize=False) if (useExistingImage == False) else image.copy() # uses the specified type of base image
    image = image.convert(imageConversionMode)

    i = 0
    while (i < image.width):
        j = 0
        while (j < image.height):
            currPixel = image.getpixel((i, j))
            newPixel = function(currPixel, i, j, image, arguments)
            if (newPixel != None): # determines whether to set pixel or not
                newImage.putpixel((i, j), newPixel)

            j += 1
        i += 1

    return newImage

def tupleIsPosition(tup:tuple) -> bool:
    """
    Description:
        Verifies that a tuple is a position (length of 2, all ints)
    ---
    Arguments:
        - tup : Tuple <>
    ---
    Returns:
        - Boolean, true if correctly formatted
    """
    if (not isinstance(tup, tuple)): # provided tup value isn't a tuple
        return False
    if (len(tup) != 2) or any(not isinstance(value, int) for value in tup): # provided tuple isn't correctly formatted
        return False
    return True

def wiiuType(type:str) -> str:
    """Takes a type and removes the s from it if it exists aka gets the wiiu type

    Args:
        type (str): expected to be link type name

    Returns:
        str: type with no s at the end aka wiiu type
    """

    return type[:-1] if (type.endswith("s")) else type

def findAverageColor(image:Image, alpha:int=255) -> tuple[4]:
    """Finds the average color out of an image

    Args:
        image (Image): image to find average color from
        alpha (Integer): the alpha value to assign to the pixel (255 is opaque, 0 is colorless)

    Returns:
        tuple[4]: a color tuple of format (RBGA) padded with the alpha value (default of 255, opaque)
    """
    
    # convert image
    image = image.convert("RGBA")

    averagePixel = [0] * 3
    foundCount = 0

    # add pixels
    i = 0
    while i < image.width:
        j = 0
        while j < image.height:
            currPixel = image.getpixel((i, j))
            if (currPixel[3] == 0):
                j += 1
                continue
            # add to average pixel
            b = 0
            while b < 3: # only should ever include 3, no opacity
                averagePixel[b] += currPixel[b]
                b += 1
            foundCount += 1
            
            j += 1
        i += 1

    # find average
    foundCount = foundCount if (foundCount != 0) else 1 # sets foundcount to 1 if it's 0 (so there is no division by 0)
    c = 0
    while c < 3:
        averagePixel[c] = round(averagePixel[c] / foundCount) # average each value
        c += 1
    return tuple(list(averagePixel) + [255])
