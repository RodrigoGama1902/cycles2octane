import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

class COC_AddonMainProps(PropertyGroup):
    
    convert_to : bpy.props.EnumProperty(
        name= 'Convert To',
        default = '1',
        items = [
            ('0','Cycles', ''),
            ('1','Octane', ''),
        ]        
    )
    
    select_method : bpy.props.EnumProperty(
        name= 'Convert',
        default = '0',
        items = [
            ('0','Active Material', ''),
            ('1','Active Object', ''),
            ('2','Selected Objects', ''),
        ]        
    )



    




    