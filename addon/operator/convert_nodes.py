import bpy

from bpy.types import (ShaderNodeTree,
                       )


from ..utility.functions import get_materials_selected
from ..utility.node_replacer import NodeReplacer


class COC_OP_ConvertNodes(bpy.types.Operator):
    """Convert Cycles nodes to Octane mdes"""

    bl_idname = "coc.convert_nodes"
    bl_label = "Convert Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    ignore_nodes = []

    # Convert all nodes, including nodes inside node groups
    def convert_node_tree(self, node_tree: ShaderNodeTree):

        for node in node_tree.nodes:

            if node.type == "FRAME":
                node_tree.nodes.remove(node)
                continue

            if node.type == "GROUP" and not node.name.startswith("NULL_NODE_"):
                self.convert_node_tree(node.node_tree)
            else:
                if not node in self.ignore_nodes:
                    replaced_node = NodeReplacer(node).new_node
                    self.ignore_nodes.append(replaced_node)

        self.ignore_nodes.clear()

    def execute(self, context):

        mat_data = get_materials_selected()

        for mat in mat_data:
            if mat:
                self.convert_node_tree(mat.node_tree)

        return {'FINISHED'}
