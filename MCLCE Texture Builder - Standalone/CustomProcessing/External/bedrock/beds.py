from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global

class beds(Custom.Function):
    def createImage(self):
        bedColors = [
            "black",
            "gray",
            "silver",
            "blue",
            "brown",
            "cyan",
            "green",
            "orange",
            "purple",
            "magenta",
            "red",
            "light_blue"
            "lime",
            "pink",
            "yellow",
            "white",
        ]

        stableImage = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
        colorImage = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
        bedsFound = 0
        for currColor in bedColors: # for every bed color
            image = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
            # note that this message WILL tolerate image resizing, meaning if images have different sizes there will be sloppy results
            # if only one bed is found, the whole thing will bed sent over to both textures
            try:
                image = rd.readImageSingular(self.wiiuName, f"bed_{currColor}", self.type, ut.size(16))
            except rd.notFoundException:
                continue
            except rd.notExpectedException:
                Global.notExpectedErrors.append(self.wiiuName)
                continue
            except rd.notx16Exception as err: # resizes image
                Global.incorrectSizeErrors.append(self.wiiuName)
                image = err.getImage().resize((ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet))

            # once everything is formatted right and working
            bedsFound += 1
            image = image.convert("RGBA")

            # don't run for the first bed, just copy it over to the stable image
            if (bedsFound == 1):
                stableImage = image
                continue

            # check for stability in all pixels (of each bed)
            i = 0
            while (i < ut.singularSizeOnTexSheet): # for pixels
                j = 0
                while (j < ut.singularSizeOnTexSheet):
                    if (stableImage.getpixel((i, j))[3] == 0): 
                        j += 1
                        continue # if both pixels are clear

                    if (image.getpixel((i, j)) != stableImage.getpixel((i, j))): # if pixels are different, then,
                        if (self.wiiuName == "bed_colorless"):
                            stableImage.putpixel((i, j), (0, 0, 0, 0)) # subtract them from the stable image
                        elif (self.wiiuName == "bed_colored"):
                            if (bedsFound > 1): # starting on cycle 2 (after the stable image has been set)
                                # turns the pixel gray
                                # this function has the potential to give undesirable results simply due the nature of the bed texture in MC bedrock
                                currPixel = image.getpixel((i, j)) 
                                lightness = int(currPixel[0] * 299/1000 + currPixel[1] * 587/1000 + currPixel[2] * 114/1000)
                                colorImage.putpixel((i, j), (lightness, lightness, lightness)) # add them to the color image
                    j += 1 
                i += 1

        # functions based on amount of beds found
        if (bedsFound == 0): # bed textures couldn't be determined
            if (Global.errorMode == "error"): # place error texture
                raise rd.notExpectedException()
            elif (Global.errorMode == "replace"): # use the wiiu texture
                raise rd.notFoundException()
        elif (bedsFound == 1): # if only 1 bed was found, we have no comparison to go off of, so it has to be the same texture as a whole
            if (Global.errorMode == "error"):
                raise rd.notExpectedException()
            elif (Global.errorMode == "replace"):
                colorImage = stableImage.copy()
                # makes sure to turn the image grayscale (ignoring alphas)
                i = 0
                while (i < ut.singularSizeOnTexSheet):
                    j = 0
                    while (j < ut.singularSizeOnTexSheet):
                        currPixel = colorImage.getpixel((i, j)) 
                        if (currPixel[3] == 0):
                            j += 1
                            continue
                        lightness = int(currPixel[0] * 299/1000 + currPixel[1] * 587/1000 + currPixel[2] * 114/1000)
                        colorImage.putpixel((i, j), (lightness, lightness, lightness)) # add them to the color image
                        j += 1
                    i += 1

        # return statements
        if (self.wiiuName == "bed_colorless"):
            return stableImage
        elif (self.wiiuName == "bed_colored"):
            return colorImage