from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
from CodeLibs import Logger as log
import TextureLibs.Global as Global
from CodeLibs import Logger as log
from CodeLibs.Logger import print

class horse__armor_leather(Custom.Function):
    def createImage(self):
        if (int(str.split(Global.inputVersion, ".")[1]) < 14): # check version
            print(f"using wiiu texture: {self.wiiuName}", log.WARNING)

            # gets the wiiuArr (for the right self.type correction) and gets wiiu image (starts on colorless)
            vert = 16
            hori = 0
            if (self.wiiuName == "horse armor_leather_colored"):
                vert = 13
                hori = 15
            vert *= ut.singularSizeOnTexSheet
            hori *= ut.singularSizeOnTexSheet

            return self.wiiuImage
        else: # splits the texture based on the monochrome and chrome parts of it
            image = rd.readImageSingular(self.wiiuName, "leather_horse_armor.png", self.type, ut.size(16))
            image = image.convert("RGBA")
            imageAlpha = image.getchannel("A")
            imageHSV = image.convert("HSV") # HSV image format for easy detection of color
            coloredImage = Image.new("RGBA", image.size, "#ffffff00")
            colorlessImage = Image.new("RGBA", image.size, "#ffffff00")
            # goes through each pixel to find color
            vertPos = 0
            while vertPos < image.height:
                horiPos = 0
                while horiPos < image.width:
                    alphaPixel = imageAlpha.getpixel((horiPos, vertPos))
                    HSVpixel = imageHSV.getpixel((horiPos, vertPos))
                    if (alphaPixel == 0): horiPos += 1; continue # pixel is completely alpha
                    if ((HSVpixel[1] > 0) and (self.wiiuName == "horse armor_leather_colorless")): # pixel is colored (and right key)
                        colorlessImage.putpixel((horiPos, vertPos), image.getpixel((horiPos, vertPos))) # sets the colored imagepixel to the original image pixel
                    elif ((HSVpixel[1] == 0) and (self.wiiuName == "horse armor_leather_colored")): # pixel has no color (and right key)
                        coloredImage.putpixel((horiPos, vertPos), image.getpixel((horiPos, vertPos))) # sets the colorless imagepixel to the original image pixel

                    horiPos += 1
                vertPos += 1

            if (self.wiiuName == "horse armor_leather_colored"):
                return coloredImage
            else:
                return colorlessImage