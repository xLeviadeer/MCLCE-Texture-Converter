from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image

class sign(Custom.Function):
    def createImage(self):
        # set up image & read
        input_image: Image = rd.readImageSingular(self.wiiuName, "oak_sign", "block", ut.size(ut.mobsideHalf), doVersionPatches=False)
        final_image: Image = ut.blankImage(ut.mobside, ut.mobsideHalf)

        # face
        final_image.paste(input_image.crop((0, 0, 24, 2)), (2, 0)) # top
        final_image.paste(input_image.crop((24, 2, 26, 14)), (0, 2)) # left
        final_image.paste(input_image.crop((0, 2, 24, 14)), (2, 2)) # front
        final_image.paste(input_image.crop((0, 28, 24, 30)), (26, 0)) # bottom
        final_image.paste(input_image.crop((0, 16, 24, 28)), (26, 2)) # back
        final_image.paste(input_image.crop((24, 16, 26, 28)), (50, 2)) # right

        # stick
        top_bottom: Image = input_image.crop((28, 30, 30, 32))
        final_image.paste(top_bottom, (2, 14)) # top
        final_image.paste(top_bottom, (4, 14)) # bottom
        final_image.paste(input_image.crop((28, 0, 32, 14)), (0, 16)) # left + front
        final_image.paste(input_image.crop((28, 16, 32, 30)), (4, 16)) # right + back

        # ret
        return final_image