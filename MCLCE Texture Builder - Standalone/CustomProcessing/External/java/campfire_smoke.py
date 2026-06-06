from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class campfire_smoke(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("big_smoke_0").getPath(), "particle", ut.size(16))