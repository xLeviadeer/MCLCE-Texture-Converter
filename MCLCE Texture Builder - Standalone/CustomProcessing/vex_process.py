from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
from CodeLibs.Path import Path
import TextureLibs.Global as Global

class vex_process(Custom.Function):
    def createImage(self, args):
        # read
        linkImage = rd.readImageSingular( # get the image based on game and vex texture
            self.wiiuName, 
            (
                (Path(self.wiiuName).getPathPrependTemp("illager")) if (Global.inputGame == "java") 
                else (Path(self.wiiuName).getPathPrependTemp("vex"))
            ),
            "entity",
            ut.size(ut.mobside / 2),
            False # ignores version patches
        )
        
        # move and resize
        wiiuImage = ut.blankImage(64)
        wiiuImage.paste(linkImage.crop((0, 0, 20, 10)).resize((32, 16)), (0, 0)) # head
        def heighten(image: Image, newBottomHeightMultiplier=3, newWidthMultiplier=2) -> Image:
            slicingPoint = 2
            f"""
            Rules:
                - Slices based on height: ({slicingPoint})
            """
            # help variables
            oldWidth = image.width
            oldHeight = image.height
            newWidth = int(oldWidth * newWidthMultiplier)
            newTopHeight = (slicingPoint * 2)
            newBottomHeight = int((oldHeight - slicingPoint) * newBottomHeightMultiplier)
            newHeight = (newTopHeight + newBottomHeight)

            # move around
            finalImage = ut.blankImage(newWidth, newHeight, doResize=False)
            finalImage.paste(image.crop((0, 0, oldWidth, slicingPoint)).resize((newWidth, newTopHeight)), (0, 0)) # top
            finalImage.paste(image.crop((0, slicingPoint, oldWidth, oldHeight)).resize((newWidth, newBottomHeight)), (0, newTopHeight)) # bottom

            return finalImage
        
        wiiuImage.paste(heighten(linkImage.crop((23, 0, 31, 6))), (40, 16)) # arms
        wiiuImage.paste(heighten(linkImage.crop((0, 10, 10, 16)), newWidthMultiplier=2.4), (16, 16)) # body
        wiiuImage.paste(heighten(linkImage.crop((0, 16, 10, 23)), newBottomHeightMultiplier=2.4), (32, 0)) # legs
        wiiuImage.paste(linkImage.crop((16, 22, 24, 27)).resize((20, 12)), (1, 33)) # wing

        return wiiuImage
