from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd

class firework__stars(Custom.Function):
    def createImage(self):
        # get the image
        image = rd.readImageSingular(self.wiiuName, "fireworks_charge", self.type, ut.size(16))
        
        # convert the image if needed and get the opacity portion of the image
        image = image.convert("RGBA")
        if (self.wiiuName == "firework star_colorless"):
            return ut.getOpacityTexture(image, True)
        elif (self.wiiuName == "firework star_colored"):
            return ut.getOpacityTexture(image, False)