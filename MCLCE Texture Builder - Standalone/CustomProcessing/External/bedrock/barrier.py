from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd

class barrier(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, "barrier", "blocks", ut.size(16))