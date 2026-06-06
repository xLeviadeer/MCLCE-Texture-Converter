from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class conduit(Custom.Function):
    def createImage(self):
        baseImage = Image.new('RGBA', (16, 16), "#00000000")
        pasteImage = rd.readImageSingular(self.wiiuName, "conduit_base", self.type, ut.size(12, 24))
        pasteImage = pasteImage.crop((6, 6, 12, 12))
        baseImage.paste(pasteImage, (5, 5))

        return baseImage