from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
import TextureLibs.Global as Global
from CodeLibs.Path import Path

class bat_process(Custom.Function):
    def createImage(self, args):
        # read
        linkImage = rd.readImageSingular( # get the image based on game and vex texture
            self.wiiuName, 
            Path("bat" if (Global.inputGame == "java") else "bat_v2"),
            "entity",
            ut.size(ut.mobside / 2),
            doVersionPatches=False
        )

        # blank wiiuImage
        wiiuImage = ut.blankImage(64)

        # -- move/scale head, body and tail --

        # left head
        (10, 9, 12, 12)
        leftHead = ut.blankImage(6)
        leftHead.paste(linkImage.crop((10, 9, 12, 12)).resize((3, 6)), (0, 0)) # left of left head
        leftHead.paste(linkImage.crop((0, 9, 2, 12)).resize((3, 6)), (3, 0)) # right of right head
        wiiuImage.paste(leftHead, (0, 6)) # to wiiuImage

        # right head (doesn't need this but is done to maintain equality between both sides)
        rightHead = ut.blankImage(6)
        rightHead.paste(linkImage.crop((6, 9, 8, 12)).resize((3, 6)), (0, 0)) # left of right head
        rightHead.paste(linkImage.crop((8, 9, 12, 12)).resize((3, 6)), (3, 0)) # right of right head
        wiiuImage.paste(rightHead, (12, 6)) # to wiiuImage

        # front, back head
        wiiuImage.paste(linkImage.crop((2, 9, 6, 12)).resize((6, 6)), (6, 6)) # front
        wiiuImage.paste(linkImage.crop((8, 9, 12, 12)).resize((6, 6)), (18, 6)) # back

        # top and bottom head
        wiiuImage.paste(linkImage.crop((2, 7, 10, 9)).resize((12, 6)), (6, 0))

        # body sides 
        wiiuImage.paste(linkImage.crop((0, 2, 10, 7)).resize((24, 12)), (0, 22))

        # body top/bottom
        wiiuImage.paste(linkImage.crop((2, 0, 8, 2)).resize((12, 6)), (6, 16))

        # tail
        wiiuImage.paste(linkImage.crop((15, 16, 23, 20)).resize((12, 8)), (0, 34))

        # back ear
        backEarAlpha = linkImage.crop((11, 14, 15, 21)) # read ear
        backEar = ut.blankImage(backEarAlpha.size, color=ut.findAverageColor(backEarAlpha)) # create bg from average color
        backEar.alpha_composite(backEarAlpha) # add ear on top of bg
        wiiuImage.paste(backEar.resize((3, 4)), (29, 1)) # put right side of right ear on back

        # front ear
        frontEarAlpha = linkImage.crop((4, 14, 8, 21)) # read ear
        frontEar = ut.blankImage(frontEarAlpha.size, color=ut.findAverageColor(frontEarAlpha)) # create bg from average color
        frontEar.alpha_composite(frontEarAlpha) # add ear on top of bg
        wiiuImage.paste(frontEar.resize((3, 4)), (25, 1)) # put right side of left ear on front

        # wing processing
        leftWing = ut.blankImage(8)
        leftWing.paste(linkImage.crop((16, 0, 22, 8)), (0, 0)) # wing
        leftWing.paste(linkImage.crop((14, 8, 16, 15)), (6, 1)) # connection
        leftWing = leftWing.resize((18, 16)) # scale up
        wiiuImage.paste(leftWing.crop((0, 0, 8, 16)), (25, 16)) # left part
        wiiuImage.paste(leftWing.crop((8, 0, 18, 16)), (43, 1)) # right part

        # return final
        return wiiuImage
