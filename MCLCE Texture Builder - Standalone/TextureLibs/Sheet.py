from typing import Union
from TextureLibs.SizingImage import SizingImage as Image
from CodeLibs.Path import Path
import TextureLibs.Global as Global
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class SheetExtractor():
    def __init__(self, 
                imagePathOrSize:Union[Image, Path, tuple[int, int]],
                subImageSize:tuple,
                wiiuName:str=None,
                type:str=None,
                expectedSize:tuple=None,
                doVersionPatches:bool=True,
                doPrint:bool=False,
                dox16Handling:bool=True):
        """
        Description:
            Creates a class holding an image in sheet format which can be used to non-destructively extract sub-images from
        ---
        Arguments:
            - imagePathOrSize : Image, Path or Tuple <>
                - an Image, Path or tuple of ints length 2 variable which the sheet originates from or determines the size of the image
            - subImageSize : Tuple <>
                - must be a tuple of length 2
                - determines the size of sub-images on the sheet
                - is NOT required to be exactly sized to the sheet (sub-images can be cut off at the edges)
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
        """        
        # verify or try to read image
        image = None
        if ut.tupleIsPosition(imagePathOrSize): # size tuple
            image = ut.blankImage(imagePathOrSize)
        elif isinstance(imagePathOrSize, Path): # path
            if any(value is None for value in (wiiuName, type, expectedSize)): 
                Global.stopGen("attempting to read image from path (in SheetExtrator) but required parameters have not been set for reading")
            image = rd.readImageSingular(wiiuName, imagePathOrSize.getPath(), type, expectedSize, doVersionPatches=doVersionPatches, doPrint=doPrint, dox16Handling=dox16Handling)
        elif isinstance(imagePathOrSize, Image): # image
            image = imagePathOrSize
        else: 
            Global.stopGen("the provided imagePathOrSize was not an image or a path")
        self.sheet = image

        # check formatting of subImageSize
        if (not ut.tupleIsPosition(subImageSize)):
            Global.stopGen("subImageSize (of SheetExtractor) isn't a tuple of the correct format")
        
        # set subsize pix
        self.subSizeXPix = subImageSize[0]
        self.subSizeYPix = subImageSize[1]

        # subsize X/Y pos would always be 1

    def _tuplePositionCheck(self, pos) -> None:
        if (not ut.tupleIsPosition(pos)):
            Global.stopGen("provided value isn't a tuple of the correct format")

    def _intCheck(self, value) -> None:
        if (not isinstance(value, int)):
            Global.stopGen("the provided value isn't an int")

    def getPixelXOf(self, x:int) -> int:
        """
        Description:
            gets the pixel position based on assuming the provided value is an x value
        ---
        Arguments:
            - x : int <>
        ---
        Returns:
            - integer, pixel position
        """
        self._intCheck(x)
        return self.subSizeXPix * x
    
    def getPixelYOf(self, y:int) -> int:
        """
        Description:
            gets the pixel position based on assuming the provided value is a y value
        ---
        Arguments:
            - y : int <>
        ---
        Returns:
            - integer, pixel position
        """
        self._intCheck(y)
        return self.subSizeYPix * y

    def getPixelPositionOf(self, pos:tuple) -> tuple[int, int]:
        """
        Description:
            gets the pixel position of the provided sheet position
        ---
        Arguments:
            - pos : Tuple <>
                - must be a position tuple (length 2, ints only)
        ---
        Returns
            - Tuple of form (int, int)
        """
        self._tuplePositionCheck(pos)
        return (self.getPixelXOf(pos[0]), self.getPixelYOf(pos[1]))

    def extract(self, pos:tuple, chunk:tuple=(1, 1), doResize:bool=True) -> Image:
        """
        Description:
            Extracts an image out of the sheet from the given position
        ---
        Arugments:
            - pos : Tuple <>
                - must be a position tuple (length 2, ints only)
            - chunk : Tuple <(1, 1)>
                - determines how many positions to also include in the extraction
                - must be a distance tuple (length 2, ints only)
        ---
        Returns:
            - Image
        """
        # main format checks and conversion
        chunkPos = self.getPixelPositionOf(chunk)
        pixelPos = self.getPixelPositionOf(pos)

        # negative checks
        if any(value < 1 for value in chunk) or any(value < 0 for value in pos):
            raise ValueError("neither pos nor chunk can contain negative values and chunk cannot be 0")        

        # check if position is inside of the sheet
        if (pixelPos[0] >= self.sheet.width) or (pixelPos[1] >= self.sheet.height):
            raise ValueError("provided pos results in a pixel position outside of the image sheet")
        
        # check chunk format and get positions
        chunkPos = [(pixelPos[0] + chunkPos[0]), (pixelPos[1] + chunkPos[1])] # add to pixel pos to get total instead of offset value

        # check if the crop is inside of the sheet and crop down
        if (chunkPos[0] > self.sheet.width): chunkPos[0] = self.sheet.width
        if (chunkPos[1] > self.sheet.height): chunkPos[1] = self.sheet.height
        chunkPos = tuple(chunkPos)

        # define crop box
        cropBox = pixelPos + chunkPos

        # crop and return image
        return self.sheet.crop(cropBox, doResize=doResize)

    def insert(self, pos:tuple, image:Image, isDestructive:bool=True, doResize:bool=True) -> Union[None, Image]:
        """
        Description:
            Inserts an image onto the sheet at the given position
        ---
        Arugments:
            - pos : Tuple <>
                - must be a position tuple (length 2, ints only)
            - image : Image <>
            - isDestructive : Bool <False>
                - True: returns none and inserts the image onto the stored sheet
                - False: returns the new image instead of inserting on the stored sheet
        """
        # check pos format and get positions
        pixelPos = self.getPixelPositionOf(pos)

        # check if position is inside of the sheet
        if (pixelPos[0] >= self.sheet.width) or (pixelPos[1] >= self.sheet.height):
            raise ValueError("provided pos results in a pixel position outside of the image sheet")
        
        # check if the image is an image
        if (not isinstance(image, Image)):
            Global.stopGen("image value was not an Image")

        # insertion based on destructive status
        if (isDestructive == True):
            self.sheet.paste(image, pixelPos, doResize=doResize)
        else:
            sheet = self.sheet.copy()
            sheet.paste(image, pixelPos, doResize=doResize)
            return sheet

    def getSheet(self) -> Image:
        """
        Description:
            Returns the sheet image
        ---
        Returns:
            - Image, sheet image
        """
        return self.sheet

    # size X pix
    @property
    def sizeXPix(self):
        return self.sheet.width
    # size Y pix
    @property
    def sizeYPix(self):
        return self.sheet.height

    # size X pos
    @property
    def sizeXPos(self):
        return (-(-self.sheet.width // self.subSizeXPix))
    # size Y pos
    @property
    def sizeYPos(self):
        return (-(-self.sheet.height // self.subSizeYPix))

    # size pix variable
    @property
    def sizePix(self):
        return (self.sizeXPix, self.sizeYPix)
    
    # size pos variable
    @property
    def sizePos(self):
        return (self.sizeXPos, self.sizeYPos)
    
    # subsize pix variable
    @property
    def subSizePix(self):
        return (self.subSizeXPix, self.subSizeYPix)
