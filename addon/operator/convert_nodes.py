import bpy

from bpy.types import (ShaderNodeTree,
                       Node
                       )

from ..utility import cycles2octane_format_nodes
from ..utility.material_functions import get_materials_selected
from ..utility.node_replacer import NodeReplacer
from ..utility.node_functions import remove_reroute_node_from_node_tree


class COC_OP_DeleteNodes(bpy.types.Operator):
    bl_idname = "coc.delete_nodes"
    bl_label = "Delete Nodes"
    bl_description = "Delete selected nodes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        nodes = context.active_object.active_material.node_tree.nodes
        for node in nodes:
            if node.select:
                nodes.remove(node)
        return {'FINISHED'}


class COC_OP_ConvertNodes(bpy.types.Operator):
    """Convert Cycles nodes to Octane nodes"""

    bl_idname = "coc.convert_nodes"
    bl_label = "Convert Material Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    # TODO Return the convertion result, amount of node that could be converted or not
    # TODO Add Dynamic property to the json data, so that other properties that are not input or output can be dynamically updated without pre/post functions
    # TODO Add support for functional node groups, like when converting the Cycles HUE Node to Octane HUE node. A node group will have to be created with math values to set the correct values
    # TODO Add support for reroute nodes, a function to get connected node will have to be created, and implemented in all code

    ignore_nodes: list = []

    def _convert_node_tree(self, node_tree: ShaderNodeTree):
        '''Convert all nodes, including nodes inside node groups'''

        self._format_node_tree(node_tree)

        for node in node_tree.nodes:

            if node.type == "FRAME":
                node_tree.nodes.remove(node)
                continue

            if node.type == "GROUP" and not node.name.startswith("NULL_NODE_"):
                self._convert_node_tree(node.node_tree)
            else:
                if not node in self.ignore_nodes:
                    replaced_node = NodeReplacer(node).new_node
                    self.ignore_nodes.append(replaced_node)

        self.ignore_nodes.clear()

    def _format_node_tree(self, node_tree: ShaderNodeTree) -> None:

        remove_reroute_node_from_node_tree(node_tree)

        for node in node_tree.nodes:
            # Format Nodes

            if node.type == "GROUP":
                self._format_node_tree(node.node_tree)
            else:
                if hasattr(cycles2octane_format_nodes, node.bl_idname if not "NULL_NODE_" in node.name else node.name):

                    node_format: Node

                    if not "NULL_NODE_" in node.name:
                        node_format = getattr(
                            cycles2octane_format_nodes, node.bl_idname, False)
                    else:
                        node_format = getattr(
                            cycles2octane_format_nodes, node.name, False)

                    if node_format:
                        node_format(node)

    def execute(self, context):

        mat_data = get_materials_selected()
        for mat in mat_data:
            if mat:
                self._convert_node_tree(mat.node_tree)

        return {'FINISHED'}
