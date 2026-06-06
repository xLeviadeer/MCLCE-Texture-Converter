from CustomProcessing import Custom
import TextureLibs.Read as rd
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor

class moon_phases(Custom.Function):
    def createImage(self):
        # create order
        order = (
            ("full_moon", "waning_gibbous", "third_quarter", "waning_crescent"),
            ("new_moon", "waxing_crescent", "first_quarter", "waxing_gibbous")
        )

        # create placement sheet
        finalSheet = SheetExtractor(ut.size(128, 64), ut.size(32))

        # follow the order, read, and place images
        y = 0
        while (y < len(order)):
            subOrder = order[y]

            x = 0
            while (x < len(subOrder)):
                currName = subOrder[x]

                image = rd.readImageSingular(self.wiiuName, f"celestial\\moon\\{currName}", "environment", ut.size(32), doVersionPatches=False)
                finalSheet.insert((x, y), image, doResize=False)

                x += 1
            y += 1

        # return final image
        return finalSheet.getSheet()