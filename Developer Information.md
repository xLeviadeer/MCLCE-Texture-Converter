# Developer Information
## Developments Needs
The Minecraft LCE Texture Converter is looking for the following developments
- conversion updates for new Minecraft versions as they come out
- "port pack" file write modes for all consoles
- support for all textures being animated
- option to generate upscales with xBR upscaling

## Dependencies
The Texture Converter will prompt you to install it's dependencies automatically only if the xLPyBasics dependency is installed. xLPyBasics is a "closed source" dependency installable here: [https://github.com/xLeviadeer/xLPyBasics](https://github.com/xLeviadeer/xLPyBasics). The project will fail to run without xLPyBasics. If you would not like to use automatic dependency installation or it isn't working for you then you can find a dependencies list in the `pyproject.toml` file.

## Looking to Add Support for Later Versions of Minecraft?
Reference the more in-depth walkthrough of how the TB works [here](https://github.com/xLeviadeer/MCLCE-Texture-Converter/blob/main/Adding%20CustomProcesses.md) to help develop this program.

## How to Execute the Texture Converter with no Interface
To run the TB you must create an instance of `EntryPoint.py` in it's own file.

1. Declare an `EntryPoint` in the file to determine what settings are used during execution. `entry = EntryPoint(…)`
2. Start the program from the `EntryPoint` with `entry.start()`

Cumulatively, an example looks like ⌄
```py
from EntryPoint import EntryPoint
from CodeLibs import Logger as log

# declare a new entry point
entry = EntryPoint(
    errorMode="error",
    processingSize=16,
    useComplexProcessing=False,
    
    inputPath="C:\\my_cool_path",
    inputPathType="folder",
    inputGame="java",
    inputVersion="1.14",
    
    outputPath="C:\\my_cool_output_path",
    outputStructure="wiiu",
    outputDrive="system",

    logging=log.LoggerHandler.DEFAULT_FLAGS,
    isDirectPath=True,
    useErrorTexture=False,
    forceDumpMode=False
)

# run entry point
entry.start()
```

Each setting has the following meanings:
- `errorMode`
    - replace: attempts to build and replace textures which cannot be simply copied
    - error: places an error texture over textures which cannot be simply copied
- `processingSize`
    - controls the expected input size and output size of textures. the TB will upscale/downscale textures of incorrect sizes.
    - integers other than powers of 2 are not supported, and not tested outside of 16 - 64
- `useComplexProcessing`
    - controls whether to use complex processing for certain textures
    - complex processing can result in excessively long (upwards of 8 minutes) processing times if used with large sizes (like x64 or greater)
- `inputPath`
    - filepath to the textures to be translated
- `inputPathType`
    - the type of file/folder the inputPath leads to
    - folder
    - mcpack
    - zip
- `inputGame`
    - the game to be translated from
    - java
    - bedrock
    - any lce format
- `inputVersion`
    - the game version of the to-be-translated textures
- `outputPath`
    - file-path of where to output textures
- `outputStructure`
    - the output file structure, used to determine which ConsoleWriter mode to use
    - selects a build mode (build/dump) and a console to write to
    - options for this are equal to the elements in the list under `global/output_structures_‹console›`
- `outputDrive`
    - determines, when using build mode, whether to name the main file as usb or mlc
    - system
    - usb
- `logging` (optional)
    - a list of LoggerModes which would be printed
- `isDirectPath` (optional)
    - whether or not (both) inputPath and outputPath are direct paths; paths which lead to the "texture" or "textures" folder exactly.
    - controls whether the program will look for valid subfolders of texture packs to locate the texture pack contents.
- `useErrorTexture` (optional)
    - whether or not to write an error texture when a custom process cannot be found.
    - used for debgugging when adding new supportedTypes to allow the completion of execution even with missing processes.
- `forceDumpMode` (optional)
    - whether to force the program to output in dump mode regardless of the build/dump status.

## Programmer Information
### Warning About Internal Paths
Paths inside of *internal only* files weren't made with the intention of being used outside of a personal environment and hence may contain specific file-paths which need to be changed in order for the method to function correctly. Internal only files include `Internal.py` and `Entry_Internal.py`

### Overview
To run to the TB (texture builder), an `EntryPoint` must be declared. 
- Some examples of this can be found in `Entry_TestJava.py` and `Entry_TestBedrock.py`.
- `Entry_Program.py` is used for running the program from the frontend.
- `Entry_Internal.py` is used to execute backend functions to manage databases and check them for errors.

The TB goes through the following steps during execution
1. **Interpret** settings declared in the `EntryPoint.py`.
2. **Run** the `TextureCreator.py` which is the overall algorithm to translate/convert textures.
    - if a texture which cannot simply be copied is found, run `CustomProcessing/` on it.
3. **Export** the textures to the output folder.

### Sheets vs Abstracts
The TB classifies certain textures as "**sheets**" aka "atlases". Generally, textures which require custom processing that are part of sheets are called "external textures".

The TB classifies certain textures as "**abstract**" aka standalone textures. Abstract textures can also be sheets/atlases if the sheet/atlas contains an animation for a singular texture rather than multiple separate textures.

Both sheets and abstract textures use fundamentally different processing methods to translate hence why they aren't one and the same.

### Program Portions
The TB is divided into a few core portions
- **Frontend** - user interface
- **Backend** - processing, non-user interface
    - **Build** - process the texture pack according to the databases and custom process library
    - **Databases** - a set of databases to store information about texture locations and processing specifications
    - **Internal** - test functions and processes for debugging and creating databases

### The Job of Each File
#### TextureLibs > EntryPoint.py
Module for defining settings, preparing and executing the program
#### TextureLibs > Global.py
Stores run-time specific settings data which can be accessed anywhere in the program
#### TextureLibs > Internal.py
*internal only*, holds all debug functions
#### TextureLibs > Read.py
Holds functions for reading databases, images, etc.
#### TextureLibs > Sheet.py
Sheet extraction class, used for handling (copy, pasting) parts of an image which is a sheet/atlas of multiple textures
#### TextureLibs > SizingImage.py
Extends/Replaces PIL's Image class to allow upscaling and downscaling of images
#### TextureLibs > SupportedTypes.py
A list of supported types and supported versions the program will run
#### TextureLibs > TextureCreator.py
Module to create and write textures.
#### TextureLibs > TextureUtility.py
Random utility functions
#### TextureLibs >  ConsoleWriter.py
Module to organize and format different output write locations.
#### base_textures/
Folder expected to contain base game textures named as `"{version}_{game}"` where the folder directly contains the contents of the "texture" or "textures" folder. Ex. `"./base_textures/1.14_java/block/grass_block.png"` would be a valid path. Contents of the `base_textures` folder aren't provided to ensure the saftey of this program. This folder also contains base game textures
#### CodeLibs > Logger.py
Extends/Replaces python's `print` function to include multiple different print types which can be enabled or disabled in the `EntryPoint.py` for more effective debugging.
#### CodeLibs > Path.py
Module with class to create and manage file-paths.
#### color_signatures/
*internal only*, folder containing information about the color data of textures for creating `linked_libraries`.
#### CustomProcessing > Custom.py
Handling for locating and executing CustomProcessing file functions.
#### CustomProcessing/
Folder of custom processes for textures which cannot simply be copied separated by game and type.
- **External** - Texture which is part of a large texture sheet (atlas) but requires a rebuilding (translation) process.
- **Abstract** - Texture which is on it's own and requires a rebuilding (translation) process.
- Override - Texture which is on it's own and can replace a texture sheet (atlas).
- **Versional** - Texture which changes processing based on the version. It's important to note that Versional processes are only used if the texture isn't already External or Abstract, in which case the versional difference programming will be within the Abstract or External process.
- **None/Shared** - Inspecific (not directly related to one texture) process for processing multiple of a particular type of texture.
#### equality_libraries/
*internal only* information and databases for comparing the equality of prospective texture libraries and verified (as correct) texture libraries.
#### global/
Small databases containing information that corresponds with the Frontend for display of user options.
#### Info/
Folder containing information about the program or certain processes
#### InterfaceLibs > …
Interface classes used to construct and manage the interface
#### linking_libraries/
Libraries of data regarding game textures and how to translate them between versions. Generated with assistance via `color_signatures`.
#### output/
*internal only* folder for testing output.
#### resources/
*internal only* files created while making image resources for the program.