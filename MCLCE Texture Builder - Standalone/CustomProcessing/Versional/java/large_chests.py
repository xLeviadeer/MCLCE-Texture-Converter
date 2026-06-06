from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path
from TextureLibs.SizingImage import SizingImageOps as ImageOps

class large_chests(Custom.Function):
    def createImage(self):
        # reads
        name = None
        match self.wiiuName:
            case "largechest": name = "normal"
            case "christmas_double": name = "christmas"
            case "trapped_double": name = "trapped"
        javaLeft = rd.readImageSingular(self.wiiuName, Path("chest", f"{name}_left"), "entity", ut.mobsize, doVersionPatches=False)
        javaRight = rd.readImageSingular(self.wiiuName, Path("chest", f"{name}_right"), "entity", ut.mobsize, doVersionPatches=False)

        # chest handle
        handle = ut.blankImage(6, 5)
        left = ut.blankImage(1, 4)
        front = ut.blankImage(2, 4)
        right = ut.blankImage(1, 4)
        back = ut.blankImage(2, 4)
        # handle left adjustments
        javaHandleRight = javaLeft.crop((0, 0, 4, 5))
        javaHandleRight.paste(ImageOps.flip(javaHandleRight.crop((0, 1, 4, 5))), (0, 1)) # flip
        front.paste(javaHandleRight.crop((1, 1, 2, 5)), (1, 0)) # front
        right.paste(javaHandleRight.crop((2, 1, 3, 5)), (0, 0)) # right
        back.paste(javaHandleRight.crop((3, 1, 4, 5)), (0, 0)) # back
        handle.paste(javaHandleRight.crop((1, 0, 2, 1)), (1, 0)) # top
        handle.paste(javaHandleRight.crop((2, 0, 3, 1)), (3, 0)) # bottom
        # handle right adjustments
        javaHandleLeft = javaRight.crop((0, 0, 4, 5))
        javaHandleLeft.paste(ImageOps.flip(javaHandleLeft.crop((0, 1, 4, 5))), (0, 1)) # flip
        left.paste(javaHandleLeft.crop((0, 1, 1, 5)), (0, 0)) # left
        front.paste(javaHandleLeft.crop((1, 1, 2, 5)), (0, 0)) # front
        back.paste(javaHandleLeft.crop((3, 1, 4, 5)), (1, 0)) # back
        handle.paste(javaHandleLeft.crop((1, 0, 2, 1)), (2, 0)) # top
        handle.paste(javaHandleLeft.crop((2, 0, 3, 1)), (4, 0)) # bottom
        # paste to handle
        handle.paste(right, (0, 1))
        handle.paste(back, (1, 1))
        handle.paste(front, (3, 1))
        handle.paste(left, (5, 1))

        # chest body
        body = ut.blankImage(88, 43)
        # right
        body.paste(javaRight.crop((29, 0, 44, 14)).rotate(180), (29, 0)) # lid top
        body.paste(javaRight.crop((14, 0, 29, 14)).rotate(180), (59, 0)) # chest bottom
        body.paste(javaRight.crop((14, 19, 29, 33)).rotate(180), (59, 19)) # lid bottom
        body.paste(javaRight.crop((29, 19, 44, 33)).rotate(180), (29, 19)) # chest top
        body.paste(javaRight.crop((43, 33, 58, 43)).rotate(180), (14, 33)) # chest front
        body.paste(javaRight.crop((14, 33, 29, 43)).rotate(180), (73, 33)) # chest back
        body.paste(javaRight.crop((0, 33, 14, 43)).rotate(180), (0, 33)) # chest left
        body.paste(javaRight.crop((0, 14, 14, 19)).rotate(180), (0, 14)) # lid left
        body.paste(javaRight.crop((43, 14, 58, 19)).rotate(180), (14, 14)) # lid front
        body.paste(javaRight.crop((14, 14, 29, 19)).rotate(180), (73, 14)) # lid back
        # left
        body.paste(javaLeft.crop((29, 0, 44, 14)).rotate(180), (14, 0)) # lid top
        body.paste(javaLeft.crop((14, 19, 29, 33)).rotate(180), (44, 19)) # chest bottom
        body.paste(javaLeft.crop((14, 0, 29, 14)).rotate(180), (44, 0)) # lid bottom
        body.paste(javaLeft.crop((29, 19, 44, 33)).rotate(180), (14, 19)) # chest top
        body.paste(javaLeft.crop((43, 33, 58, 43)).rotate(180), (29, 33)) # chest front
        body.paste(javaLeft.crop((14, 33, 29, 43)).rotate(180), (58, 33)) # chest back
        body.paste(javaLeft.crop((29, 33, 43, 43)).rotate(180), (44, 33)) # chest right
        body.paste(javaLeft.crop((29, 14, 43, 19)).rotate(180), (44, 14)) # lid right
        body.paste(javaLeft.crop((43, 14, 58, 19)).rotate(180), (29, 14)) # lid front
        body.paste(javaLeft.crop((14, 14, 29, 19)).rotate(180), (58, 14)) # lid back

        # paste onto finalImage
        finalImage = ut.blankImage((ut.mobside * 2), ut.mobside)
        finalImage.paste(body, (0, 0))
        finalImage.paste(handle, (0, 0))

        return finalImage