from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
from CodeLibs.Path import Path

class pigzombie(Custom.Function):
    def createImage(self):
        if (ut.checkVersion(16)): # 1.16 or newer
            image = rd.readImageSingular(self.wiiuName, Path("piglin", "zombified_piglin"), "entity", ut.mobsize, doVersionPatches=False)
            return Custom.runFunctionFromPath("shared", "pigzombie_process", self.wiiuName, self.type, self.wiiuImage, True, image)
        else:
            image = rd.readImageSingular(self.wiiuName, Path("zombie_pigman").getPath(), "entity", ut.mobsize)
            return image.crop((0, 0, image.width, (image.height / 2)), doResize=False) # contextual (to image size) resizing, means no resizing is needed
            

        