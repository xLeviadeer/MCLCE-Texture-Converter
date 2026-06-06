from CustomProcessing import Custom
from CodeLibs.Path import Path
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class campfire_smoke(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("campfire_smoke"), "particle", ut.size(16, 192))