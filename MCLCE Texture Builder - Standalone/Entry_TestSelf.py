from TextureLibs.EntryPoint import EntryPoint
from CodeLibs import Logger as log

# declare new entry point
entry = EntryPoint(
    error_mode="replace",
    processingSize=16,
    useComplexProcessing=True,
    
    inputPath="",
    inputPathType="folder",
    inputGame="wiiu",
    inputVersion="1.13.2",
    
    outputPath="F:\\Coding\\Ab- LeRe\\MCWiiU-Texture-Builder\\MCLCE Texture Builder - Standalone\\output",
    outputStructure="wiiu dump",
    outputDrive="system",

    logging=log.LoggerHandler.DEFAULT_FLAGS,
    isDirectPath=True,
    useErrorTexture=False,
    forceDumpMode=True
)

# run entry point
entry.start()