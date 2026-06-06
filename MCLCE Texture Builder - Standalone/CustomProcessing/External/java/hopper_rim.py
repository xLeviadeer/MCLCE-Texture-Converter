from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class hopper_rim(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, "hopper_top", self.type, ut.size(16))
        image.paste(Image.new('RGBA', (12, 12), "#00000000"), (2, 2))

        return image