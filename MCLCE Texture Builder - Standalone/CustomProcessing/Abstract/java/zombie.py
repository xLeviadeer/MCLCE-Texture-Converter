from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class zombie(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("zombie", self.wiiuName).getPath(), "entity", ut.mobsize).crop((0, 0, 64, 32))