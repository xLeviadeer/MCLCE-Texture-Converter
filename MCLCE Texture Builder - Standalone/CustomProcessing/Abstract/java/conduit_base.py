from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class conduit_base(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("conduit", "base"), "entity", ut.size(32, 16)).crop((0, 0, 24, 12))
    