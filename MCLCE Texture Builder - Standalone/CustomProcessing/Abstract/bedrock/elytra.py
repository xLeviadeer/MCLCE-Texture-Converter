from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class elytra(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("armor", "elytra"), "models", ut.size(ut.mobside, (ut.mobside / 2)))