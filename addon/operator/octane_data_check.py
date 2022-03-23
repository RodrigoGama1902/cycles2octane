import bpy

from bpy.types import (ShaderNodeTree,
                       )

from ..utility import cycles2octane_post_functions 
from ..utility.functions import node_replacer, get_materials_selected

class COC_OP_ConvertNodes(bpy.types.Operator):
    """Convert Cycles nodes to Octane mdes"""

    bl_idname = "coc.convert_nodes"
    bl_label = "Convert Nodes"
    bl_options = {'REGISTER', 'UNDO'}
                        
    def execute(self, context):        

        
                
        return {'FINISHED'}