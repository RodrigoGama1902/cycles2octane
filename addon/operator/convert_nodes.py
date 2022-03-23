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
    
    ignore_nodes = []
    
    # Convert all nodes, including nodes inside node groups
    def convert_node_tree(self, node_tree : ShaderNodeTree):
                
        for node in node_tree.nodes:   

            if node.type == "FRAME":
                node_tree.nodes.remove(node)
                continue

            if node.type == "GROUP":
                self.convert_node_tree(node.node_tree)
            else:
                if not node in self.ignore_nodes:
                    replaced_node = node_replacer(node)
                    self.ignore_nodes.append(replaced_node)
        
        self.ignore_nodes.clear()
                
    def execute(self, context):        

        mat_data = get_materials_selected()
                
        for mat in mat_data:                  
            if mat:                      
                self.convert_node_tree(mat.node_tree) 
                
        return {'FINISHED'}

