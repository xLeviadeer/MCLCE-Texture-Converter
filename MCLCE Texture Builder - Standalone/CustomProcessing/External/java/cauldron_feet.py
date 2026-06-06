from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class cauldron_feet(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, "cauldron_bottom", self.type, ut.size(16))
        image.paste(Image.new('RGBA', (12, 12), "#00000000"), (2, 2))

        # cut for each side segment
        image.paste(Image.new('RGBA', (2, 8), "#00000000"), (0, 4))
        image.paste(Image.new('RGBA', (2, 8), "#00000000"), (14, 4))
        image.paste(Image.new('RGBA', (8, 2), "#00000000"), (4, 0))
        image.paste(Image.new('RGBA', (8, 2), "#00000000"), (4, 14))

        return image