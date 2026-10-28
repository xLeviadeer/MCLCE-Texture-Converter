from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class dragon(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, Path("enderdragon", "dragon"), "entity", ut.size(ut.mobside * 2))
        image.paste(image.crop((0, 88, 56, 200)), (56, 88))
        return image