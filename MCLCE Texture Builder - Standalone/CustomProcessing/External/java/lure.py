from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class lure(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("fishing_hook"), "entity", ut.size(8))