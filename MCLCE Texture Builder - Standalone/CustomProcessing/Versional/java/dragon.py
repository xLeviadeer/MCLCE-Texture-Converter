from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class dragon(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(self.wiiuName, Path("enderdragon", "dragon").getPath(withFirstSlash=False), "entity", ut.size(ut.mobside * 2))
        image.paste(image.crop((0, 88, 56, 200)), (56, 88))
        return image