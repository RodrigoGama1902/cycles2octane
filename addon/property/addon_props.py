# type:ignore

import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       EnumProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList,
                       )


class COC_AddonMainProps(PropertyGroup):

    convert_to: EnumProperty(
        name='Convert To',
        default='OCTANE',
        items=[
            ('CYCLES', 'Cycles', ''),
            ('OCTANE', 'Octane', ''),
        ]
    )

    select_method: EnumProperty(
        name='Convert',
        default='0',
        items=[
            ('0', 'Active Material', ''),
            ('1', 'Active Object', ''),
            ('2', 'Selected Objects', ''),
        ]
    )
