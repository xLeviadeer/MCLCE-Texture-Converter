from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd

class dragon_fireball(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, "dragon_fireball", "items", ut.size(16))