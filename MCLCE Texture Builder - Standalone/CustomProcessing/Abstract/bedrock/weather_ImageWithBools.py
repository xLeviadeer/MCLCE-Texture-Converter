from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
from typing import Union, Self
import os
import time

# class to determine images with bools
class ImageWithBools():
    # image : Image
    # nested : nested List
    # validBount : int

    def __init__(self, image:Image, *, validBound:int=None) -> None:
        """
        Description:
            holds/finds data about image regarding the image itself and it represented as booleans
        ---
        Arguments:
            - image : Image <>
            - validBound : Integer <None>
                - determines the bounds which this class will count as valid for conversion between nested and singular lists
                - None: equal to the image's size bounds
                - otherwise a size tuple of length 2
        ---
        Other:
            - holds the image
            - holds a value, "nested", which is the image as booleans where true is non-alpha and false is alpha
        """

        # set image
        if isinstance(image, Image):
            self.image = image
        else:
            Global.endProgram(f"ImageWithBool's value, image, was not a SizingImage: {type(image)}")

        # set valid bounds for the bools
        if (validBound == None):
            self.validBound = self.width
        else: # validBounds was set
            if isinstance(validBound, int): # check it's the correct format
                self.validBound = validBound
            else:
                Global.endProgram(f"ImageWithBool's value, validBound, was not a size/position tuple: {type(validBound)}")

        # image as bools
        self.setTextureBools()
        
    def setTextureBools(self, lst:list=None) -> None:
        """
        Description:
            Sets the texture bools from the current image; true will be non-alpha pixels
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

            # for every pixel in the image, build part of the array based on transparency 
            def buildImageAsBools(pixel, x, y, image, args):
                # if it's a new y row, create new
                if (x == 0):
                    self.nested.append([])

                # find the if the pixel is alpha and append it
                pixelBool = (pixel[3] > 0)
                self.nested[y].append(pixelBool)

            # run through pixels and execute the function
            ut.forEveryPixel(self.image, buildImageAsBools)

        elif isinstance(lst, list):
            if all((isinstance(value, list) 
                    and (all(isinstance(subValue, bool) for subValue in value))
                    ) for value in lst): # nested list
                self.nested = lst
            elif all(isinstance(value, bool) for value in lst): # singular list
                self.nested = self._convertSingleListToNested(lst)
            else:
                Global.endProgram("lst list format wasn't correct (must be all ints or all lists of ints)")
        else:
            Global.endProgram("lst was not a list")

    def _convertNestedListToSingle(self, lst:list) -> list[bool]:
        """
        Description:
            internal function for converting a nested list to a singular list
        ---
        Arguments:
            - lst : List <>
        """

        # for each sub-list, extend it to a new list
        newLst = []
        for sublst in lst:
            # check if sublist is correct length
            if (len(sublst) != self.validBound):
                Global.endProgram(f"the nested list contained a list not of length {self.validBound} when attempting to convert to singular list, meaning it is not rectangular")
            
            # extend new list
            newLst.extend(sublst)
        
        # return
        return newLst

    def convertNestedListToSingle(self, lst:list) -> list[bool]:
        """
        Description:
            converts a nested list to a singular list
        ---
        Arguments:
            - lst : List <>
        """

        # check format
        if (isinstance(lst, list) 
            and all((isinstance(value, list) 
            and (all(isinstance(subValue, bool) for subValue in value))
            ) for value in lst)) == False:
            Global.endProgram("lst was not correctly formatted when attempting to convert nested list to singular list")

        # run
        return self._convertNestedListToSingle(lst)

    def _convertSingleListToNested(self, lst:list) -> list[list[bool]]:
        """
        Description:
            internal function for converting a singular list to a nested list
        ---
        Arguments:
            - lst : List <>
        """

        # ensure the list is of the right size
        if (len(lst) % self.validBound) != 0:
            Global.endProgram("the singular list had remainder when attempting to convert to nested list, meaning it is not rectangular")

        # for each value, split it into a new nested list
        newLst = []
        i = 0
        while i < len(lst):
            newLst.append(lst[i:(i + self.validBound)])
            i += self.validBound

        # return
        return newLst

    def convertSingleListToNested(self, lst:list) -> list[list[bool]]:
        """
        Description:
            converts a single list to a nested list
        ---
        Arguments:
            - lst : List <>
        """

        # check format (lst is a list, all elements are integers)
        if (isinstance(lst, list) and all(isinstance(value, bool) for value in lst)) == False:
            Global.endProgram("lst was not correctly formatted when attempting to convert singular list to nested list")

        # run
        return self._convertSingleListToNested(lst)

    def getBoolsSingular(self) -> list[bool]:
        """
        Description:
            gets the bools as a singular list
        ---
        Returns:
            - singular list of each pixel in the image as a bool
        """

        return self._convertNestedListToSingle(self.nested)
    
    def getBoolsNested(self) -> list[list[bool]]:
        """
        Description:
            gets the bools as a nested list
        ---
        Returns:
            - nested list of each pixel in the image as a bool by it's x,y coordinates
        """

        return self.nested

    def _addUsedValues_additionStatement(self, xPos:int, yPos:int) -> None:
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

        # paste in
        self.nested[yPos][xPos] = True # doesn't matter if already true

    def addUsedValues(self, valueOrValues:Union[int, list[int], tuple[int]]) -> None:
        """
        Description:
            adds a value or multiple values to the used values for this section
        ---
        Arguments:
            - valueOrValues : Integer, List of Integers or a Tuple of Integers <>
        ---
        Returns:
            - nothing, updates existing values
        """

        # -- value validity --
        
        # if int, convert to tuple
        if isinstance(valueOrValues, int):
            valueOrValues = (valueOrValues,)
        
        # if list check validity
        elif ((not (isinstance(valueOrValues, list) or isinstance(valueOrValues, tuple))) 
            and all(isinstance(value, int) for value in valueOrValues)):
            Global.endProgram(f"provided valueOrValues is/are not an int/list or tuple of ints: {type(valueOrValues)}")

        # -- update nested --

        # for every value in the values, set the corresponding value to true
        for num in valueOrValues:
            numX = (num % self.width)
            numY = (num // self.width)
            self._addUsedValues_additionStatement(numX, numY)

    def _pasteUsedValues_additionStatement(self, xPos:int, yPos:int) -> None:
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

        # set overall value in nested to true
        self.nested[yPos][xPos] = True 

    def pasteUsedValues(self, valuesNested:list[list[int]], pos:tuple[int]) -> None:
        """
        Description:
            pastes a nested list of values onto another nested list of values
        ---
        Arguments:
            - valuesNested : nested List <>
                - must be a nested list (list of lists which contain only ints)
        ---
        Returns:
            - nothing, updates exisiting values
        """

        # check nested values
        if not (isinstance(valuesNested, list)
            and all(isinstance(value, list) for value in valuesNested)
            and all(all(isinstance(item, int) for item in value) for value in valuesNested)):
            Global.endProgram("provided valuesNested isn't of the correct format; must be a nested list")
        if not all((len(value) == len(valuesNested[0])) for value in valuesNested):
            Global.endProgram("all nested lists weren't the same length")

        # check pos
        if not ut.tupleIsPosition(pos):
            Global.endProgram("the provided pos is not a position tuple")

        # starting at the pos and moving fo the size of the valuesNested
        overallY = pos[1]
        while overallY < (len(valuesNested) + pos[1]): # for size of valuesNested
            if (0 <= overallY < self.height): # only if within bounds of the paste array
                overallX = pos[0]
                while overallX < (len(valuesNested[0]) + pos[0]): # for the size of valuesNested[0]
                    if (0 <= overallX < self.width): # only if in the bounds
                        relativeY = overallY - pos[1]
                        relativeX = overallX - pos[0]
                        if (valuesNested[relativeY][relativeX] == True): # if the valuesNested value is true
                           self._pasteUsedValues_additionStatement(overallX, overallY)
                    overallX += 1
            overallY += 1

    def paste(self, imageWithBools:Self, pos:tuple[int]=(0,0)) -> None:
        """
        Description:
            pastes an ImageWithBools (parent or child) onto this WeatherSection in terms of both visual imagery and nesting and bracket randomization
        ---
        Arguments:
            - imageWithBools : ImageWithBools <>
            - pos : Tuple <(0, 0)>
                - must be a position tuple
        ---
        Returns:
            - nothing, modifies the original image and other data
        """

        # check image
        if not isinstance(imageWithBools, ImageWithBools):
            Global.endProgram(f"provided value for variable imageWithBools is not type ImageWithBools: {type(imageWithBools)}")
        
        # check pos
        if not ut.tupleIsPosition(pos):
            Global.endProgram(f"provided value for variable pos is not a tuple of length 2 with only integers: {type(pos)}")

        # paste boolean pattern
        self.pasteUsedValues(imageWithBools.nested, pos)

        # paste actual image
        self.image.alpha_composite(imageWithBools.image, pos, doResize=False)

    def alreadyUsed(self, index:int) -> bool:
        """
        Description:
            checks if a value by index is true in self.nested
        ---
        Arugments:
            - index : Integer <>
        ---
        Returns:
            - boolean, true if the value at the index is true, false if it's false
        """

        # type check
        if not isinstance(index, int):
            Global.endProgram(f"the value supplied for variable index was not an int: {type(index)}")

        # get value
        x = index % self.width
        y = index // self.width
        return self.nested[y][x]

    # --- Tests ---

    @ut.test
    def _visualizeUsedAsImage_trueCheck(self, xPos:int, yPos:int):
        return (self.nested[yPos][xPos] == True)

    @ut.test
    def visualizeUsedAsImage(self):
        # create an image to the size of the section and turn all unpastable pixels black and the rest white
        testImage = ut.blankImage(self.width, self.height, doResize=False)
        def testFunc(pixel, x, y, image, args):
            if (self._visualizeUsedAsImage_trueCheck(x, y)):
                return (0, 0, 0, 255)
            else:
                return (255, 255, 255, 255)
        testImage = ut.forEveryPixel(testImage, testFunc)
        
        # save to output for viewing
        folder = f"{Global.outputPath}\\test_weather"
        if (not os.path.exists(folder)):
            os.mkdir(folder)
        testImage.save(f"{folder}\\step_{Global.iter}.png", "PNG")
        print(f"successfully wrote step_{Global.iter}")
        Global.iter += 1

    # image height
    @property
    def width(self):
        return self.image.width

    # image width
    @property
    def height(self):
        return self.image.height

    # image size
    @property
    def size(self):
        return self.image.size

    # length of the image bools (amount of pixels)
    def __len__(self):
        return len(self._convertNestedListToSingle(self.nested))
