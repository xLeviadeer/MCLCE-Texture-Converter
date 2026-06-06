from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class horse_armor_leather(Custom.Function):
    def createImage(self):
        return ut.getOpacityTexture(
                    rd.readImageSingular(self.wiiuName, Path("horse2", "armor", "horse_armor_leather"), "entity", ut.mobsize),
                    False if (self.wiiuName == "horse_armor_leather_1") else True,
                )