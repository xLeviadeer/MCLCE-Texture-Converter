from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class redstone_quad(Custom.Function):
    def createImage(self):
        # create
        dotImage = rd.readImageSingular(self.wiiuName, "redstone_dust_dot.png", self.type, ut.size(16))
        dotCutImage = Image.new('RGBA', (7, 7), "#00000000")
        lineImage = rd.readImageSingular(self.wiiuName, "redstone_dust_line1", self.type, ut.size(16))

        # edit
        lineImage.paste(dotCutImage, (5, 5)) # cuts line down the middle for the dotSize
        dotImage = dotImage.convert("RGBA")
        dotImage.alpha_composite(lineImage)
        dotImage.alpha_composite(lineImage.rotate(90))

        return dotImage