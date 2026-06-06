from CustomProcessing import Custom
import TextureLibs.Global as Global
import TextureLibs.TextureUtility as ut
import os
import TextureLibs.Read as rd
from CodeLibs.Path import Path
from TextureLibs.Sheet import SheetExtractor

class stack_textures(Custom.Function):
    def createImage(self, args):
        """
        Description:
            attempts to read textures between the start and end and places error or wiiu replacement textures where it cannot read them
        ---
        Arguments:
            - "name" : String <>
                - prepends numbers exactly; requires underscores if needed
            - "padZeros : Boolean <False>
                - whether or not to pad names with 0s when they are less than 10
        ---
        Returns:
            - completed image
        """

        # get variables from arguments
        name = args[0] # expected to be a string
        padZeros = False if (len(args) < 2) else args[1] # expected to be a bool, defualts to False if not provided

        # get the wiiuImage as a sheet for placing bad textures (only is set if needed)
        wiiuImageAsSheet = None

        # find the highest texture number
        path = Path(Global.inputPath, self.type, isRootDirectory=True).getPath()
        if (not os.path.isdir(path)): raise rd.notFoundException # will not be able to read from the list of textures
        textureNumbers = [ # get numbers from each texture
            int(os.path.splitext(file.name)[0].replace(name, ""))
            for file in os.scandir(path) 
            if (file.is_file()) and (file.name.startswith(name))
        ]
        if (len(textureNumbers) == 0): raise rd.notFoundException # if none were found, raise notFound
        amountOfTextures = max(textureNumbers) + 1 # running it with this + 1 makes it the same as calling len() but max has better error raising for my needs
            
        # sheet for textures to be placed on of the size of amount of textures
        sheet = SheetExtractor(ut.size(16, (amountOfTextures * 16)), ut.size(16))

        # for the amount of textures
        for i in range(amountOfTextures):
            # get the name with the current number appended
            iString = i if (padZeros == False) else f"0{i}" if (i < 10) else i # pads zeros if set to true
            currName = f"{name}{iString}"

            # read the currImage from the path
            currImage = None
            try: # try read
                currImage = rd.readImageSingular(self.wiiuName, currName, self.type, ut.size(16), dox16Handling=False)
            except rd.notx16Exception as err: # image isn't x16 in replace mode (resize the image)
                Global.incorrectSizeErrors.append(currName)
                currImage = err.getImage().resize(ut.size(16))
            except rd.notExpectedException: # image isn't x16 in error mode (place error texture)
                Global.notExpectedErrors.append(currName)
                currImage = Global.notFoundImage.resize(ut.size(16))
            except rd.notFoundException: # image didn't exist (use wiiu texture)
                if (wiiuImageAsSheet == None): # set sheet if none
                    wiiuImageAsSheet = SheetExtractor(self.wiiuImage, ut.size(16))
                currImage = wiiuImageAsSheet.extract((0, i))

            # place the image on the sheet
            sheet.insert((0, i), currImage)

        # return
        return sheet.getSheet()



