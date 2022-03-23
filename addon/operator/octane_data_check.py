import bpy

from bpy.types import (ShaderNodeTree,
                       Nodes,
                       Material
                       )

from typing import List

from ..utility.json_manager import load_json


class COC_OP_OctaneDataCheck(bpy.types.Operator):
    """Check Octane Data"""

    bl_idname = "coc.octanedatacheck"
    bl_label = "Check Octane Data"
    bl_options = {'REGISTER', 'UNDO'}

    temp_mats: List[Material] = []

    def _create_temp_material(self, bl_idname: str) -> Nodes:

        temp_mat = bpy.data.materials.new(
            name="OCTANE_CONVERTER_CHECKER_" + bl_idname)
        temp_mat.use_nodes = True

        self.temp_mats.append(temp_mat)

        node_tree = temp_mat.node_tree

        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        print(bl_idname)

        temp_node = node_tree.nodes.new(bl_idname)

        return temp_node

    def execute(self, context):

        json_data = load_json()

        for bl_idname in json_data:
            temp_node = self._create_temp_material(bl_idname)

            # Checking for outdated Cycles Output Nodes

            for output in json_data[bl_idname]["outputs"]:
                if not output in [o.name for o in temp_node.outputs]:
                    if not output.isdigit():
                        print(f"{bl_idname} - Output Not Found: {output}")

            # Checking for outdated Cycles Input Nodes

            for input in json_data[bl_idname]["inputs"]:
                if not input in [i.name for i in temp_node.inputs]:
                    if not input.isdigit():
                        print(f"{bl_idname} - Input Not Found: {input}")

            temp_octane_node = json_data[bl_idname]["octane_node"]

            if temp_octane_node:
                if isinstance(temp_octane_node, list):
                    for i in temp_octane_node:
                        self._create_temp_material(i)
                else:
                    self._create_temp_material(temp_octane_node)

        for material in self.temp_mats:
            bpy.data.materials.remove(material)

        self.temp_mats.clear()

        return {'FINISHED'}
