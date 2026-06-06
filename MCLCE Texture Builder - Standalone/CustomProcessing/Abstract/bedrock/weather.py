from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Global as Global
from CodeLibs.Path import Path
import TextureLibs.SizingImage as si
from CodeLibs import Logger as log
from CodeLibs.Logger import print
import random

# custom class imports
from CustomProcessing.Abstract.bedrock.weather_WeatherSection import WeatherSection
from CustomProcessing.Abstract.bedrock.weather_WeatherLinkTexture import WeatherLinkTexture

class weather(Custom.Function):    
    def getLinkImages(self, useComplex:bool):
        # --- obtain raindrop textures ---

        # read weather image
        weatherSheet = SheetExtractor(
            Path("weather"), 
            si.convertTuple(ut.size(4)), 
            self.wiiuName, 
            "environment", 
            (32, 32)
        )

        # extract raindrops from sheet
        linkDrops = []
        tallestTextureHeight = -1
        i = 0
        while i < weatherSheet.sizeXPos:
            # adjust for rain/snow texture size
            heightPos = 0
            chunkSize = (1, 1)
            if (self.wiiuName == "rain"):
                heightPos = 1
                chunkSize = (1, 4)

            # extract raindrops into list of rain drop link textures
            currTexture = weatherSheet.extract(
                (i, heightPos), 
                chunkSize, 
                doResize=False
            )
            if (useComplex == True): currTexture = WeatherLinkTexture(currTexture) # if complex, cast into WeatherLinkTexture
            linkDrops.append(currTexture)

            # only if complex
            if (useComplex == True):
                # find tallest height
                if (currTexture.realHeight > tallestTextureHeight):
                    tallestTextureHeight = currTexture.realHeight

            # increment
            i += 1

        return {
            "linkDrops": linkDrops,
            "tallestTextureHeight": tallestTextureHeight
        }

    def complexProcess(self):
        # constants (not all caps because it would be too hard to read)
        AmountOfSections = 8

        # --- obtain raindrop textures ---

        dataDict = self.getLinkImages(useComplex=True)
        linkDrops = dataDict["linkDrops"]
        tallestTextureHeight = dataDict["tallestTextureHeight"]

        # --- create raindrop texture ---

        # wiiu image size
        wiiuImageWidth = 64
        wiiuImageHeight = 256

        # section height
        sectionHeight = wiiuImageHeight / AmountOfSections
        if (sectionHeight % 1) != 0: # check if the division isn't an integer result (value with no decimals)
            Global.endProgram(f"AmountOfSections ({AmountOfSections}) doesn't result in an integer pixel height for sections. Choose a different amount of sections.")
        sectionHeight = int(sectionHeight) # integer cast since we know it's an int

        # blank wiiu image
        newImage = ut.blankImage(wiiuImageWidth, wiiuImageHeight)

        # split the blank image into the amount of sections with correct oversizing
        i = 0
        while i < AmountOfSections:
            print(f"section {i}/{AmountOfSections}", log.CUSTOMWEATHER)

            # append to sections
            currSection = WeatherSection(
                newImage.crop(( # the imageHeight will be cropped down further in the method for adding raindrops
                    0,
                    (i * sectionHeight),
                    wiiuImageWidth,
                    ((i * sectionHeight) + sectionHeight + si.deconvertInt(tallestTextureHeight))
                ))
            )
            
            # add drops to the image
            currSection.addRainDropsToImage(
                linkDrops, 
                tallestTextureHeight, 
                WeatherSection.getRandomAmountOfRaindrops(), 
                (i == (AmountOfSections - 1 )))

            # add the completed section to the newImage
            newImage.alpha_composite(currSection.image, (0, (i * sectionHeight)))
        
            # increment
            i += 1

        # return the completed image
        return newImage
    
    def findPositionsFromSampleImage(self):
        # read image (not a wiiu texture, lol, but this works)
        image = rd.readWiiuImage(inWiiuAbstract=False, name="drop_samples", doResize=False)
        
        # for every pixel in the image, determine if the pixel is black (only will ever react to true black pixels)
        positions = []
        def findPositionsFromBlackPixels(pixel, x, y, image, args):
            r, g, b, a = pixel
            if (r == 0) and (g == 0) and (b == 0) and (a == 255):
                positions.append(si.convertTuple((x, y)))
        ut.forEveryPixel(image, findPositionsFromBlackPixels)

        # return
        return positions

    def simpleProcess(self):

        # -- get link images --
        linkDrops = self.getLinkImages(useComplex=False)["linkDrops"]

        # -- get positional data --

        # positions to put raindrops in (pull from drop_sampler image)
        positions = self.findPositionsFromSampleImage()

        # -- paste a random raindrop to each position --

        # blank, pastable, final image
        pasteImage = ut.blankImage(ut.size(64, 256))

        # for every position
        for position in positions:
            # get a random drop
            currDrop = linkDrops[random.randint(0, (len(linkDrops) - 1))]

            # paste to position
            pasteImage.alpha_composite(currDrop, position, doResize=False)

        # return final
        return pasteImage

    def createImage(self):
        # use either simple or complex processing
        if (Global.useComplexProcessing == True):
            return self.complexProcess()
        elif (Global.useComplexProcessing == False):
            return self.simpleProcess()
        else:
            Global.endProgram("the weather image process mode could not be decided because Global.useComplexProcessing was not set")