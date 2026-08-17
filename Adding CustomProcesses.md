# Adding a new Custom Process
This document will explain how to create a new CustomProcess and some other details about how the program determines versional differences. (A versional difference is a texture change due to an update to Minecraft java/bedrock)

## What are Linking Libraries?
### What is a Type Library?
A "type library" is a dictionary or list of values based on a particular "type" which associates lce base game images with identifyable string names

### What is a Layer Library?
A "layer library" is a library which extends Type Libraries via layering. When the program attempts to convert textures to LCE versions which aren't 1.13 then certain textures need to be removed or added to accommodate missing or extra textures. Layer Libs serve this purpose either adding, replacing or removing elements from different type libraries non-destructively at runtime. **In the case you need to add textures to ps4 only conversion, you must add them through the 1.14 layer lib.**

### What is a Base Library?
A "base library" is a dictionary which is used like a phone book of translations for texture names.

Textures are first assigned a "wiiu" name. Everything in the TB builds off of this. When the TB runs it will find a texture and it's associted wiiu name. To find the correct texture for java or bedrock it will translate the wiiu name to it's associated java or bedrock name using the linking library, "Base_java" or "Base_bedrock" respectively. 

Base libs contain keys regarding all conversions. This includes keys for converting 1.14 textures because extra keys simply wont be referenced if they aren't needed at runtime.

**Importantly, the base libs can contain string, true and false values and nothing else.** 
* String Values
    * When the value is a string value the value of the string is expected to be a path extension on top of the currently targeted type (except for misc) to where the texture is located.
* False Value
    * When the value is false the wiiu texture (the texture from the base lce game) will always be used and no texture translation will be attempted
* True Value
    * When the value is true the program hunts for a "Custom Process" which are special processes used for converting complex textures "which cannot be simply copied".

### What is a Versional Library?
A "versional library" is a library which changes the location of a java/bedrock texture or it's Custom process status based on the input game version. For example, villagers are given extra processing for 1.13 output when the input version is greater than or equal to 1.14 for java because the structure of villager textures is changed in the 1.14 update. 

A versional library is also a layered library system where changes are layered onto the base lib non-destrutively at runtime. However the implementation of how this layering is done is different because when versional custom processes are ran, versional differences shouldn't be searched for or there would be an infinite recursion loop. **this means, if you are writing a versional function you must always make sure that `doVersionPatches` is set to false for all file reads.**

## What is A Custom Process?
A "Custom Process" is a specialized function for converting a particular texture between versions. Custom processes can be broken into 2 distinct groups with a few subctegories.

### Shared vs. Non-Shared Custom Processes
A shared custom process is a custom process that can be referenced from multiple input games (*both* java *and* bedrock). Shared custom processes will run a conversion for either java or bedrock depending on the given parameters. Shared processes should *only* be used when a custom process is required that is very similar for both java and bedrock.

A non-shared custom process is a custom process that can only be references for one input game (*either* java *or* bedrock). Non-shared custom processes are the required file for all custom process calls any base library (more on this later). When a non-shared custom process wants to run a shared custom process it will reference the shared process from itself and pass along the execution of image processing to the shared process. `isPrintRecursed` should always be set to true in this case.

A non-shared custom process can also reference another non-shared custom process to have "pseudo sharing" between multiple custom processes of the same input game (java or bedrock) which cannot cross reference between input games. This should *only* be used when multiple custom processes reference a very similar conversion. An example of this are the processes related to map icons (under Abstract > java). `isPrintRecursed` should always be set to true in this case.

Regarding the file system structure, shared custom processes are always in the root `CustomProcessing/water_process.py` directory whereas non-shared custom processes are all in nested folders underneath. For example, `CustomProcessing/Abstract/java/bed.py`.

## How to Create a New Custom Process
### Step 1 - Add Lib Ref
Change the base library or versional library reference for your target texture to true so that the TB will use a Custom Process for this texture.

### Step 2 - Create Custom Process File
Create a custom function file in the respective location using the correct name.

Your file must be placed in the correct process type and of the game it is associated with. A games process type is determined by what kind of texture it is. Sheet textures (textures that are placed onto the terrain, items, particle, etc. sheet) fall under "External". Abstract textures (textures that are NOT placed onto the terrain, items, particle, etc. sheet) fall under "Abstract". Textures which require custom processes as a result of a versional difference, regardless of sheet or abstract status fall under "Versional".

The name of the file must be exactly the same as the associated textures "wiiu key" aka it's name in type library. If the name contains spaces, spaces should be replaced with two underscores, "cool texture" -> "cool__texture".

### Step 3 - Define a Custom Process
Inside of the custom process file the following code is *required* for the process to run correctly.
```py
from CustomProcessing import Custom

class wiiuName(Custom.Function):
    def createImage(self):
        return Image
```
where `wiiuName` is the exact wiiu key for your associated texture (with space to double underscore replacement) and `Image` is a `SizingImage` -> `Image` object. 
The code inside of createImage is expected to return a completed image after all conversions.

Some important notes are as follows
* since library references are changed/set to true other than a string value the program has no known path from where to read the java/bedrock texture from. Reading of files is handled on a per-custom function basis; you will need to read the file manually inside the code.
* your custom function class can contain any other additional functions you want to add, but createImage must exist and return the completed image; createImage the entry point and exit point for custom processes.

## Custom Process Conventions and Implementaion Details
### Builtin Data
Every custom process has the following **read-only** data attached to it's class data
* wiiuName - the wiiu key name from the associated type library
* type - a "link" type name
    * "link" in this case means "java/bedrock". link type names are different than wiiu type names. link names following the naming convention of the associated version (java/bedrock). For example, the block type in java is "block" but in bedrock it's "block**s**". To get the wiiuType (the type required for making references to any wiiu associated data) run `Utility.wiiuType(self.type)`.
* wiiuImage - the associated wiiu image with the current wiiu name
* isShared - if the current process is a shared or non-shared process

All of the above data can be referenced through `self` or whatever you decide to name the self class reference in the `createImage` function definition. An example function which simply returns the wiiu image as the translation is detailed below
```py
from CustomProcessing import Custom

class wiiuName(Custom.Function):
    def createImage(self):
        return self.wiiuImage
```


### Global Information Access
The TB has a set of "Global" information. The Global.py file has code comments describing what each piece of information means. **Global information should be treated as read-only.**. Global information works like the program's build settings.

Some examples of Global information are the input file path, the output file path, the output structure, the version of minecraft being converted from, etc.

Global information can be accessed by importing `Global` and referencing a variable. 
```py
import Global

print(Global.inputGame)
```

### Printing with Logger
The TB runs all prints through the `Logger.py` module as long as the following import statements are used.
```py
from CodeLibs.Logger import Logger as log
from CodeLibs.Logger import print
```
The `Logger.py` module offers printing logs with an associated "type". A list of types is found in the `Logger.py` file under the `LoggerMode(Enum)` class. These types can be enabled or disabled in the `EntryPoint` in a list as the `logging` argument. Each type has a different print style and set of settings for it.

The following is a code example of printing using `Logger.py`
```py
from CodeLibs.Logger import Logger as log
from CodeLibs.Logger import print

print("Test", log.CHANNELONE) # first print statement
print("Test", log.CHANNELONE, 1) # second print statement
print("Test", log.CHANNELTWO) # third print statement
print("test") # fourth print statement
```
All the print statements will print "test" somewhere int he message. Print types, `CHANNELONE`, `CHANNELTWO` and `CHANNELTHREE` are print channels that are left empty intended for debugging and later being changed to more fitting types (you can use these types for debugging). Each channel has a slightly different print format. 

1. The first print statement prints "    +Test" (with 4 leading spaces).
2. The second print statement prints "     +Test" (with 5 leading spaces). This prints an extra leading space because of the 1 argument. Only some logger types can be intended like this.
3. The third print statement prints "   ++Test" (with 3 leading spaces).
4. The fourth print statement prints "Test" (with nothing added). It uses the default, `PLAIN` type. This should be avoided unless quickly debugging and removing it afterwards.

The following is a code snippet of a list of logger types that could be used in the `EntryPoint` for enabling certain print types. Some print types are enabled by default, including `CHANNELONE`, `CHANNELTWO` and `CHANNELTHREE`.
```py
from CodeLibs.Logger import Logger as log

# ...
logging=[log.CUSTOMFUNCTION, log.CUSTOMFUNCTIONRECURSION],
# ...
```
This could would explicitly enable the `CUSTOMFUNCTION` and `CUSTOMFUNCTIONRECURSION`'s types when entering the program.

### Creating a Blank Image
Sometimes a blank image of a particular color and size is needed. This can generated using the `Utlity.blankImage()` function. 
```py
import Utility as ut

ut.blankImage(100, 200).show()
ut.blankImage(500, color=(255, 0, 0, 255)).show()
```
The above code demonstrates how the `Utility.blankImage` function works by creating and showing
1. an image of size x100, y200 which is transparent and empty
2. an image of size x500, y500 which is the color red

### Reading Images
#### Reading WiiU Images
Before reading a wiiu image ensure that you aren't trying to read the wiiu image associated with the current wiiu name. This image is already provided via `self.wiiuImage`.

The following code is an example of how to read a wiiuImage.
```py
from CustomProcessing import Custom
import Read as rd
import Utlity as ut

class wiiuName(Custom.Function):
    def createImage(self):
        image = rd.readWiiuImage(False, f"{ut.wiiuType(self.type)}\\bat")
        return image
```
The above code reads the wiiu image for a bat. 
Breaking it down:
1. the first argument in `readWiiuImage` is a boolean associated with whether or not the texture is in the wiiu abstract. This essentially means `False` if the texture is on a wiiu sheet and `True` if the texture is all on it's own (not on a sheet).
2. the second argument in `readWiiuImage` is a string which must be a wiiu name. If it's abstract it is in this case, the type must be prepended to the name with an directory break.

Another way to write the same code would be by using the CodeLibs Path class. This is good for more complicated path or paths which must be able to be modified in odd ways.
```py
from CustomProcessing import Custom
import Read as rd
import Utlity as ut
from CodeLibs.Path import Path

class wiiuName(Custom.Function):
    def createImage(self):
        image = rd.readWiiuImage(
            False, 
            Path(
                ut.wiiuType(self.type), 
                "bat"
            ).getPath(withFirstSlash=False)
        )
        return image
```
In this instance, both components of the path (the type and name) are broken into two separate variables and converted by the path class and retrieved without the first slash at the beginning.

#### Reading Java/Bedrock Images
The following code is an example of how to read an image from the input texture pack location (java/bedrock)
```py
from CustomProcessing import Custom
import Read as rd
import Utlity as ut
from CodeLibs.Path import Path

class wiiuName(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(
            self.wiiuName, 
            Path("bat").getPath(), 
            "entity", 
            ut.size(64)
        )
        return image
```
The code above uses the default reading convention for custom processes, the `Read.readImageSingular` function.
1. The first argument is expected to be the current associated wiiu name
2. The second aregument is expected to be a path extension to the targeted texture where the path extention extends a path leading into the associated type. (ex. `"some_pathing\\textures\\entity\\bat"`)
3. The third argument is expected to be the associated type to get to the path extension's image name
4. The fourth argument is the "expected size" of the texture. this is used for determining the texture is the correct size or needs to be rescaled. The size of the bat texture on java (for older versions) is 64x64. The `Utility.size()` function will take a single value, tuple of values, list of values and turn them into a "size tuple" which is the required format for `Read.readImageSingular`.

Once again, this code works but there is another way to do things which is a little simpler. The following code changes the path extension to be simpler since it's contained in one directory only and simplifies the expected size argument. This is possible because mobs in Minecraft often tend to use the same size of texture sheet.
```py
from CustomProcessing import Custom
import Read as rd
import Utlity as ut

class wiiuName(Custom.Function):
    def createImage(self):
        image = rd.readImageSingular(
            self.wiiuName, 
            "bat", 
            "entity", 
            ut.mobsize
        )
        return image
```

### Custom Error Handling
The TB has default error handling for image processing failiures, "fallback handling". This is the behavior that runs for the following scenarios by default:
* the image attempting to be read is not of the expected size it's supposed to be
    * the image is size 20x20 when it's supposed to be 16x16.
* the image attempting to be read was not found or didn't exist
However, this behavior can be handled on a per-custom process basis as well if the specific method would benefit from handling the errors in-method. 

An example of when it would be a good idea to do this is when running a custom process for an atlas of texturs, where, if some textures are missing or missized but not all of them, the image should still construct itself using partially the correct images or otherwise process the incorrect images into correct images. In this case, the fallback handling would simply error the entire texture if any one of the textures could not be found or was not the right size. But handling each error case in-method (for the custom process) allows the TB to more robustly convert this texture.

The TB can raise (throw) 3 potential errors when reading an image. These errors are contained in the `Read.py` file as `Read.notFoundException`, `Read.notx16Exception` and `Read.notExpectedException`. Each of these errors is raised in different, and very specific, scenarios and understanding it fully is crucial in properly handling each error.

It's **important** to note that using `Utility.readImageSingular()` will automatically handle `Read.notx16Exception`s by resizing the images down to the correct size unless the argument `dox16Handling` is set to false. The default value for this argument is true.

#### Not Found Exception - `notFoundException`
`notFoundException`, "not found error" is thrown under the following conditions:
* the texture converter attempted to read a file and found the texture
* the read texture was not the same size as the expected size
    * the size of the texture was not of the same aspect ratio as the expected size
* `Global.errorMode` is set to `"error"`
The default handling of a `notFoundException` is to place a "notFound" texture on the image. The notFound image can be found as `Global.notFoundImage` and is of size x16. This means the notFound image may need to be rescaled before placement.

When a `notFoundException` is thrown it's type lib name should be added to the corresponding global errors list. This is so that when textures encounter errors they are put into the errors document which lists problematic textures out when the program is finished running. The list for `notFoundException` is `Global.notExpectedErrors` which should be `.append()`'ed to with `self.wiiuName` if this is inside of a custom process (`Global.notExpectedErrors.append(self.wiiuName)`).

The following is a code example of placing an error image and appending the the global errors lib.
```py
import Read as rd
import Global
# ...

# try block here
except rd.notFoundException:
    Global.notExpectedErrors.append(self.wiiuName)
    image = Global.notFoundImage.resize(self.wiiuImage.size, doResize=False)
```

#### Not x16 Exception - `notx16Exception`
`notx16Exception`, "x16 error" is thrown under the following conditions:
* the texture converter attempted to read a file and found the texture
* the read texture was not the same size as the expected sie
    * the size was not the same size as the expected size
* `Global.errorMode` is set to `"replace'`
The default handling of `notx16Exception` is to resize the texture to be the expected size and then continue processing with this new image.

When a `notx16Exception` is thrown it's type lib name should be added to the corresponding global errors list. This is so that when textures encounter errors they are put into the errors document which lists problematic textures out when the program is finished running. The list for `notx16Exception` is `Global.incorrectSizeErrors` which should be `.append()`'ed to with `self.wiiuName` if this is inside of a custom process (`Global.incorrectSizeErrors.append(self.wiiuName)`).

The following code is an example of getting the found image from the error and resizing it.
```py
import Read as rd
import Global
# ...

# try block here
except rd.notx16Exception as err:
    Global.incorrectSizeErrors.append(self.wiiuName)
    image = err.getImage().resize(self.wiiuImage.size, doResize=False)
```

#### Not Expected Exception - `notExpectedException`
`notExpectedException` is thrown under the following conditions:
* the texture converter attempted to read a file and could NOT find the texture
    * this could be due to the path being incorrect, the file having a different name, or the file not existing in the texture pack. However, it's assumed that the texture doesn't exist and the path and file name are correct when processing this error because both the path and file name are checked to be correct before attempting to read via `EntryPoint.py` for the file path and the version patches library system for file names.
The default handling of `notExpectedException` is to use the wiiu image so that the file isn't missing from the finished pack. 

No error name is appended for this type of exception because, again, it's assumed that the file just doesn't have a custom texture in this pack and shouldn't exist.

The following code is an example of handling a `notExpectedException`.
```py
import Read as rd
# ...

# try block here
except rd.notExpectedException:
    image = self.wiiuImage
```

### Image Scaling
The texture converter can detect images of the same aspect ratio which are powers of two and scale them up and down to be the correct size when converting textures. This is handled through the `SizingImage.py` class which contains the `SizingImage` class which wraps the needed functions of `PIL`s `Image` class with scaling support. However, this means that all images that are ever read go through scaling changes. 

To ensure all images can be properly processed as sized it's recommended to use the following import statements, where `Image` is called for image processes and `si` is called for image sizing processes
```py
import SizingImage as si
from SizingImage import SizingImage as Image
```

Changes to the reading scale of images is directly controlled by the value `si.processingSize`, however this value *should never directly be modified*, instead use the method `si.changeProcessingSize()` to change the value. This method checks if the provided value is a valid size. This value must be a power of two larger than or equal to 16 up to 64. It's possible that the TB could scale larger textures but it isn't directly supported as to avoid excessively long processing times and lack of ability for certain consoles to handle larger texture packs without crashing.

The processing size can be retrieved as `si.processingSize`. This will be a pixel count value. The "multiplier" can also be retrived with `si.getMultiplier()`. This is a value to multiply the original texture by which results in it's size being the correct larger size. You can check if resizing is needed with the `si.resizingNeeded()` function which returns a boolean, true if resizing is needed.

However, the aforementioned functions become almost entirely obsolete due the following features:

#### Controlling Resizing During Texture Reading
You can control whether or not an image is resized when reading an image by setting `doResize=False` (which has a default value of True) when reading an image. This means the expected size is the size that the image must be exactly (unless it automatically goes through x16 handling via the `Utility.readImageSingular()` function).

This is desirable when an image being read should never be resized from x32, x64, etc.

#### Modifying Sizes Before Texture Reading
You can control the expected size of the image being read by using different `si` functions. Each function explains itself by it's name but they're listed out here regardless. *These are the functions that should be used for size handling when `doResize` is not an option*; these functions are the highest level handling for sizes outside of `doResize` and are the easiest to work with. 

`si.convertInt()` - converts an integer upwards from the regular size to the modified size
`si.deconvertInt()` - converts an integer from the modified size down the the regular size 
`si.convertTuple()` - converts a tuple's value upwards from the regular size to the modified size
`si.deconvertTuple()` - converts a tuple's values from the modified size down the the regular size

This is desirable when an image being read should be resized only sometimes but not always from x32, x64, etc.

#### So How Do I Manage Image Scaling?
**Generally speaking, the TB will automatically handle all size differences; methods should be written with their x16 size requirements and the TB will automatically scale them in most cases.** However, sometimes the TB will have issues where a texture is compoundingly resized making it much too large or causing other processing issues. The following facts should be rememebered when troubleshooting why a custom process may be breaking when changing the processing size.
* all wiiu images that are read are automatically upscaled. This means that a wiiu image with size x16 will be converted to an image of size x32 if the processing size is set so. This, then, means that referencing `self.wiiuImage.size` will result in a *non-constant size* that changes depending on the processing size.
* all images read with with the `Read.py` functions will be automatically upscaled to the processing size unless `doResize` is set to false.

Generally, every sizing error will fall into either of the described issues above in some form or another. Check the sizes of images during the custom process during debugging to understand where an image may be being duplicately upscaled.

### Checking Versions
Sometimes a custom process must handle both Versional aspects and standard custom process aspects. If a texture requires both a custom process and a versional difference it's version checking must be handled inside of the associated custom process.

A code example is detailed below
```py
from CustomProcessing import Custom
import Utility as ut

class wiiuName(Custom.Function):
    def createImage(self):
        if (ut.checkVersion(15, 1, direction=False)):
            # do old code
        else:
            # do new code
```
The code above checks the version (given as integers) in the funtion against the Global version. Let's break it down.
1. The first argument is the "major version". For example it's the "13" in "1.13.2".
2. The second argument is the "minor version". For example, it's the "2" in "1.13.2".
3. The third argument is the direction to check from. 
    * By default, `Utility.checkVersion` checks equal-and-up (inclusive).
    * In this case `direction` is set to `False` meaning that it will check if the Global input version is equal to "1.15.1" and older.
    * More robust version checking can be handled with `Utility.compareVersions()` but is almost never necessary.


### Per-Pixel Functions
Sometimes images must be handled on a per-pixel basis, where a particular opertion is to be performed on every pixel in the image. This can be done with the `Utility.forEveryPixel()` function.
```py
from CustomProcessing import Custom
import Utility as ut

class wiiuName(Custom.Function):
    def createImage(self):
        someImage = ut.blankImage(499, color=(0, 255, 0, 255)) # blank green image for testing

        # for every pixel function
        def setEvery4OddPixelsToOffWhite(pixel, x, y, image, args):
            count = args # use args as count
            
            if (((y * image.width) + x) % 2) == 1: # if the current pixel is odd
                if (count[0] == 4): # if it's the 4th pixel odd 
                    pixel = (255, 255, 255, 255) # set color
                    count[0] = 0 # reset count
                else: count[0] += 1 # increment count
            return pixel # always return the pixel

        # run for every pixel
        newImage = ut.forEveryPixel(
            someImage, 
            setEvery4OddPixelsToOffWhite,
            arguments=[0]
        )

        # show result
        newImage.show()
```
The code above is a relatively complex example. Let's break it down.
1. The first block of code creates an image of size 499 which is fully green.
2. The second block of code defines a function to the requirements of the `Utility.forEveryPixel()` for executing a function for every pixel. The function must have the following properties
    1. Argument 1 will be a pixel (length 4 tuple of color data)
    2. Argument 2 will be the x position of the current pixel
    3. Argument 3 will be the y position of the current pixel
    4. Argument 4 will be the image currently being processed. Depending on if `useExistingImage` is set to True (it's False by default) this will either be a static image or imaging that is modified as the function proceeds
    5. Argument 5 will be a argument dedicated for additional arguments which will hold their data outside of the `Utility.forEveryPixel()` function; this data is is not destroyed after each pixel.
    * The funtion must *always* return a pixel. To return the same pixel as was started with just return Argument 1 (`return pixel` in this case). 
3. The third block of code runs the `Utility.forEveryPixel()` function on the given image `someImage` and passes it an integer wrapped in a list.
    * Wrapping the integer in a list turns it into a reference type so that it holds its value between iteratios.

What `Utility.forEveryPixel()` does is run a function for every pixel of an image and passes it any extra arguments.

In this case, the function `setEvery4OddPixelsToOffWhite` is run for every pixel in the image. What this function does is set every 4th found odd pixel to an off-white color. More specificallt, it executes the following
* set the arguments to the count variable (makes code more readable)
* check if the current pixel is an odd pixel
    * getting `((y * image.width) + x)` simply gets the current pixel as if it were an index in a single-dimensional list of pixel
* checks if the count is 4 and sets the color of the current pixel and resets the count if it is.
* if the count wasn't 4 then increment the count by 1
* return the pixel (required)

### Sheet Handling
Sometimes images need to be accessed as if they were "(sprite) sheets" composed of multiple images. When this is the case the `SheetExtractor` class of `Sheet` can be used.
```py
from CustomProcessing import Custom
import Utility as ut
from CodeLibs.Path import Path
from Sheet import SheetExtractor

class wiiuName(Custom.Function):
    def createImage(self):
        sheet = SheetExtractor(ut.blankImage(100, color=(255, 255, 255, 255)), ut.size(10))
        sheet.extract((0, 0)).show() # the first 10x10 block

        sheet.insert( # insert an image oversized to the the width of the image x the subsize Y * 2 to block 0, 4
            (0, 4), 
            ut.blankImage(
                sheet.sizeXPix, 
                (sheet.subSizeYPix * 2), 
                color=(255, 0, 0, 255)
            )
        )

        sheet.extract((9, 0), (1, 10)).show() # the 10 blocks on the rightmost of the image
```
The code example above shows one use of the sheet extractor. The code example:
* creates a sheet out of a blank white image of size 100 where the sheet is split into 10x10 blocks. 
* Gets the first 10x10 block out of the image and shows it
* replaces 20 blocks of the image with red
    * moves to block (x0, y4) and places a blank image
    * the blank image is of the size (the x size of the whole sheet, the y size of one subsection of the sheet multiplied by 2)
    * the blank image is colored red
* extracts the 10 10x10 blocks on the rightmost side of the image from top to bottom and shows them

`SheetExtractor` can be initalized multiple ways; it doesn't need to be an image being passed as an argument. Some examples are detailed below.

`SheetExtractor` created using an image reference
```py
SheetExtractor(ut.blankImage(100, color=(255, 0, 0, 0)), ut.size(10))
```

`SheetExtractor` created using a size
```py
SheetExtractor(ut.size(100), ut.size(20))
```

`SheetExtractor` created using an image reading. When this is true SheetExtractor will assume the reading behavior of `Utility.readImageSingular()`
```py
SheetExtractor(Path("map_icons"), ut.size(8), self.wiiuName, "map", ut.size(128))
```
In this particular example, `SheetExtractor` reads from `"map\\map_icons"` for an image sized 128x128 split into subsections of 8

### Referencing Shared or Psuedo-Shared Custom Proccesses
Shared custom processes cannot be directly references through a base libary reference. Instead they must be accessed by passing the image creation execution from a non-shared custom process. This is also how psuedo-shared custom processes are referenced
```py
from CustomProcessing import Custom

class wiiuName(Custom.Function):
    def createImage(self):
        return Custom.runFunctionFromPath(
            "shared", 
            "some_function", 
            self.wiiuName, 
            self.type, 
            self.wiiuImage, 
            isPrintRecursed=True
        )
```
The above code is an example of running a shared function.
1. The first argument is the type of function it is. This can be shared, external, abstract, override, and versional
2. The second argument is the name of the function (file/class name, they should both be the same)
3. The third argument is a required pass of wiiuName
4. The fourth argument is a required pass of the type
5. The fifth argument is a required pass of the wiiuImage
6. The 6th argument is the print recusrion status. This should *always* be set to true when running a shared or pseudo-shared custom process.

This function call can also be written with arguments to pass to it. However, it's important to note that **only shared custom processes (not pseduo shared) can take arguments.** this is also reflected in that shared custom functions must be defined with the arguments parameter (`def createImage(self, args)`).
```py
from CustomProcessing import Custom

class wiiuName(Custom.Function):
    def createImage(self):
        return Custom.runFunctionFromPath(
            "shared", 
            "some_function", 
            self.wiiuName, 
            self.type, 
            self.wiiuImage, 
            True, # print recursion
            "some arguments"
        )
```

It's also possible to run a custom process through an instance of itself rather than a direct call to the path to the function. This is rarely used, but useful if a custom process class contains class information that can be referenced globally. This also means a custom function class can be called, modified at runtime and then executed.
```py
from CustomProcessing import Custom

class wiiuName(Custom.Function):
    def createImage(self):
        cls = Custom.getClass("external", "some_function") # get the class
        clsInstance = cls(self.wiiuName, self.type, self.wiiuImage, isShared=False) # create instance of the class
        print(clsInstance.someData) # print some class data from the class
        return Custom.runFunctionFromInstance(clsInstance, isPrintRecursed=True) # run a custom function
```

## What Does This System Mean?
This library systems means the following statements are true
* All convertable textures must exist in a type lib so as to give them an identity
* All convertable textures must have *both* a reference in the Base Bedrock lib and the Base Java lib for conversion
* All textures which require Custom Processes must have a custom function file of the correct format

## How to Update the Overall Supported Versions
To update the overall supported versions of the TB update the max versions for both java and bedrock in the `SupportedTypes.py` file. The `SupportedTypes.py` file controls the TB's detection of valid versions. Some other changes are also required if building for the frotnend including modifying `global\\supported_versions.json` and rebuilding the backend for the frontend. 

