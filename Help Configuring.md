# Help Configuring

## Contents
- [Help Configuring](#help-configuring)
    - [Input Settings](#input-settings)
    - [Output Settings](#output-settings)
    - [Advanced Settings](#advanced-settings)
- [Help Converting](#help-converting)
    - [help it says my build failed](#help-it-says-my-build-failed)
    - [help the convert button is grey](#help-the-convert-button-is-grey)
    - [Logger Flags](#logger-flags)

--- 
## Help Configuring 

### Input Settings
The **text field, browse input button, and large rounded square** are for the **path to the textures you want to convert from**

The **convert from drop-down** determines what game you will be converting from. One set of options for conversion are *modern versions* ⌄
- java folder: your texture pack is a folder of java resource pack 🜿 don't navigate directly into the textures folder 𐑶
- java .zip file: your texture pack is a zip file containing a java resource pack
    - java .zip files may take longer to convert at the start, don't worry if the progress bar gets stuff for a minute
- bedrock folder: your texture pack is a folder of a bedrock resource pack
- bedrock .mcpack file: your texture .mcpack file containing a bedrock resource pack
    - bedrock .mcpack files may take longer to convert at the start, don't worry if the progress bar gets stuff for a minute

Other, *lce versions* may be generated. This exists so that you cannot accidentally delete your textures and lose them. The Texture Converter can create a pack containing the base game textures. Some adjustments have been made to correct errors with the original textures 🝗 fixing the position of conduit power particles, ⌯ 𐑶 ⌄
- xbox one/nintendo switch default textures
- wiiu default textures
- xbox360/ps3/psV default textures
- ps4 default textures

The **version dropdown** must be set to **match the version your texture pack you are converting is intended for** 🜚 1.13, 1.14, ⌯ 𐑶. If your version is not specifically listed *pick the listed version that is underneath your version*. *if you don't know the version* then *picking any version will allow texture version to complete*. However, some textures may fail to properly convert. You can use the ⟨show log⟩ button to see your textures being processed in realtime and determine which textures have not been converted. 

### Output Settings
The **text field and browse output button** are for the **path to where you want your converted textures to go**

The **convert to drop-down** determines in what format your textures will come out as. Since what your textures are converted to depends on what you are converting from you will not be able to select it until you choose ⟨convert from⟩ ⌄
- a *dump* places all converted textures into simple mostly unested folders
- a *port pack* is a reconstruction of the file system for your console so you can paste in the generated textures folder at your console root and replace all of your existing textures
- a *modpack* is a console-specific file structure to be used with modding tools for the console 🜚 sdcafiine on wiiu 𐑶

the **open output** button **opens the output folder you selected**

### Advanced Settings
The **output drive drop-down** is a console specific setting which is used when generating *port packs* that determines whether to structure files such that they should replace a **system or usb** downloaded game

The **build mode drop-down** is a mode selector for size based error handling behavioral changes during texture generation ⌄
*in ⟨replace⟩ mode*, the program is forced to generated a pack with fully completed textures ⌄
- crops animated textures that are not animated in the vanilla game
- interprets ambiguous textures into an an subjectively correct form
- upscales/downscales textures that are not the correct size
- always creates ⸉mipmap⸉ textures 

*in ⟨error⟩ mode*, the program generates textures which can be deterministally convert but replaces anything that cannot be with an error texture. Error mode should be used if you want to automatically convert all textures which can be converted directly but leave all textures which cannot be open for you to go in and edit yourself ⌄
- places errors for textures that are animated which are not animated in the vanilla game
- places an error for ambiguous textures
- places errors for textures which are not the correct size
- does not create mipmaps unless no error textures had to be placed on the respective sheet 

The **size mode drop-down** changes the expected input size and the concrete output size of textures. Standard textures are x16 but some texture packs may have higher resolution textures ⌄
- input textures may error or be upscaled/downscaled depending on the ⟨build mode⟩
- output textures will always match the selected size mode

Size mode has an option for ⸉simple processing⸉ which should generally be used when available but with caveats: ⟨Simple processing⟩ changes the algorithm which some textures use to convert. This can massively reduce the amount of time it takes to convert textures but may reduce the technical texture quality. The behavior changes which occur due to simple processes are complex differences that occur on a case-by-case basis. Some examples of changes that occur due to simple processing ⌄
- in LCE kelp is normally invisible background pixels are used for the transition between single animation textures, requiring invisible pixels to be set with appropriate colors ⌄
    - in simple mode: invisible pixels are set via a color average function of the entire kelp animation texture
    - in non-simple mode: invisible pixels are set via a square blurring algorithm which smooths the known texture colors into the invisible space
    - caveat of simple mode: It is fine for kelp textures which maintain a consistent color across the animation but if you used╌say╌a rainbow kelp animation then the average color would become something like brown or black which isn't represenative of the texture
- rain in minecraft bedrock edition is generated via an algorithm which sets single drops to fall down as opposed to LCE and java's system where a predetermined rain texture is used. When converting from bedrock only ⌄
    - in simple mode: rain is placed in a collection of pretermined random-like locations on the texture sheet
    - in non-simple mode: rain is placed via a complex algorithm which considers the shape of the rain textures and ensures that each raindrop is distributed locally randomly and broadly regulary across the texture to ensure drops may never broadly cluster, end up outside of the texture bounds or overlap while still being randomly placed
    - caveat of simple mode: rain textures cannot be placed too close to the edges of the texture to ensure that the maximum size texture never is placed out of bounds and the raindrop placement is not truly random

The **show log button shows a log of process notes** about texture conversion as it occurs. The log must be open to start seeing any generation logs. 

The **clear output folder button clears the given output folder of ¡all¡ files**. Cleared files are attempted to be sent to your recycle bin but if they cannot be they will instead be deleted permanently. You should clear the output folder if you will be converting a new pack different from the one you last converted. 

---
## Help Converting
This tool is only officially supported on Windows and may not function correctly on other operating systems.

### help it says my convert failed
- ensure your input path is actually a texture pack
- open the log by pressing ⟨show log⟩ under ⟨advanced/more settings⟩ and try to convert your pack again. You should see a bunch of text appear in the log. It may give some hints as to why your pack is failing to convert
- ensure the convert-from game is correct. if it's a java pack you must select java. if it's a bedrock pack you must select bedrock.
- ensure that the correct convert-from version is selected to match your texture pack's version
- if you cannot resolve the issue then please create a new issue here⊶[https://github.com/xLeviadeer/MCLCE-Texture-Converter/issues](https://github.com/xLeviadeer/MCLCE-Texture-Converter/issues)⊷. Describe your issue. If you want help you MUST attach the pack you are trying to convert from and a copy of your logs from ⟨show log⟩.

### help the convert button is grey
The convert button is greyed out only if all necessary options to convert your pack have not been selected. The required options are highly variable and may change depending on what other options you have selected. Go through and select an option for anything that not greyed out and unselectable. 

### Logger Flags
The MCLCE Texture Converter supports adding additional logging flags to your logger. To do so add items to the logger list in `logging.json` that sits next to the program `.exe`. Valid log items are given ⌄
- veryimportant
- important
- exit
- error
- warning
- log
- debug
- note
- plain
- section
- channelone
- channeltwo
- channelthree
- customfunction
- customfunctionrecursion
- customfunctiontiming
- pathfunction
- customweather
- debugtwo
- debugbracketrandom