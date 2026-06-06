from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd

class tipped_arrow(Custom.Function):
    def createImage(self):
        finalImage = ut.blankImage(int(ut.mobside / 2))
        image = rd.readImageSingular(self.wiiuName, "arrows", "entity", ut.size((ut.mobside / 2)))
        finalImage.paste(image.crop((0, 0, 32, 10)), (0, 0))
        return finalImage