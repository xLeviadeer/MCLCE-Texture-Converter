from xLPyBasics.RandomAPI import Random, NoRandomValuesAvailableException

from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global
import TextureLibs.TextureUtility as ut
from typing import Union, Self
from CodeLibs import Logger as log
from CodeLibs.Logger import print

# custom class imports
from CustomProcessing.Abstract.bedrock.weather_ImageWithBools import ImageWithBools
from CustomProcessing.Abstract.bedrock.weather_WeatherLinkTexture import WeatherLinkTexture

# class for managing images and their associated pasting size
class WeatherSection(ImageWithBools):
    # class variables
    RaindropsPerSectionMin = 4
    RaindropsPerSectionMax = 7
    # raindrops per section average is 5.5, 5.5 * 8 is 44

    # nested : nested list
    # random : Bracket Random
    # validBound : int
    # __min : int
    # __max : int

    def __init__(self, image:Image):
        """
        Description
            holds/finds data about a section image and it's pastable area as well as randomization data
        ---
        Arguments:
            - image : Image <>
        ---
        Other:
            - holds a bracket random which will mirror all values that have been used in nested
            - holds min/max values to support the bracket random
        """

        # -- overview of how the order of setting values works --
        # super class __init__ is ran
        # - image is set
        # - valid bound is set
        # super class runs child class setTextureBools
        # - min and max are set based off image
        # - nested list is set (cleared)
        # - random bracket is set

        # run super
        super().__init__(image)

    def setTextureBools(self, lstOrBracketRandom:list=None):
        """
        Description:
            Sets the texture bools from the current image; true will be non-alpha pixels
        ---
        Arguments:
            - lstOrBracketRandom : List, 2 layer multidimensional List or BracketRandom.Random object <None>
                - sets the texture's image as bools list and bracket random
                - None: get from image
                - Other: set to provided input
        """

        # type check for lstOrBracketRandom
        if (lstOrBracketRandom == None): # generate from image
            # __min and __max (assumes image has just been set in __init__)
            self.__min = 0
            self.__max = (self.width * self.height) - 1

            # -- set nested --

            super().setTextureBools()

            # -- mirror added values to random --
            self.random = Random(
                self.__min, 
                self.__max,
                self._convertBoolListToIntList(
                    self._convertNestedListToSingle(self.nested)
                )
            )
        elif isinstance(lstOrBracketRandom, Random): # bracket random
            # set random
            self.random = lstOrBracketRandom

            # set nested
            self.nested = self._convertSingleListToNested(
                self._convertIntListToBoolList(
                    lstOrBracketRandom.getBracketsAsList()
                )
            )
        elif isinstance(lstOrBracketRandom, list):
            if all((isinstance(value, list)
                    and (all(isinstance(subValue, bool) for subValue in value))
                    ) for value in lstOrBracketRandom): # nested list
                # set nested
                self.nested = lstOrBracketRandom

                # set bracket random
                self.random = Random(
                    self.__min, 
                    self.__max, 
                    self._convertBoolListToIntList(
                        self._convertNestedListToSingle(lstOrBracketRandom)
                    )
                )
            elif all(isinstance(value, bool) for value in lstOrBracketRandom): # singular list
                # set nested
                self.nested = self._convertSingleListToNested(lstOrBracketRandom)

                # set bracket random
                self.random = Random(
                    self.__min, 
                    self.__max, 
                    self._convertBoolListToIntList(lstOrBracketRandom)
                )
            else:
                Global.stopGen("lst list format wasn't correct (must be all ints or all lists of ints)")
        else:
            Global.stopGen("lstOrBracketRandom was not a list or bracket random")

    def _convertBoolListToIntList(self, lst:list[bool]):
        """
        Description:
            interal function for converting a list of booleans to a list of integer index positions for every true value.
        ---
        Arguments:
            - lst : List <>
        ---
        Returns:
            a list of integer index posisions
        """

        intLst = []
        for i, value in enumerate(lst):
            if (value == True): intLst.append(i)
        return intLst

    def convertBoolListToIntList(self, lst:list[bool]):
        """
        Description:
            converts a list of booleans to a list of integer index positions for every true value
        ---
        Arguments:
            - lst : List <>
        ---
        Returns:
            a list of integer index posisions
        """

        if not all(isinstance(value, bool) for value in lst):
            Global.stopGen("lst was not correctly formatted when attempting to convert bool list to int list")

        return self._convertBoolListToIntList(lst)

    def _convertIntListToBoolList(self, lst:list[bool]):
        """
        Description:
            interal function for converting a list of int index positions to a list of booleans true and false where an index doesn't exist.
        ---
        Arguments:
            - lst : List <>
        ---
        Returns:
            a list of booleans
        """

        boolLst = []
        for i in range(len(self)):
            boolLst.append(i in lst)
        return boolLst

    def convertIntListToBoolList(self, lst:list[bool]):
        """
        Description:
            converts a list of int index positions to a list of booleans true and false where an index doesn't exist.
        ---
        Arguments:
            - lst : List <>
        ---
        Returns:
            a list of booleans
        """

        if not all(isinstance(value, int) for value in lst):
            Global.stopGen("lst was not correctly formatted when attempting to convert int list list to bool list")

        return self._convertIntListToBoolList(lst)

    def addUsedValues(self, valueOrValues:Union[int, list[int], tuple[int]]):
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

        # all is already checked in the super function
        super().addUsedValues(valueOrValues)

        # -- update random --

        self.random.addUsedValues(valueOrValues, raiseRandomAlreadyUsedException=False)

    def _pasteUsedValues_additionStatement(self, xPos:int, yPos:int):
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

        # run super function for nested
        super()._pasteUsedValues_additionStatement(xPos, yPos)
        
        # update bracket random
        self.random.addUsedValues(((yPos * self.width) + xPos), raiseRandomAlreadyUsedException=False)
    
    def pasteWeatherLinkTexture(self, weatherLinkTexture:WeatherLinkTexture, pos:tuple[int]=(0,0)) -> None:
        """
        Description:
            pastes a WeatherLinkTexture (parent or child) onto this WeatherSection in terms of both visual imagery and nesting and bracket randomization
        ---
        Arguments:
            - weatherLinkTexture : WeatherLinkTexture <>
            - pos : Tuple <(0, 0)>
                - must be a position tuple
        ---
        Returns:
            - nothing, modifies the original image and other data
        """

        # check image
        if not isinstance(weatherLinkTexture, ImageWithBools):
            Global.stopGen(f"provided value for variable imageWithBools is not type ImageWithBools: {type(imageWithBools)}")
        
        # check pos
        if not ut.tupleIsPosition(pos):
            Global.stopGen(f"provided value for variable pos is not a tuple of length 2 with only integers: {type(pos)}")

        # find pos adjusted for the real image starting point
        adjustedPos = ((pos[0] - weatherLinkTexture.startingPixelPos[0]), (pos[1] - weatherLinkTexture.startingPixelPos[1]))

        # paste boolean pattern
        self.pasteUsedValues(weatherLinkTexture.nested, adjustedPos)

        # paste actual image
        self.image.alpha_composite(weatherLinkTexture.getRealImage(), adjustedPos, doResize=False)

    @classmethod
    def getRandomAmountOfRaindrops(self):
        """
        Description:
            Generates a random number between the min and max raindrops per section
        ---
        Returns:
            - Integer
        """

        return Random.getRegularRandom(min=self.RaindropsPerSectionMin, max=self.RaindropsPerSectionMax)

    def addRainDropsToImage(self, dropsToUse:list, tallestRaindropHeight:int, amount:int, isLastSection:bool):
        """
        Description:
            generate an amount of provided raindrops on the image in the pastable locations
        ---
        Arguments:
            - dropsToUse : List of RainDropTextures <>
            - tallestRainDropHeight : Integer <>
            - amount : Integer <>
            - isLastSection : Boolean <>
        ---
        Returns:
            - None, modifies the image of this class does NOT return
        """

        # check if drops to use are correct
        if not all(isinstance(drops, WeatherLinkTexture) for drops in dropsToUse):
            Global.stopGen("all drops in dropsToUse aren't RainDropLinkTextures")

        # check if amount is an int
        if not isinstance(amount, int):
            Global.stopGen("amount isn't an integer")

        # incrementing down from the amount of drops
        a = amount if (isLastSection == False) else (amount - 2) # make 2 less drops on the last section
        while a > 0:
            print(f"generating drop {(amount - a) + 1}/{amount}", log.CUSTOMWEATHER, 1)

            # select a raindrop to use
            currDrop = dropsToUse[Random.getRegularRandom(min=0, max=(len(dropsToUse) - 1))]

            # copy of self for finding currDrop's vailid locations
            copySection = self.copy()

            print("completed section copy", log.CUSTOMWEATHER, 2)

            # -- add pastability (edge lines where the drop cannot be pasted) edges --

            # pastable area
            edgeLeft = 0
            edgeRight = (self.width - (currDrop.realWidth - 1))
            edgeTop = 0
            edgeBottom = (self.height - tallestRaindropHeight)

            # change edges if bottom
            if (isLastSection == True): edgeBottom -= (currDrop.realHeight - 1)

            # go through every pixel and find those out of pastability
            for x in range(self.width):
                for y in range(self.height):
                    if (not (edgeLeft <= x < edgeRight)) or (not (edgeTop <= y < edgeBottom)):
                        i = (y * self.width) + x
                        copySection.addUsedValues(i)

            print("completed pastability processing", log.CUSTOMWEATHER, 2)

            # -- apply padding shape to all true values in a copy (determine pastable pixels for the currDrop) --            

            # for every pixel in the image
            for k in range(len(self)):
                # x and y for easy access
                kX = k % self.width
                kY = k // self.width

                # make sure it's not detecting the edge lines as pixels to paste invalidity next to
                if not ((edgeLeft < kX < edgeRight) and (edgeTop < kY < edgeBottom)):
                    continue

                # if k is true in self.nested
                if self.alreadyUsed(k):

                    # add padding to the copy for the current pixel from the current drop
                    copySection.pasteUsedValues(
                        currDrop.padding, 
                        (
                            ((kX + 1) - currDrop.paddingWidth),
                            ((kY + 1) - currDrop.paddingHeight)
                        )
                    )

            print("comepleted pad processing", log.CUSTOMWEATHER, 2)
            
            # -- find position, paste and (implicitly) mirror to original -- 

            # find a random position from the copy
                # interesting tangent: when we getRandom, the pixel we chose will technically be set to true meaning it has been used
                # however, since we dont make checks about invalid pixels after this point and also before pasting, this doesn't matter
                # as we dont ever re-use this random sheet again. However, this means that visualization of the copySection must be done before this
            try:
                randomIndex = copySection.random.getRandom()
            except NoRandomValuesAvailableException: # cut the amount of drops short
                return # no more space to put drops so simply return and try drops on the next image
            randomX = randomIndex % self.width
            randomY = randomIndex // self.width

            # paste drop
            self.pasteWeatherLinkTexture(
                currDrop,
                (randomX, randomY)
            )

            print("completed final paste", log.CUSTOMWEATHER, 2)

            # increment
            a -= 1

    def copy(self) -> Self:
        """
        Description:
            returns a copy of the current WeatherSection class; saves time from processing overhead to copy rather than recreate
        ---
        Returns:
            - replica of this class
        """

        # declare
        copyCls = WeatherSection(self.image)

        # copy values
        copyCls.nested = [[boolVal for boolVal in listValue] for listValue in self.nested]
        copyCls.random = self.random.copy()
        copyCls.__min = self.__min
        copyCls.__max = self.__max
        copyCls.validBound = self.validBound

        # return
        return copyCls

    # --- Tests ---

    # checks to ensure that the values of self.random and self.nested are the same
    @ut.test
    def checkValueEquality(self):
        # get bracket random as a singular list
        brcsBoolsLst = []
        brcsLst = self.random.getBracketsAsList()
        for i in range(len(self)):
            brcsBoolsLst.append(i in brcsLst)

        # get singular list from nested
        nstSingularLst = self._convertNestedListToSingle(self.nested)

        # check equality
        equalBool = (brcsBoolsLst == nstSingularLst)
        print("Values are equal" if equalBool else "Values are NOT equal")
        if (equalBool == False): # show an equality analysis
            inequalityIndexes = []
            length = len(brcsBoolsLst) if (len(brcsBoolsLst) > len(nstSingularLst)) else len(nstSingularLst) # find largest list if inequal
            for i in range(length):
                brcValue = brcsBoolsLst[i]
                nstValue = nstSingularLst[i]
                if (brcValue != nstValue): 
                    print(f"b:{brcValue}, n:{nstValue}")
                    inequalityIndexes.append(i)
            print("showing inequality analysis by index")
            print(inequalityIndexes)
        return equalBool

    # shows a mapping of the pastable pixels using a black and white image written to the output folder
    @ut.test
    def visualizeUsedAsImage(self):
        # check equality and quit if not equal, indicating an error
        if not self.checkValueEquality():
            Global.stopGen("values were not equal, could not properly visualize")

        # run super
        super().visualizeUsedAsImage()

