from CustomProcessing import Custom
from CodeLibs.Path import Path
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class campfire_smoke(Custom.Function):
    def createImage(self):
        return SheetExtractor(Path("campfire_smoke"), ut.size(16), self.wiiuName, "particle", ut.size(16, 192)).extract((0, 0))