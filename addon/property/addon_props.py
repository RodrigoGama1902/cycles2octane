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
        default='ACTIVE_MATERIAL',
        items=[
            ('ACTIVE_MATERIAL', 'Active Material', ''),
            ('ACTIVE_OBJECT', 'Active Object', ''),
            ('SELECTED_OBJECTS', 'Selected Objects', ''),
        ]
    )
