from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class breaks(Custom.Function):
    def createImage(self):
        num = int(self.wiiuName[-1:])
        return rd.readImageSingular(self.wiiuName, f"destroy_stage_{num}", "environment", ut.size(16))