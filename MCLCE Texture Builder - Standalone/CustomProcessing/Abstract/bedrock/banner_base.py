from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class banner_base(Custom.Function):
    def createImage(self):
        if (ut.checkVersion(14, direction=False)): # earlier than 1.15
            return rd.readImageSingular(self.wiiuName, Path("banner", "banner"), "entity", ut.size(512)).crop((0, 0, 64, 64))
        else:
            return rd.readImageSingular(self.wiiuName, Path("banner", "banner_base"), "entity", ut.mobsize)