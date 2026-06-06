from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class pigzombie(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, Path("piglin", "zombie_piglin").getPath(), "entity", ut.mobsize)
        return Custom.runFunctionFromPath("shared", "pigzombie_process", self.wiiuName, self.type, self.wiiuImage, True, image)