# Minecraft LCE Texture Converter
The MCLCE Texture Converter is a texture conversion tool to convert texture packs from Minecraft Java or Minecraft Bedrock to Minecraft LCE. It can review textures which may not immediately be in the correct format and "rebuild" them so they meet format specifications.

![program-image](https://github.com/xLeviadeer/MCLCE-Texture-Converter/blob/main/.github/images/program_image.png)

## Why Use the Texture Converter?
Texture conversion at first seems simple. The problem looks like just copying and pasting textures into the right locations for different consoles. However, this isn't the case in actuality. 

The Minecraft LCE Texture Converter handles converting from dozens of different input versions of both Java and Bedrock edition. And it converts all of those versions to several different LCE editions and versions. Where different size constraints may also exist like x16 and x32.

Additionally, many textures require complex specialized processes. Take the two bed textures below.

#### bed on java

![red-java-bed](https://github.com/xLeviadeer/MCLCE-Texture-Converter/blob/main/.github/images/java_red_bed.png)

#### bed on lce

![generic-lce-bed](https://github.com/xLeviadeer/MCLCE-Texture-Converter/blob/main/.github/images/lce_generic_bed.png)

The bed texture needs to be transformed to have the correct UV mappings. Additionally, LCE's bed texture is generic and Java only has colored bed textures. Suppose a pack only provides some of the bed colors not including a white bed texture? Which texture should be used for normalizing into a generic bed texture?

The job of the Minecraft LCE Texture Converter is to account for all of these possible permutations and give the best resulting texture conversion.

## Features
- [x] Converts all plain textures
- blocks
- animated blocks
- items
- animated items
- entities
- particles
- environment
- misc
- [x] Supports x16, x32 and x64 conversion sizes
- [x] Supports converting from versions 1.13.2 and newer*
- Minecraft Java Edition
- Minecraft Bedrock Edition
- [x] Supports converting to the newest version of each LCE version
- Minecraft WiiU Edition
- Minecraft Nintendo Switch Edition
- Minecraft Xbox 360 Edition
- Minecraft Xbox One Edition
- Minecraft Playstation Vita Edition
- Minecraft Playstation 3 Edition
- Minecraft Playstation 4 Edition
- [x] Different error modes for replacing textures

## Installation
#### Download
The texture builder can be installed with the official interface [here in the releases section](https://github.com/xLeviadeer/MCLCE-Texture-Converter/releases). Download the zip file started with `Minecraft.LCE.Texture.Converter` and run the `MC LCE Texture Converter.exe` to start the program.

#### Run and Configure
You can find help for configuring the program once it's open [here](Help%20Configuring.md) which also can be found when pressing "Help and Info" under the "Advanced" section of the program.

#### Supported Operating Systems
This program is only supported on Windows. It is expected to not function on MacOS and has not been tested on Linux.

## Looking to Develop?
Access the [Developer Information](Developer%20Information.md) file for more information about development.

## Authors
created by: xlevia

discord user: `xlevia`

[discord server](https://discord.gg/eJqhbPDkqZ) ╎ [github](https://github.com/xLeviadeer/MCLCE-Texture-Converter)

contributors ⌄
- [Leviah](https://github.com/xLeviadeer)
