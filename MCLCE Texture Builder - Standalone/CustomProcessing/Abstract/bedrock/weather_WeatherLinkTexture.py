from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
from typing import Self

# custom class imports
from CustomProcessing.Abstract.bedrock.weather_ImageWithBools import ImageWithBools

# raindrop link image texture class
class WeatherLinkTexture(ImageWithBools):
    def __init__(self, image:Image) -> None:
        """
        Description:
            holds/finds data about a singular raindrop texture
        ---
        Arguments:
            - image : Image <>
        ---
        Other:
            - modifies nested to not be able to be able to pasted onto; pasting for this class will result in pasting onto the padding map
            - includes values for supporting "real" size
            - stores a value of the padding shape of the texture
        """
        
        # empty values, will always be set in setTexturesBools(None)
        self.__firstRowWithPixels = None
        self.__lastRowWithPixels = None
        self.__firstColumnWithPixels = None
        self.__lastColumnWithPixels = None

        # define image and set the texture bools
        super().__init__(image)

    def setTextureBools(self, lst:list=None) -> None:
        """
        Description:
            Sets the texture bools from the current image
        ---
        Arguments:
            - lst : List or 2 layer multidimensional List <None>
                - sets the texture's image as bools list
                - None: get from image
                - Other: set to input
        """

        if (lst == None): # generate from image
            # clear imageAsBools
            self.nested = []
            
            # set values up
            self.__firstRowWithPixels = None
            self.__lastRowWithPixels = -1
            self.__firstColumnWithPixels = None
            self.__lastColumnWithPixels = -1

            # for every pixel in the image, build part of the array based on transparency 
            def buildImageAsBools(pixel, x, y, image, args):
                # if it's a new y row, create new
                if (x == 0):
                    self.nested.append([])

                # find the if the pixel is alpha and append it
                pixelBool = (pixel[3] > 0)
                self.nested[y].append(pixelBool)

                # -- find rows, columns and starting pixel --

                # must be targeting a real pixel
                if (pixelBool == True):
                    # find the first row with pixels
                    if (self.__firstRowWithPixels == None) or (self.__firstRowWithPixels > y):
                        self.__firstRowWithPixels = y

                    # find the first column with pixels
                    if (self.__firstColumnWithPixels == None) or (self.__firstColumnWithPixels > x):
                        self.__firstColumnWithPixels = x

                    # set the last row if the stored row is smaller
                    if (self.__lastRowWithPixels < y):
                        self.__lastRowWithPixels = y

                    # set the last column if the stored column is smaller
                    if (self.__lastColumnWithPixels < x):
                        self.__lastColumnWithPixels = x

            # set values if they are left empty (the texture must be blank for this to happen)
            if (self.__firstRowWithPixels == None): self.__firstRowWithPixels = 0
            if (self.__lastRowWithPixels == -1): self.__lastRowWithPixels = 0
            if (self.__firstColumnWithPixels == None): self.__firstColumnWithPixels = 0
            if (self.__lastColumnWithPixels == -1): self.__lastColumnWithPixels = 0

            # run through pixels and execute the function
            ut.forEveryPixel(self.image, buildImageAsBools)
            self._setPaddingBools()
        elif isinstance(lst, list):
            if all((isinstance(value, list) 
                    and (all(isinstance(subValue, bool) for subValue in value))
                    ) for value in lst): # nested list
                self.nested = lst
                self._setPaddingBools()
            elif all(isinstance(value, bool) for value in lst): # singular list
                self.nested = self.__convertSingleListToNested(lst)
                self._setPaddingBools()
            else:
                Global.endProgram("lst list format wasn't correct (must be all ints or all lists of ints)")
        else:
            Global.endProgram("lst was not a list")

    def _setPaddingBools(self):
        """
        Description:
            finds the padding shape of the current self.nested
        ---
        Returns:
            - nothing, updates existing values
        """

        # constant intersection point
        INTERSECTPOINT = ((self.width - 1), (self.height - 1))

        # clear/originally set padding to the size of this image
        self.padding = [[False for _ in range(self.width)] for _ in range(self.height)]

        # check every pixel position for interception
        for y in range(len(self.nested)):
            for x in range(len(self.nested[0])):
                # skip the first pixel since it doesn't matter what it is, it can't end up outside of itself-
                # -(this wouldn't be true if intersect was anything else)
                if (x == 0) and (y == 0): continue

                # check if the current nested value is true
                if (self.nested[y][x] == True):
                    # paste to the inverse position; this because the inverse (opposite of the total, which the intersect is the total)- 
                    # -position will paste the nested to the position where it will intersect with the intersection point
                    posOutOfIntersect = ((INTERSECTPOINT[0] - x), (INTERSECTPOINT[1] - y))
                    self.pasteUsedValues(self.nested, posOutOfIntersect)

    def _addUsedValues_additionStatement(self, xPos, yPos) -> None:
        """
        Description:
            the addition statement used for addUsedValues; helps to making overriding this function easier
        ---
        Arguments:
            - xPos : Integer <>
                - where to place addition pixel x
            - yPos : Integer <>
                - where to place additional pixel y
        ---
        Returns
            - nothing, updates exisitng values 
        """
        
        self.padding[yPos][xPos] = True

    def _pasteUsedValues_additionStatement(self, xPos, yPos) -> None:
        """
        Description:
            the addition statement used for pasteUsedValues; helps to making overriding this function easier
        ---
        Arguments:
            - xPos : Integer <>
                - where to place addition pixel x
            - yPos : Integer <>
                - where to place additional pixel y
        ---
        Returns
            - nothing, updates exisitng values 
        """

        self.padding[yPos][xPos] = True

    def paste(self, imageWithBools:Self, pos:tuple[int]=(0,0)) -> None:
        raise NotImplementedError("paste cannot be used on WeatherLinkTexture class; nested cannot be updated for WeatherlinkTexture")

    def getRealImage(self) -> Image:
        """
        Description:
            Gets the real image aka gets the image where it's "canvas clipped"; where there is no whitespace on the edges
        ---
        Return:
            - Image without no whitespace around the edges
        """

        return self.image.crop(self.startingPixelPos + self.endingPixePos, doResize=False)

    # --- Tests ---

    @ut.test
    def _visualizeUsedAsImage_trueCheck(self, xPos, yPos):
        return (self.padding[yPos][xPos] == True)

    # read height/width/size (1 offset like how len works)
    @property
    def realWidth(self):
        return (self.__lastColumnWithPixels - self.__firstColumnWithPixels) + 1
    @property
    def realHeight(self):
        return (self.__lastRowWithPixels - self.__firstRowWithPixels) + 1
    @property
    def realSize(self):
        return (self.realWidth, self.realHeight)
    
    # padding size (will always be the same as the image size anyway)
    @property
    def paddingWidth(self):
        return self.width
    @property
    def paddingHeight(self):
        return self.height
    @property
    def paddingSize(self):
        return self.size

    # starting/ending pixel pos
    @property
    def startingPixelPos(self):
        return (self.__firstColumnWithPixels, self.__firstRowWithPixels)
    @property
    def endingPixePos(self):
        return ((self.__firstColumnWithPixels + self.realWidth), (self.__firstRowWithPixels + self.realHeight))
