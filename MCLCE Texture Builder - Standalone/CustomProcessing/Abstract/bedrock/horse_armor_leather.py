from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class horse_armor_leather(Custom.Function):
    def createImage(self):
        return ut.getOpacityTexture(
                    rd.readImageSingular(self.wiiuName, Path("horse2", "armor", "horse_armor_leather"), "entity", ut.mobsize),
                    False if (self.wiiuName == "horse_armor_leather_1") else True,
                )