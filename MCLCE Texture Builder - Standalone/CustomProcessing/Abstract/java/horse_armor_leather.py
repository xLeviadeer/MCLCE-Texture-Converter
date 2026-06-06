from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global
from CodeLibs.Path import Path

class horse_armor_leather(Custom.Function):
    def createImage(self):
        # normally I'd have an error to check the version here so that when the textures doesn't exist (in 1.13) then it uses the wiiu texure. But simply not finding the image will result in the same thing.

        # reads image (notFound and notExpected is caught at a higher level)
        image = Image.new("RGBA", (64, 64), "#ffffff00")
        try:
            image = rd.readImageSingular(self.wiiuName, Path("horse", "armor", "horse_armor_leather").getPath(), self.type, ut.mobsize)
        except rd.notx16Exception as err:
            Global.incorrectSizeErrors.append(self.wiiuName)
            image = err.getImage().resize((64, 64))

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
                if ((HSVpixel[1] > 0) and (self.wiiuName == "horse_armor_leather_1_b")): # pixel is colored (and right key)
                    colorlessImage.putpixel((horiPos, vertPos), image.getpixel((horiPos, vertPos))) # sets the colored imagepixel to the original image pixel
                elif ((HSVpixel[1] == 0) and (self.wiiuName == "horse_armor_leather_1")): # pixel has no color (and right key)
                    coloredImage.putpixel((horiPos, vertPos), image.getpixel((horiPos, vertPos))) # sets the colorless imagepixel to the original image pixel

                horiPos += 1
            vertPos += 1

        if (self.wiiuName == "horse_armor_leather_1"):
            return coloredImage
        else:
            return colorlessImage