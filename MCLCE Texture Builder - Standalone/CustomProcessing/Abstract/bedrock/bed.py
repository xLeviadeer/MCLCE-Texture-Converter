from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class bed(Custom.Function):
    def createImage(self):
        def assignBedParts(image, brightness):
            finalImage = ut.blankImage(64, 128)
            # grayscale portion (blankets)
            finalImage.paste(image.crop((2, 14, 26, 38)), (2, 14)) # blanket
            image.paste(ut.blankImage(24, 24), (2, 14)) # (blanket erase)
            finalImage.paste(image.crop((22, 2, 38, 6)), (22, 2)) # blanket (bottom/back)
            image.paste(ut.blankImage(16, 4), (22, 2)) # (blanket (bottom/back) erase)
            finalImage = ut.grayscale(finalImage, brightness) # grayscale
            # the rest of stuff (not blankets)
            finalImage.paste(image.crop((0, 0, 44, 50)), (0, 64)) # other
            return finalImage
        nums = [
            "black", "gray", "silver", "blue", "brown", "cyan", "green", "orange", "purple", "magenta", "red", "undyed", "light_blue" "lime", "pink", "yellow"
        ]

        return rd.readMulticolorGrayscale(self.wiiuName, "entity", assignBedParts, nums, Path("bed").getPath(withLastSlash=True), Path("bed", "white").getPath(), ut.mobsize)
