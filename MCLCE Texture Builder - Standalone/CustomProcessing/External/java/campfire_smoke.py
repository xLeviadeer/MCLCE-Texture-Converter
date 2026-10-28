from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class campfire_smoke(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("big_smoke_0"), "particle", ut.size(16))