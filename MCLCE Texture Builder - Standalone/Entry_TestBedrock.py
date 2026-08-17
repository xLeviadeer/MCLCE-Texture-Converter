from TextureLibs.EntryPoint import EntryPoint
from CodeLibs import Logger as log

# declare new entry point
entry = EntryPoint(
    error_mode="replace",
    processingSize=16,
    useComplexProcessing=True,
    
    inputPath="F:\\Coding\\Ab- LeRe\\MCWiiU-Texture-Builder\\MCLCE Texture Builder - Standalone\\base_textures\\1.6.1.0_bedrock",
    inputPathType="folder",
    inputGame="bedrock",
    inputVersion="1.6.1.0",
    
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