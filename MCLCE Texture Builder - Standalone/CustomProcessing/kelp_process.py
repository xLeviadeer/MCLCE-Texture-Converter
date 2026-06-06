from CustomProcessing import Custom
import TextureLibs.SizingImage as si
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from multiprocessing import Pool
import TextureLibs.Global as Global

class kelp_process(Custom.Function):
    def generateBlockOnImage(self, image, pos, color):
        # pastes of block of the multiplier size on the image
        image.paste(
            ut.blankImage(
                ut.size(si.getMultiplier()), 
                color=color, 
                doResize=False
            ), 
            pos, 
            doResize=False
        ) 
        return image

    def ifPositionIsMultiplierModuloLocation(self, pos):
        multiplier = si.getMultiplier()
        return ((pos[0] % multiplier) == 0) and ((pos[1] % multiplier) == 0)

    def processKelpSubImage(self, image):
        alphaImage = ut.blankImage(image.size, doResize=False)
        image = image.convert("RGBA")
        averageColor = ut.findAverageColor(image, 0)

        i = 0
        while (i < image.width):
            j = 0
            while (j < image.height):
                if (not self.ifPositionIsMultiplierModuloLocation((i, j))): # if it's not a valid location then skip
                    j += 1
                    continue
                # collect pixel values to average
                class wrapper(): # wraps variables
                    lengthToInclude = 3 # amount of pixels to average
                    grabRadius = 2 * si.getMultiplier() # grabRadius will be 2 for x16 and size up with the multiplier
                    grabCount = 0
                    x = i - grabRadius
                    y = j - grabRadius
                    def incr(self): # incrementing logic
                        if (self.x == (i + self.grabRadius)):
                            self.y += 1
                            self.x = i - self.grabRadius
                        else:
                            self.x += 1
                    def collectAndAveragePixels(self):
                        totalPixel = [0] * 4
                        while (self.x, self.y) != ((i + self.grabRadius), (j + self.grabRadius)):
                            if (
                                (self.x > image.width - 1) # right edge
                                or (self.y > image.height - 1) # bottom edge
                                or (self.x < 0) # left edge
                                or (self.y < 0) # top edge
                                ): # checks if the prospective pixel will be out of bounds
                                self.incr()
                                continue
                            if ((self.x, self.y) == (i, j)): # checks for middle pixel
                                self.incr()
                                continue
                            checkPixel = image.getpixel((self.x, self.y)) # get check pixel
                            if (checkPixel[3] == 0): # if the pixel is alpha
                                self.incr()
                                continue

                            # addition
                            b = 0
                            while b < len(checkPixel):
                                if (b >= self.lengthToInclude): # break if above pixels to include (sets them to 0)
                                    break
                                totalPixel[b] += checkPixel[b]
                                b += 1

                            # last (increment)
                            self.grabCount += 1 # counts every pixel that was successfully grabbed
                            self.incr()

                        # find the average
                        if (self.grabCount == 0):
                            return averageColor
                        # works as an else case for average pixels
                        c = 0
                        while c < len(totalPixel):
                            totalPixel[c] = round(totalPixel[c] / self.grabCount) # average each value
                            c += 1
                        return tuple(totalPixel) # return edited
                alphaImage = self.generateBlockOnImage(alphaImage, (i, j), wrapper().collectAndAveragePixels())

                j += 1
            i += 1

        # set alpha sections to alpha
        def setAsAlpha(currPixel, i, j, image, args):
            return tuple(list(currPixel)[:3] + [0])
        newImage = ut.forEveryPixel(alphaImage, setAsAlpha)
        # composite kelp on top
        newImage.alpha_composite(image, (0, 0), doResize=False)

        return newImage

    def deconstructImage(self, image):
        images = []

        y = 0
        while y < image.height:
            images.append(image.crop((0, y, ut.singularSizeOnTexSheet, (y + ut.singularSizeOnTexSheet)), doResize=False)) # adds image to list
            y += ut.singularSizeOnTexSheet
        return images
        
    def reconstructImage(self, images, image):
        y = 0
        while y < image.height:
            image.paste(images[(y // ut.singularSizeOnTexSheet)], (0, y), doResize=False)
            y += ut.singularSizeOnTexSheet
        return image

    def complexProcess(self, image):
        images = self.deconstructImage(image)
        amountOfParallelProcesses = 20
        with Pool(amountOfParallelProcesses) as pool:
            images = pool.map(self.processKelpSubImage, images)
        image = self.reconstructImage(images, ut.blankImage(image.size, doResize=False))
        return image

    def simpleProcess(self, image):
        # for every image in the deconstruction
        images = self.deconstructImage(image)
        for i in range(len(images)):
            # find the average color for this subimage
            currAverageColor = ut.findAverageColor(images[i], 0)

            # create background image
            bgImage = ut.blankImage(images[i].size, color=currAverageColor, doResize=False)

            # set kelp onto background and set images[i]
            bgImage.alpha_composite(images[i])
            images[i] = bgImage

        # return reconstructed image
        image = self.reconstructImage(images, ut.blankImage(image.size, doResize=False))
        return image

    def createImage(self, args):
        # determines which texture to use
        readName = args[0]
        if (not isinstance(readName, str)):
            Global.endProgram("kelp_process was not supplied a valid reading name")
            return
        type = "block" + ("" if (Global.inputGame == "java") else "s") # sets the type based on game
        image = rd.readImageSingular(self.wiiuName, readName, type, ut.size(16, 320))

        # replaces all alpha pixels in the kelp with generalized alpha pixels
        image = image.convert("RGBA")

        # use either simple or complex processing
        if (Global.useComplexProcessing == True):
            return self.complexProcess(image)
        elif (Global.useComplexProcessing == False):
            return self.simpleProcess(image)
        else:
            Global.endProgram("the kelp_process image process mode could not be decided because Global.useComplexProcessing was not set")
