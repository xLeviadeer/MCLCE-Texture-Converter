from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class elytra(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("armor", "elytra").getPath(), "models", ut.size(ut.mobside, (ut.mobside / 2)))