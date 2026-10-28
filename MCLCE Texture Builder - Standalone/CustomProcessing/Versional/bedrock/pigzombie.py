from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class pigzombie(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, Path("piglin", "zombie_piglin"), "entity", ut.mobsize)
        return Custom.runFunctionFromPath("shared", "pigzombie_process", self.wiiuName, self.type, self.wiiuImage, True, image)