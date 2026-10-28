from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class sheeps(Custom.Function):
    def createImage(self):
        sheepImage = rd.readImageSingular(self.wiiuName, Path("sheep", "sheep"), "entity", ut.mobsize)
        if (self.wiiuName == "sheep"):
            return ut.getImageNoOpacity(sheepImage.crop((0, 0, 64, 32)))
        else: # sheep fur
            return sheepImage.crop((0, 32, 64, 64))