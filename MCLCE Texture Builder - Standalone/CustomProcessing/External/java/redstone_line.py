from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class redstone_line(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, "redstone_dust_line0", self.type, ut.size(16))
        image = image.rotate(90)

        return image