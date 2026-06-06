from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class conduit_base(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("conduit", "base").getPath(), "entity", ut.size(32, 16)).crop((0, 0, 24, 12))
    