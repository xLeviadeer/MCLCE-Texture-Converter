from typing import (
    Self,
    ClassVar
)
from dataclasses import (
    dataclass, KW_ONLY
)

from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.SizingImage import (
    SizingImage as Image,
    SizingImageOps as ImageOps
)
from TextureLibs.Sheet import SheetExtractor
from CodeLibs import Logger as log

class bed(Custom.Function):
    NAMES = [ # names list (latest is in the list is the highest priority)
        "black",
        "gray",
        "silver",
        "blue",
        "brown",
        "cyan",
        "green",
        "orange",
        "purple",
        "magenta",
        "red",
        "light_blue"
        "lime",
        "pink",
        "yellow",
    ]

    @dataclass(slots=True)
    class Foot:
        _: KW_ONLY
        left: Image = ut.blankImage(3, 3)
        front: Image = ut.blankImage(3, 3)
        right: Image = ut.blankImage(3, 3)
        back: Image = ut.blankImage(3, 3)
        top: Image = ut.blankImage(3, 3)
        bottom: Image = ut.blankImage(3, 3)

        # feet don't map normally ╎ they map circularly around the top ∋ ⌄
        #   • left = left
        #   • front = top
        #   • right = right
        #   • back = bottom
        #   • top = front
        #   • bottom = back
        SIZE: ClassVar[tuple[int, int]] = (12, 6)
        LEFT_POS: ClassVar[tuple[int, int]] = (0, 3)
        FRONT_POS: ClassVar[tuple[int, int]] = (3, 0)
        RIGHT_POS: ClassVar[tuple[int, int]] = (6, 3)
        BACK_POS: ClassVar[tuple[int, int]] = (6, 0)
        TOP_POS: ClassVar[tuple[int, int]] = (3, 3)
        BOTTOM_POS: ClassVar[tuple[int, int]] = (9, 3)

        def to_img(self: Self) -> Image:
            uv_img: Image = ut.blankImage(self.SIZE)
            uv_img.paste(self.left, self.LEFT_POS)
            uv_img.paste(self.front, self.FRONT_POS)
            uv_img.paste(self.right, self.RIGHT_POS)
            uv_img.paste(self.back, self.BACK_POS)
            uv_img.paste(self.top, self.TOP_POS)
            uv_img.paste(self.bottom, self.BOTTOM_POS)
            return uv_img

    def process(self: Self) -> Image:
        # read each image
        BOT_BLANKET_SECT = (0, 7, 16, 11)
        bot_east: Image = self.read_section("foot_east", BOT_BLANKET_SECT)
        bot_south: Image = self.read_section("foot_south", BOT_BLANKET_SECT)
        bot_west: Image = self.read_section("foot_west", BOT_BLANKET_SECT)
        bot_up: Image = self.read_section("foot_up", (0, 0, 16, 16))
        TOP_EAST_BLANKET_SECT = (0, 7, 8, 11)
        top_east: Image = self.read_section("head_east", TOP_EAST_BLANKET_SECT)
        top_north: Image = rd.readImageSingular(self.wiiuName, "bed_head_north", "block", ut.size(16))
        TOP_WEST_BLANKET_SECT = (8, 7, 16, 11)
        top_west: Image = self.read_section("head_west", TOP_WEST_BLANKET_SECT)
        TOP_UP_BLANKET_SECT = (0, 8, 16, 16)
        top_up: Image = self.read_section("head_up", TOP_UP_BLANKET_SECT)
        down: Image = rd.readImageSingular(self.wiiuName, "bed_down", "block", ut.size(16))
        final: Image = ut.blankImage(64, 128)

        # collect blanket
        bot_east, bot_east_blanket = bot_east.cut(BOT_BLANKET_SECT) # pull from bot_east
        final.paste(bot_east_blanket.rotate(90, expand=True), (22, 22)); del bot_east_blanket
        bot_south, bot_south_blanket = bot_south.cut(BOT_BLANKET_SECT) # pull from bot_south
        final.paste(bot_south_blanket.rotate(180), (22, 2)); del bot_south_blanket
        bot_west, bot_west_blanket = bot_west.cut(BOT_BLANKET_SECT) # pull from bot_west
        final.paste(bot_west_blanket.rotate(-90, expand=True), (2, 22)); del bot_west_blanket
        # pull from bot_up
        final.paste(bot_up, (6, 22)); del bot_up
        top_east, top_east_blanket = top_east.cut(TOP_EAST_BLANKET_SECT) # pull from top_east
        final.paste(top_east_blanket.rotate(90, expand=True), (22, 14)); del top_east_blanket
        # no pull from top_north
        # ⌃
        top_west, top_west_blanket = top_west.cut(TOP_WEST_BLANKET_SECT) # pull from top_west
        final.paste(top_west_blanket.rotate(-90, expand=True), (2, 14)); del top_west_blanket
        top_up, top_up_blanket = top_up.cut(TOP_UP_BLANKET_SECT) # pull from top_up
        final.paste(top_up_blanket, (6, 14)); del top_up_blanket 

        # foot boxing
        FOOT_LEFT_BOX = (0, 13, 9, 16)
        FOOT_RIGHT_BOX = (7, 13, 16, 16)
        FOOT_BOTH_LEFT_BOX = (0, 13, 6, 16)
        FOOT_BOTH_RIGHT_BOX = (10, 13, 16, 16)
        bot_east_foot = bed.Foot()
        bot_west_foot = bed.Foot()
        top_east_foot = bed.Foot()
        top_west_foot = bed.Foot()

        # collect foot angles from bot_east
        bot_east, bot_east_foot_angles = bot_east.cut(FOOT_LEFT_BOX) # pull from bot_east
        bot_east_foot_angles = SheetExtractor(bot_east_foot_angles, ut.size(3))
        bot_east_foot.right = bot_east_foot_angles.extract((0, 0)).rotate(90)
        bot_east_foot.back = bot_east_foot_angles.extract((1, 0)).rotate(-90)
        bot_east_foot.bottom = bot_east_foot_angles.extract((2, 0)).rotate(90)
        del bot_east_foot_angles

        # collect foot angles from bot_south
        bot_south, bot_south_foot_angles_right = bot_south.cut(FOOT_BOTH_RIGHT_BOX)
        bot_south_foot_angles_right = SheetExtractor(bot_south_foot_angles_right, ut.size(3))
        bot_east_foot.front = bot_south_foot_angles_right.extract((1, 0)).rotate(-90)
        bot_east_foot.left = bot_south_foot_angles_right.extract((0, 0)).rotate(-90)
        del bot_south_foot_angles_right
        bot_south, bot_south_foot_angles_left = bot_south.cut(FOOT_BOTH_LEFT_BOX)
        bot_south_foot_angles_left = SheetExtractor(bot_south_foot_angles_left, ut.size(3))
        bot_west_foot.front = bot_south_foot_angles_left.extract((0, 0)).rotate(90)
        bot_west_foot.right = bot_south_foot_angles_left.extract((1, 0)).rotate(90)
        del bot_south_foot_angles_left

        # collect foot angles from bot_west
        bot_west, bot_west_foot_angles = bot_west.cut(FOOT_RIGHT_BOX)
        bot_west_foot_angles = SheetExtractor(bot_west_foot_angles, ut.size(3))
        bot_west_foot.left = bot_west_foot_angles.extract((2, 0)).rotate(-90)
        bot_west_foot.back = bot_west_foot_angles.extract((1, 0)).rotate(90)
        bot_west_foot.bottom = bot_west_foot_angles.extract((0, 0)).rotate(180)
        del bot_west_foot_angles

        # collect foot angles from top_east
        top_east, top_east_foot_angles = top_east.cut(FOOT_RIGHT_BOX)
        top_east_foot_angles = SheetExtractor(top_east_foot_angles, ut.size(3))
        top_east_foot.right = top_east_foot_angles.extract((2, 0)).rotate(90)
        top_east_foot.front = top_east_foot_angles.extract((1, 0)).rotate(-90)
        top_east_foot.bottom = top_east_foot_angles.extract((0, 0)).rotate(180)
        del top_east_foot_angles

        # collect foot angles from top_north
        top_north, top_north_foot_angles_left = top_north.cut(FOOT_BOTH_LEFT_BOX)
        top_north_foot_angles_left = SheetExtractor(top_north_foot_angles_left, ut.size(3))
        top_east_foot.back = top_north_foot_angles_left.extract((0, 0)).rotate(90)
        top_east_foot.left = top_north_foot_angles_left.extract((1, 0)).rotate(-90)
        del top_north_foot_angles_left
        top_north, top_north_foot_angles_right = top_north.cut(FOOT_BOTH_RIGHT_BOX)
        top_north_foot_angles_right = SheetExtractor(top_north_foot_angles_right, ut.size(3))
        top_west_foot.back = top_north_foot_angles_right.extract((1, 0)).rotate(-90)
        top_west_foot.right = top_north_foot_angles_right.extract((0, 0)).rotate(90)
        del top_north_foot_angles_right

        # collect foot angles from top_west
        top_west, top_west_foot_angles = top_west.cut(FOOT_LEFT_BOX)
        top_west_foot_angles = SheetExtractor(top_west_foot_angles, ut.size(3))
        top_west_foot.left = top_west_foot_angles.extract((0, 0)).rotate(-90)
        top_west_foot.front = top_west_foot_angles.extract((1, 0)).rotate(90)
        top_west_foot.bottom = top_west_foot_angles.extract((2, 0)).rotate(90)
        del top_west_foot_angles

        # place feet
        final.paste(bot_east_foot.to_img(), (12, 108))
        final.paste(bot_west_foot.to_img(), (0, 108))
        final.paste(top_east_foot.to_img(), (12, 102))
        final.paste(top_west_foot.to_img(), (0, 102))

        # collect bed frame & pillows
        final.paste(bot_east.rotate(90), (22 - 7, 86)); del bot_east 
        final.paste(bot_south.rotate(180), (22, 64 - 3)); del bot_south
        final.paste(bot_west.crop((0, 7, 16, 13)).rotate(-90, expand=True), (0, 86)); del bot_west 
        final.paste(top_east.rotate(90), (22 - 7, 70)); del top_east
        final.paste(top_north.rotate(180), (6, 64 - 3)); del top_north
        final.paste(top_west.crop((0, 7, 16, 13)).rotate(-90, expand=True), (0, 70)); del top_west
        final.paste(top_up, (6, 70)); del top_up

        # collect bottom
        final.paste(down, (28, 70))
        final.paste(down, (28, 86))

        # ret
        return final

    def read_section(
        self: Self,
        location: str,
        box: tuple[int, int, int, int]
    ) -> Image:
        """read a multicolor grayscale grayscaling only a section of the image"""
        return rd.readMulticolorGrayscale(
            self.wiiuName, "block", 
            lambda image, brightness: bed.grayscale_section(image, box, brightness),
            bed.NAMES, f"_bed_{location}", f"white_bed_{location}",
            ut.size(16), 
            doPrepend=True
        )

    @staticmethod
    def grayscale_section(
        image: Image, 
        box: tuple[int, int, int, int],
        brightness: bool
    ) -> Image:
        """grayscales the boxed section of the image"""
        image = image.convert("RGBA")
        image.paste(ut.grayscale(image.crop(box), brightness), box[:2])
        return image

    def process_old(self: Self) -> Image:
        return rd.readMulticolorGrayscale(
            self.wiiuName,
            self.type,
            bed.assign_bed_parts_old, # assignment function
            bed.NAMES,
            "bed\\", # names path prefix
            "bed\\white", # white path
            ut.size(64, 64)
        )

    @staticmethod
    def reassign_foot_old(foot: Image, position: str) -> Image: # assigns for dynamic feet
        newFoot: Image = ut.blankImage(12, 6)
        def m(num): # used for easy numbers
            return num * 3
        def crop(x, y = None): # used to generate easy crops
            if (y == None): # (assumes x is a tuple)
                y = x[1]
                x = x[0]
            return (x, y, (x + m(1)), (y + m(1)))
        def set(posTargetFrom, posTargetTo, operations = None, argument = None):
            imageTargetFrom = foot.crop(crop(posTargetFrom))
            if (operations != None): # there can only be one argument anyway
                for operation in operations:
                    match (operation):
                        case "mirror":
                            imageTargetFrom = ImageOps.mirror(imageTargetFrom)
                        case "flip":
                            imageTargetFrom = ImageOps.flip(imageTargetFrom)
                        case "rotate":
                            if (argument == None): print("error in set syntax", log.ERROR); return newFoot.paste(imageTargetFrom, posTargetTo)
                            imageTargetFrom = imageTargetFrom.rotate(argument)
                        case _:
                            pass
            newFoot.paste(imageTargetFrom, posTargetTo)
        TOP = (m(1), m(0))
        BOTTOM = (m(2), m(0))
        LEFT = (m(0), m(1))
        FRONT = (m(1), m(1))
        RIGHT = (m(2), m(1))
        BACK = (m(3), m(1))
    
        match (position):
            case "top_left":
                set(LEFT, TOP, ("rotate",), 180)
                set(FRONT, LEFT, ("rotate",), -90)
                set(TOP, FRONT)
                set(BOTTOM, BACK, ("mirror",))
                set(RIGHT, RIGHT, ("mirror", "rotate"), 90)
                set(BACK, BOTTOM, ("rotate",), 180)
            case "top_right":
                set(LEFT, RIGHT, ("rotate",), 90)
                set(FRONT, TOP, ("mirror",))
                set(TOP, FRONT)
                set(BOTTOM, BACK)
                set(RIGHT, LEFT, ("rotate",), -90)
                set(BACK, BOTTOM, ("flip",))
            case "bottom_left":
                set(LEFT, LEFT, ("rotate",), -90)
                set(FRONT, BOTTOM, ("flip",))
                set(TOP, FRONT)
                set(BOTTOM, BACK, ("mirror",))
                set(RIGHT, RIGHT, ("rotate",), 90)
                set(BACK, TOP, ("rotate",), 180)
            case "bottom_right":
                set(LEFT, BOTTOM)
                set(FRONT, RIGHT, ("rotate",), 90)
                set(TOP, FRONT)
                set(BOTTOM, BACK)
                set(RIGHT, TOP, ("rotate",), 180)
                set(BACK, LEFT, ("rotate",), -90)
            case _:
                pass
        return newFoot

    @staticmethod
    def assign_bed_parts_old(image: Image, brightness: bool) -> Image:   
        finalImage: Image = ut.blankImage(64, 128)
        image = image.convert("RGBA")
    
        # blanket (erase)
        blanket: Image = ut.blankImage(24, 24)
        blanket.paste(image.crop((2, 14, 26, 22)), (0, 0)) # top (upper)
        image.paste(ut.blankImage(24, 8), (2, 14)) # erase
        blanket.paste(image.crop((2, 28, 26, 44)), (0, 8)) # top (lower)
        image.paste(ut.blankImage(24, 16), (2, 28)) # erase
        bottomBlanket = image.crop((22, 24, 38, 28)) # bottom
        image.paste(ut.blankImage(16, 4), (22, 24)) # erase
    
        # blanket (assign)
        finalImage.paste(bottomBlanket, (22, 2)) # bottom
        finalImage.paste(blanket, (2, 14)) # blanket
    
        # grayscale (while only blanket is present in the image)
        finalImage = ut.grayscale(finalImage, brightness)
    
        # bed
        image.paste(image.crop((22, 22, 38, 24)), (22, 0)) # bottom
        image.paste(image.crop((0, 28, 44, 44)), (0, 22)) # bed (bottom)
        # no need to erase because it's cropped out
    
        finalImage.paste(image.crop((0, 0, 44, 38)), (0, 64))
    
        # feet
            # java feet key (where top is pillow looking from above)
            # 1 - bottom left
            # 2 - top left
            # 3 - bottom right
            # 4 - top right
        finalImage.paste(bed.reassign_foot_old(image.crop((50, 0, 62, 6)), "bottom_left"), (0, 108)) # bottom left (java)
        finalImage.paste(bed.reassign_foot_old(image.crop((50, 6, 62, 12)), "top_left"), (0, 102)) # top left (java)
        finalImage.paste(bed.reassign_foot_old(image.crop((50, 12, 62, 18)), "bottom_right"), (12, 108)) # bottom right (java)
        finalImage.paste(bed.reassign_foot_old(image.crop((50, 18, 62, 24)), "top_right"), (12, 102)) # top right (java)
    
        return finalImage

    def createImage(self):
        if ut.checkVersion(26, 2):
            return self.process()
        else:
            return self.process_old()