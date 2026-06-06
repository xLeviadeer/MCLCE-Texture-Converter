from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd

class banner_process(Custom.Function):

    bannerSheetSize = (256, 288)
    bannerSize = (42, 41)

    def createImage(self, args):
        images = args[0]

        x = 0
        y = 0
        finalImage = ut.blankImage(self.bannerSheetSize)
        for currPattern in images:
            # crop the curr pattern
            background = ut.blankImage(currPattern.size, color=(0, 0, 0, 255))
            background.alpha_composite(currPattern)
            finalImage.paste(background.crop((0, 0, self.bannerSize[0], self.bannerSize[1])), (x, y))

            # continue
            x += self.bannerSize[0]
            if ((x + self.bannerSize[0]) >= self.bannerSheetSize[0]): # checks the next banner size rather than the current so there's no clipping
                x = 0
                y += self.bannerSize[1]
        return finalImage