from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global

class map_filled_overlay(Custom.Function):
    def createImage(self):
        # try to read the filled map
        filledImage = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
        foundFilledImage = False
        try:
            filledImage = rd.readImageSingular(self.wiiuName, "map_filled", self.type, ut.size(16))
            foundFilledImage = True
        except rd.notFoundException:
            raise rd.notFoundException()
        except rd.notExpectedException:
            raise rd.notExpectedException()
        except rd.notx16Exception as err: # resizes image
            Global.incorrectSizeErrors.append(self.wiiuName)
            filledImage = err.getImage().resize((ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet))
            foundFilledImage = True
        filledImage.convert("RGBA")

        # try to read the empty image
        emptyImage = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
        foundEmtpyImage = False
        try:
            emptyImage = rd.readImageSingular(self.wiiuName, "map_empty", self.type, ut.size(16))
            foundEmtpyImage = True
        except rd.notFoundException:
            raise rd.notFoundException()
        except rd.notExpectedException:
            raise rd.notExpectedException()
        except rd.notx16Exception as err: # resizes image
            Global.incorrectSizeErrors.append(self.wiiuName)
            emptyImage = err.getImage().resize((ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet))
            foundEmtpyImage = True
        emptyImage.convert("RGBA")

        finalImage = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
        if ((foundFilledImage) and (foundEmtpyImage)): # all images found
            # gives out an interpretted image
                # if you don't design moronic textures this gives good output

            # runs through the texture for the filled image
            i = 0
            while (i < ut.singularSizeOnTexSheet):
                j = 0
                while (j < ut.singularSizeOnTexSheet):
                    currPixel = filledImage.getpixel((i, j))
                    if (currPixel[3] == 0): # skips for alpha pixels
                        j += 1 
                        continue
                    
                    if (currPixel != emptyImage.getpixel((i, j))):
                        # invert black and white values only
                        red = currPixel[0]
                        green = currPixel[1]
                        blue = currPixel[2]
                        finalImage.putpixel((i, j), (int(255 - ((green + blue) / 2)), int(255 - ((red + blue) / 2)), int(255 - ((red + green) / 2)), currPixel[3]))

                    j += 1
                i += 1
        elif (foundFilledImage): # only integral image found
            # pastes image as is
            finalImage = filledImage
        else:
            # errors
            if (Global.errorMode == "replace"):
                raise rd.notFoundException()
            elif (Global.errorMode == "error"):
                raise rd.notExpectedException()

        return finalImage