from TextureLibs.EntryPoint import EntryPoint
from CodeLibs import Logger as log
import TextureLibs.Global as Global

# set the name (must be set in the entry file)
Global.name = str(__name__)

# declare new entry point
entry = EntryPoint(
    errorMode="replace",
    processingSize=16,
    useComplexProcessing=True,
    
    inputPath="",
    inputPathType="folder",
    inputGame="wiiu",
    inputVersion="1.13.2",
    
    outputPath="F:\\Coding\\Ab- LeRe\\MCWiiU-Texture-Builder\\MCLCE Texture Builder - Standalone\\output",
    outputStructure="wiiu dump",
    outputDrive="system",

    logging=[],
    showTracebacks=False,
    isDirectPath=True,
    useErrorTexture=False,
    forceDumpMode=True
)

# run entry point
entry.start()