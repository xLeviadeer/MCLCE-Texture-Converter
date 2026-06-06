from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class glint(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, "enchanted_glint_item", self.type, ut.size(128), doVersionPatches=False)
        image = ut.grayscale(image, enhanceBrightness=True)
        image = image.resize(ut.size(64))
        return image