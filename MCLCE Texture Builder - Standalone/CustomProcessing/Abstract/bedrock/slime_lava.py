from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class slime_lava(Custom.Function):
    def createImage(self):
        return ut.getImageNoOpacity(
                rd.readImageSingular(self.wiiuName, Path("slime", "magmacube"), "entity", ut.size(ut.mobside, (ut.mobside / 2))),
                doZeroDetection=True
            )