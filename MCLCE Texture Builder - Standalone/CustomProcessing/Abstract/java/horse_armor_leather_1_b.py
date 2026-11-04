from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class horse_armor_leather_1_b(Custom.Function):
    def createImage(self):
        if ut.checkVersion(21, 11):
            return rd.readImageSingular(self.wiiuName, Path("equipment", "horse_body", "leather_overlay"), self.type, ut.mobsize)
        return Custom.runFunctionFromPath("abstract", "horse_armor_leather", self.wiiuName, self.type, self.wiiuImage, isPrintRecursed=True)