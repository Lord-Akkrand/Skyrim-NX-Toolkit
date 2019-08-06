#! python3

'''
I've been pretty harsh in my resizing policy.  

There are ~32000 textures in Skyrim SE
On PC, 
	1500 are greater than 1024x1024.
	Mean is 298331, which is about 546x546
	Median is 65536
	Std. Dev is 843449
On Switch, 
	68 are greater than 1024x1024.
	Median is 32768
	Std. Dev is 319954


in a "menu"-folder: User-interface element, alpha is element-mask
in a "landscapelod"- or "terrain"-folder: World-space normal-map for terrain, no alpha
"_n"-suffix: Tangent-space normal-map, alpha is specularity
"_msn"-suffix: Model-space normal-map, no alpha
"_g"-, "_glow"- or "_emit"-suffix: Glow-map, alpha is a mask
"_hh"-suffix: Gloss-map for hair, no alpha
"_hl"-suffix: Detail-map for hair, alpha is opacity
"_m"-suffix: Reflectivity-map for light-sources, no alpha
"_em"- or "_envmap"-suffix: Reflectivity-map for environment-maps, no alpha
"_e"-suffix: Environment-map (some are planar, some are cube-maps), no alpha
"_b"- or "_bl"-suffix: Backlight-map, no alpha
"_s"-suffix: Specularity-map for skins, no alpha
"_sk"-suffix: Tone-map for skins, no alpha
"_p"-suffix: Parallax-map, no alpha
"_d"-suffix: Diffuse-map, alpha is opacity
"_h"-suffix: Haze-map, alpha is unknown
All others are color-map, alpha is opacity or parallax


'''
DXT1 = ('DXT1','BC1_UNORM')
DXT5 = ('DXT5','BC3_UNORM')
BC4U = ('BC4U','BC4_UNORM')
RGBA = ('RGBA', 'R8G8B8A8_UNORM')
BGRA = ('BGRA', 'B8G8R8A8_UNORM')
R8UN = ('R8UN', 'R8_UNORM')
DX10 = ('DX10','BC7_UNORM')
DX10_SRGB = ('BC3_UNORM_SRGB', 'BC3_UNORM_SRGB')
R8G8UN = ('R8G8_UNORM', 'R8G8_UNORM')

Formats = []
Formats.append(DXT1)
Formats.append(DXT5)
Formats.append(BC4U)
Formats.append(RGBA)
Formats.append(BGRA)
Formats.append(R8UN)
Formats.append(DX10)
Formats.append(DX10_SRGB)
Formats.append(R8G8UN)

Rules = {}

# As an example, the dragon skeleton textures are 2048^2 on Switch, and stored in /actors/dragon/dragonskeleton.dds
# There can be gaps in it - for example, the following would also match /actors/dragon/something/dragonskeleton.dds
# But all elements must be in the order specified

#Rules.append({"Name":"ExampleDragon", 'Path':[r'\bactors\b', r'\bdragon\b', 'dragonskeleton.dds'], 'Size':2048*2048})

BaseRules = []

BaseRules.append({"Name":"Actors", 'Path':[r'\bactors\b'], 'Size':2048*2048})
BaseRules.append({"Name":"Pandorable", 'Path':[r'\bPandorable\b'], 'Size':2048*2048})

Rules['Base'] = BaseRules
# If you come across a texture that is the following type, convert it to the other type

ConvertFromTo = []
ConvertFromTo.append(('DX10',DXT5))
ConvertFromTo.append(('BGRA',RGBA))
ConvertFromTo.append(('BC3_UNORM_SRGB',DXT5))
ConvertFromTo.append(('BC4U',DXT5))
ConvertFromTo.append(('R8G8_UNORM',DXT5))


ConvertFromToSDK = []
ConvertFromToSDK.append(('R8UN',DXT1))
ConvertFromToSDK.append(('BC3_UNORM_SRGB',DXT5))
ConvertFromToSDK.append(('DX10',DXT5))
ConvertFromToSDK.append(('BC4U',DXT5))
ConvertFromToSDK.append(('R8G8_UNORM',DXT5))


