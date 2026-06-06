from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class endergolem(Custom.Function):
    def createImage(self):
        def assignFaceAndBody(image, brightness): 
            returnImage = ut.blankImage(64, 128)
            returnImage.paste(ut.grayscale(image.crop((0, 0, 64, 52)), brightness), (0, 0)) # body (only turn this part grayscale)
            returnImage.paste(image.crop((0, 52, 64, 64)), (0, 116)) # face
            return returnImage
        nums = [
            "black", "gray", "silver", "blue", "brown", "cyan", "green", "orange", "purple", "magenta", "red", "undyed", "light_blue" "lime", "pink", "yellow"
        ]
        
        return rd.readMulticolorGrayscale(self.wiiuName, "entity", assignFaceAndBody, nums, Path("shulker", "shulker_").getPath(), Path("shulker", "shulker_white").getPath(), ut.mobsize)
            