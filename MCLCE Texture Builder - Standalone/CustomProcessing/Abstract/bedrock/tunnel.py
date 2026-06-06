from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class tunnel(Custom.Function):
    def createImage(self):        
        linkImage = rd.readImageSingular(self.wiiuName, "end_sky", "environment", ut.size(128))
        purple = self.findConversionColor(linkImage)
        def blendMultiplyPurple(pixel, x, y, image, args):
            pixel = list(pixel)
            pixel[0] = int(pixel[0] * purple[0])
            pixel[1] = int(pixel[1] * purple[1])
            pixel[2] = int(pixel[2] * purple[2])
            pixel = tuple(pixel)
            return pixel
        return ut.forEveryPixel(linkImage, blendMultiplyPurple)
    
    # finds the conversion color for the end
    def findConversionColor(self, linkImage):
        PIXELPOS = (0, 0)

        # read link image pixel
        linkPixel = linkImage.getpixel(PIXELPOS)
        # read wiiu image pixel
        wiiuPixel = self.wiiuImage.getpixel(PIXELPOS)

        # find purple
        purple = []
        purple.extend([wiiuPixel[0] / linkPixel[0]])
        purple.extend([wiiuPixel[1] / linkPixel[1]])
        purple.extend([wiiuPixel[2] / linkPixel[2]])
        purple = tuple(purple)
        
        return purple
