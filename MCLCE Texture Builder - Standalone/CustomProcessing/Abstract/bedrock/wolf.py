from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class wolf(Custom.Function):
    def createImage(self):
        collarImage = rd.readImageSingular(self.wiiuName, Path("wolf", "wolf_tame"), "entity", ut.size(ut.mobside, (ut.mobside / 2)))
        wolfImage = rd.readImageSingular(self.wiiuName, Path("wolf", "wolf"), "entity", ut.size(ut.mobside, (ut.mobside / 2)))

        # wolf tame or wolf collar
        if (self.wiiuName == "wolf_tame"):
            i = 0
            while i < collarImage.width:
                j = 0
                while j < collarImage.height:
                    if (collarImage.getpixel((i, j))[3] != 0): # if pixel isn't empty in collar image
                        wolfImage.putpixel((i, j), (0, 0, 0, 0)) # erase from wolf image
                    j += 1
                i += 1
            return wolfImage
        else:
            return collarImage