from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class conduit_wind_vertical(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("conduit", f"wind_vertical"), "entity", ut.size(64, 1024)).crop((0, 0, 64, 704))
        