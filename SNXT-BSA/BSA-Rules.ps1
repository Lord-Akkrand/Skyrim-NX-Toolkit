# Formats of DDS textures
# (FourCC, LongName)
# Some textures don't have a FourCC, I have made one up for them

$DXT1 = ('DXT1','BC1_UNORM')
$DXT5 = ('DXT5','BC3_UNORM')
$BC4U = ('BC4U','BC4_UNORM')
$RGBA = ('RGBA', 'R8G8B8A8_UNORM')
$BGRA = ('BGRA', 'B8G8R8A8_UNORM')
$R8UN = ('R8UN', 'R8_UNORM')
$DX10 = ('DX10','BC7_UNORM')
$DX10_SRGB = ('SRGB', 'BC3_UNORM_SRGB')

$Formats = @($DXT1, $DXT5, $BC4U, $RGBA, $BGRA, $R8UN, $DX10, $DX10_SRGB)


# Depending on whether the user has the SDK, convert textures from some formats to others.
$ConvertFromTo = @{
    "DX10" = $DXT5
    "BGRA"= $RGBA
    "BC3_UNORM_SRGB" = $DXT5
}

$ConvertFromToSDK = @{
    "DX10" = $DXT5
    "R8UN"= $DXT1
    "BC3_UNORM_SRGB" = $DXT5
}

# RuleSets for resizing textures
$RuleSets = @{}

# As an example, the dragon skeleton textures are 2048^2 on Switch, and stored in /actors/dragon/dragonskeleton.dds
# There can be gaps in it - for example, the following would also match /actors/dragon/something/dragonskeleton.dds
# But all elements must be in the order specified


$BaseRules = @(
    @{
        "Name" = "Default"
        "Path" = @(".*\.dds")
        "Size" = 512*512
     },
    @{
        "Name" = "Architecture"
        "Path" = @("\barchitecture\b")
        "Size" = 1024*1024
     },
     @{
        "Name" = "Landscape"
        "Path" = @("\blandscape\b")
        "Size" = 1024*1024
     },
     @{
        "Name" = "Actors"
        "Path" = @("\bactors\b")
        "Size" = 2048*2048
     }
)

$RuleSets['Base'] = $BaseRules

# AdPDDs.exe Resizing Rules
$AdPDDsRules = @(
    @{ 
        Name="Compress"
        Options = @{
            Check=0
            Compress=1
        }
    },
    @{ 
        Name="LayerProcessing"
        Options = @{
            Software=0
        }
    },
    @{ 
        Name="IfNoMaskCompress"
        Options = @{
            No=0
            DXT1=1
            DXT3=3
            DXT5=5
            Preserve=9
        }
    },
    @{ 
        Name="IfMaskIs1BitCompress"
        Options = @{
            No=0
            DXT1=1
            DXT3=3
            DXT5=5
            Preserve=9
        }
    },
    @{ 
        Name="IfMaskIsTranslucentCompress"
        Options = @{
            No=0
            DXT1=1
            DXT3=3
            DXT5=5
            Preserve=9
        }
    },
    @{ 
        Name="MakeMipmaps"
        Options = @{
            Delete=0
            Yes=1
            Rebuild=2
            Preserve=9
        }
    },
    @{ 
        Name="FixBadSize"
        Options = @{
            No=0
            Yes=1
            '16x16'=2
            '32x32'=3
            '64x64'=4
        }
    },
    @{ 
        Name="FixAlphaChannel"
        Options = @{
            No=0
            Yes=1
            SetInvisible=2
        }
    },
    @{ 
        Name="MinimizeWhiteoutLoss"
        Options = @{
            No=0
            '4x4'=1
            '8x8'=2
            '16x16'=3
        }
    },
    @{ 
        Name="DeleteClones"
        Options = @{
            No=0
            Delete=1
        }
    },
    @{ 
        Name="ResizeIf"
        Options = @{
            No=0
            All=1
            '256'=2
            '512'=3
            '1024'=4
            '2048'=5
            '4096'=6
            '8192'=7
        }
    }
    @{ 
        Name="Unused"
        Options = @{
            Unused=0
        }
    }
)

$AdPDDsRuleSet = @{
    Compress="Compress"
    LayerProcessing="Software"
    IfNoMaskCompress="DXT1"
    IfMaskIs1BitCompress="DXT1"
    IfMaskIsTranslucentCompress="DXT1"
    MakeMipmaps="Rebuild"
    FixBadSize="No"
    FixAlphaChannel="No"
    MinimizeWhiteoutLoss="No"
    DeleteClones="No"
    ResizeIf="No"
    Unused="Unused"
}

