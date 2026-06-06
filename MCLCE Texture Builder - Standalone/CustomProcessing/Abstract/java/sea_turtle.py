from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class sea_turtle(Custom.Function):
    def createImage(self):
        seaTurtleSize = ut.size((ut.mobside * 2), (ut.mobsideHalf * 2))
        baseImage = ut.blankImage(seaTurtleSize)
        turtleImage = rd.readImageSingular(self.wiiuName, Path("turtle", "big_sea_turtle"), "entity", seaTurtleSize)
        baseImage.paste(turtleImage.crop((1, 0, (ut.mobside * 2), (ut.mobsideHalf * 2)), (0, 0))) # moves it 1 to the left
        return baseImage