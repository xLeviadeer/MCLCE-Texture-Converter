from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
import TextureLibs.SizingImage as si 

class conduits(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, self.wiiuName, "blocks", si.deconvertTuple(self.wiiuImage.size))