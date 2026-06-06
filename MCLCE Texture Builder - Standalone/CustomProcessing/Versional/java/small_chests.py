from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path

class small_chests(Custom.Function):
    def createImage(self):
        match self.wiiuName:
            case "enderchest": self.wiiuName = "ender"
            case "chest": self.wiiuName = "normal"
            # others stay the same
        image = rd.readImageSingular(self.wiiuName, Path("chest", self.wiiuName).getPath(), "entity", ut.mobsize)
        image = image.convert("RGBA")
        finalImage = image.copy()
        def swapLocationsAndRotate(imageOneBox, imageTwoBox):
            finalImage.paste(image.crop(imageOneBox).rotate(180), imageTwoBox[:2])
            finalImage.paste(image.crop(imageTwoBox).rotate(180), imageOneBox[:2])

        # Locations in terms of java
        def lid(left, right):
            return (left, 14, right, 19)
        def body(left, right):
            return (left, 33, right, 43)
        def lidTop(left, right):
            return (left, 0, right, 14)
        def bodyTop(left, right):
            return (left, 19, right, 33)
        LIDTOP = lidTop(14, 28)
        LIDBOTTOM = lidTop(28, 42)
        LIDLEFT = lid(0, 14)
        LIDFRONT = lid(14, 28)
        LIDRIGHT = lid(28, 42)
        LIDBACK = lid(42, 56)
        BODYTOP = bodyTop(14, 28)
        BODYBOTTOM = bodyTop(28, 42)
        BODYLEFT = body(0, 14)
        BODYFRONT = body(14, 28)
        BODYRIGHT = body(28, 42)
        BODYBACK = body(42, 56)

        swapLocationsAndRotate(LIDTOP, LIDBOTTOM)
        swapLocationsAndRotate(BODYTOP, BODYBOTTOM)
        swapLocationsAndRotate(LIDLEFT, LIDRIGHT)
        swapLocationsAndRotate(BODYLEFT, BODYRIGHT)
        swapLocationsAndRotate(LIDFRONT, LIDBACK)
        swapLocationsAndRotate(BODYFRONT, BODYBACK)

        return finalImage
