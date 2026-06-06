from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class conduit_wind_vertical(Custom.Function):
    def createImage(self):
        return rd.readImageSingular(self.wiiuName, Path("conduit", f"wind_vertical").getPath(), "entity", ut.size(64, 1024)).crop((0, 0, 64, 704))
        