from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global

class map_filled_overlay(Custom.Function):
    def createImage(self):
        # try to get map images
        filledImage = rd.readImageSingular(self.wiiuName, "map_filled", self.type, ut.size(16))
        filledImage = filledImage.convert("RGBA")
        emptyImage = rd.readImageSingular(self.wiiuName, "map_empty", self.type, ut.size(16))
        emptyImage = emptyImage.convert("RGBA")
        finalImage = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")

        # runs through the texture for the filled image and gets differences
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
        return finalImage