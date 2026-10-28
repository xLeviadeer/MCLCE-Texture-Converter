from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class zombie(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("zombie", self.wiiuName), "entity", ut.mobsize).crop((0, 0, 64, 32))