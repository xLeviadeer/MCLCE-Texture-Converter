from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImageOps as ImageOps
from CodeLibs import Logger as log

class bed(Custom.Function):
    def createImage(self):
        def __assignBedParts(image, brightness):
            def reassignFoot(foot, position): # assigns for dynamic feet
                newFoot = ut.blankImage(12, 6)
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

            finalImage = ut.blankImage(64, 128)
            image = image.convert("RGBA")

            # blanket (erase)
            blanket = ut.blankImage(24, 24)
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
            thing = image.crop((0, 28, 44, 44))
            image.paste(thing, (0, 22)) # bed (bottom)
            # no need to erase because it's cropped out

            finalImage.paste(image.crop((0, 0, 44, 38)), (0, 64))

            # feet
                # java feet key (where top is pillow looking from above)
                # 1 - bottom left
                # 2 - top left
                # 3 - bottom right
                # 4 - top right
            finalImage.paste(reassignFoot(image.crop((50, 0, 62, 6)), "bottom_left"), (0, 108)) # bottom left (java)
            finalImage.paste(reassignFoot(image.crop((50, 6, 62, 12)), "top_left"), (0, 102)) # top left (java)
            finalImage.paste(reassignFoot(image.crop((50, 12, 62, 18)), "bottom_right"), (12, 108)) # bottom right (java)
            finalImage.paste(reassignFoot(image.crop((50, 18, 62, 24)), "top_right"), (12, 102)) # top right (java)

            return finalImage
        
        return rd.readMulticolorGrayscale(
                self.wiiuName,
                self.type,
                __assignBedParts, # assignment function
                [ # names list (latest is in the list is the highest priority)
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
                ],
                "bed\\", # names path prefix
                "bed\\white", # white path
                ut.size(64, 64)
            )