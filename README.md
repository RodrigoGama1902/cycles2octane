# Cycles2Octane Material Converter

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Blender](https://img.shields.io/badge/Blender-3.3-orange.svg)](https://www.blender.org/download/releases/3-3/)
[![Octane](https://img.shields.io/badge/Octane-26.5-red.svg)](https://render.otoy.com/forum/viewtopic.php?f=113&t=80550/)

## Overview

Convert Cycles Materials to Octane Materials in Blender with a single click.

![Converting](img/converter.gif)

## Features

- **Single Click Conversion**: Convert Cycles materials to Octane materials with a single click.
- **Reverse Conversion**: Convert Octane materials back to Cycles materials.
- **Support for Blender 3.3**: Fully compatible with Blender 3.3 and earlier versions.

## Installation

1. Download the addon from the [releases page](#).
2. Open Blender and go to `Edit > Preferences`.
3. Select `Add-ons` and click `Install`.
4. Choose the downloaded `.zip` file and click `Install Add-on`.
5. Enable the addon by checking the box next to `Cycles2Octane`.

## Usage

1. Go to the add-on panel located in the `Octane` tab.
2. Select the conversion method.
3. Click the `Convert Material Nodes` button.

![Panel](img/panel.webp)

# Supported Cycles Material Nodes

| Cycles Node               | Octane Node                                   |
|---------------------------|-----------------------------------------------|
| ShaderNodeBsdfTranslucent | OctaneUniversalMaterial                       |
| ShaderNodeBsdfPrincipled  | OctaneUniversalMaterial                       |
| ShaderNodeTexImage        | ShaderNodeOctImageTex \| ShaderNodeOctAlphaImageTex |
| ShaderNodeOutputMaterial  | ShaderNodeOutputMaterial                      |
| ShaderNodeInvert          | OctaneInvertTexture                           |
| ShaderNodeMapping         | Octane3DTransformation                        |
| ShaderNodeVertexColor     | OctaneColorVertexAttribute                    |
| ShaderNodeMixRGB          | OctaneMixTexture \| OctaneAddTexture \| OctaneMultiplyTexture \| OctaneSubtractTexture |
| ShaderNodeMath            | OctaneBinaryMathOperation \| OctaneUnaryMathOperation |
| ShaderNodeBsdfTransparent | OctaneNullMaterial                            |
| ShaderNodeAddShader       | OctaneMixMaterial                             |
| ShaderNodeMixShader       | OctaneMixMaterial                             |
| ShaderNodeBsdfDiffuse     | OctaneDiffuseMaterial                         |
| ShaderNodeBump            | None                                          |
| ShaderNodeNormalMap       | None                                          |
| ShaderNodeHueSaturation   | OctaneColorCorrection                         |
| ShaderNodeBrightContrast  | OctaneColorCorrection                         |
| ShaderNodeRGB             | OctaneRGBColor                                |
| ShaderNodeMapRange        | OctaneRange                                   |


## License

This project is licensed under the GPL v3 License - see the [LICENSE](LICENSE) file for details.