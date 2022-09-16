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
            if node.type == "GROUP" and not node.name.startswith("NULL_NODE_"):
                self._convert_node_tree(node.node_tree)
            else:
                if not node in self.ignore_nodes:
                    replaced_node = NodeReplacer(node).new_node
                    self.ignore_nodes.append(replaced_node)

        self.ignore_nodes.clear()

    def _format_node_tree(self, node_tree: ShaderNodeTree) -> None:
        '''Readjust the old node tree to be compatible with the new node tree'''

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

    def _remove_unlinked_nodes(self, node_tree: ShaderNodeTree) -> None:

        for node in node_tree.nodes:
            unused_node = False

            for outp in node.outputs:
                if outp.links:
                    unused_node = True
                    break

            if node.type == 'OUTPUT_MATERIAL':  # Material output does not have output
                for inp in node.inputs:
                    if inp.links:
                        unused_node = True
                        break

            if not unused_node:
                node_tree.nodes.remove(node)

    def _join_mapping_nodes(self, node_tree):
        '''Join mapping nodes links to remove extra mapping nodes with same values'''

        mapping_nodes = [n for n in node_tree.nodes if n.type == 'MAPPING']
        mapping_patterns = []

        for mapping_node in mapping_nodes:
            if not mapping_patterns:
                mapping_patterns.append(mapping_node)
                continue

            new_pattern = True
            node_inputs_parameters = ["Location", "Rotation", "Scale"]

            same_node = None

            for n in mapping_patterns:

                same_input_parameters = True
                for inp in node_inputs_parameters:
                    if n.inputs[inp].default_value != mapping_node.inputs[inp].default_value:
                        same_input_parameters = False

                if same_input_parameters:
                    new_pattern = False
                    same_node = n
                    break

            if new_pattern:
                mapping_patterns.append(mapping_node)
                continue
            else:
                for out_link in mapping_node.outputs[0].links:
                    node_tree.links.new(
                        same_node.outputs[0], out_link.to_socket)  # type:ignore

    def _remove_frame_nodes(self, node_tree: ShaderNodeTree) -> None:
        for node in node_tree.nodes:
            if node.type == "FRAME":
                node_tree.nodes.remove(node)

    def execute(self, context):

        mat_data = get_materials_selected()
        for mat in mat_data:
            if mat:
                self._remove_frame_nodes(mat.node_tree)
                self._join_mapping_nodes(mat.node_tree)
                self._convert_node_tree(mat.node_tree)
                self._remove_unlinked_nodes(mat.node_tree)

        return {'FINISHED'}
