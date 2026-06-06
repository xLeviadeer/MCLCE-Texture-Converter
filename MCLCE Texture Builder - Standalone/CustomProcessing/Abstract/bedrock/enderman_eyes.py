from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class enderman_eyes(Custom.Function):
    def createImage(self):
        return ut.getOpacityTexture(
                    rd.readImageSingular(self.wiiuName, Path("enderman", "enderman").getPath(), "entity", ut.size(ut.mobside, (ut.mobside / 2))),
                    True, # boolean true if enderman eyes
                )