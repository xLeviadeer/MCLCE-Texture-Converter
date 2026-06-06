from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
from CodeLibs.Path import Path
import TextureLibs.Global as Global

class drowned(Custom.Function):
    def createImage(self):
        # variable determined whether the order of layering should be base order or inverse
        baseOrder = True
        countNotFound = 2

        # read reg
        regImage = Image.new("RGBA", ut.mobsize, "#ffffff00")
        try:
            regImage = rd.readImageSingular(self.wiiuName, Path("zombie", "drowned").getPath(), self.type, ut.mobsize)
        except rd.notFoundException:
            countNotFound -= 1
        except rd.notx16Exception as err:
            Global.incorrectSizeErrors.append(self.wiiuName)
            regImage = err.getImage().resize(ut.mobsize)
        except rd.notExpectedException:
            Global.notExpectedErrors.append(self.wiiuName)
            regImage = Global.notFoundImage.resize(ut.mobsize)

        # read overlay
        overImage = Image.new("RGBA", ut.mobsize, "#ffffff00")
        try:
            overImage = rd.readImageSingular(self.wiiuName, Path("zombie", "drowned_outer_layer").getPath(), self.type, ut.mobsize)
        except rd.notFoundException:
            countNotFound -= 1
        except rd.notx16Exception as err:
            Global.incorrectSizeErrors.append(self.wiiuName)
            overImage = err.getImage().resize(ut.mobsize)
        except rd.notExpectedException:
            baseOrder = False
            Global.notExpectedErrors.append(self.wiiuName)
            overImage = Global.notFoundImage.resize(ut.mobsize)

        if (countNotFound == 0): # if neither were found
            raise rd.notFoundException

        # move textures to the right location
        overImageAdjusted = Image.new("RGBA", ut.mobsize, "#ffffff00")
        overImageAdjusted.paste(overImage.crop((0, 0, 32, 16)), (32, 0)) # head
        overImageAdjusted.paste(overImage.crop((0, 16, 56, 32)), (0, 32)) # body and arms
        overImageAdjusted.paste(overImage.crop((16, 48, 32, 64)), (0, 48)) # left leg
        overImageAdjusted.paste(overImage.crop((32, 48, 48, 64)), (48, 48)) # right leg

        # check ordering and paste correctly
        regImage = regImage.convert("RGBA")
        overImageAdjusted = overImageAdjusted.convert("RGBA")
        if (baseOrder):
            regImage.alpha_composite(overImageAdjusted)
            return regImage
        else:
            overImageAdjusted.alpha_composite(regImage)
            return overImageAdjusted