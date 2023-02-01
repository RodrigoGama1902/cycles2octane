import bpy

from .json_manager import load_json

from .node_functions import create_node, create_node_link

from bpy.types import (Node, NodeTree, NodeGroup)


class NodeGroupsGenerator:

    node_group: NodeGroup

    group_input_node: Node
    group_output_node: Node

    custom_node_group: Node

    def __init__(self, old_node):

        self.node_group = self._create_group_node_tree(old_node)
        self.custom_node_group = self._add_group_node_tree_to_node_tree(
            old_node, self.node_group)

    def _add_group_node_tree_to_node_tree(self, old_node, group_node_tree):

        node_tree = old_node.id_data

        custom_node_group = node_tree.nodes.new('ShaderNodeGroup')
        custom_node_group.node_tree = group_node_tree
        custom_node_group.name = "CUSTOM_NODE_" + \
            load_json()[old_node.bl_idname]["octane_node"]
        custom_node_group.label = load_json(
        )[old_node.bl_idname]["octane_node"]

        custom_node_group.location = old_node.location
        #custom_node_group.hide = True

        return custom_node_group

    def _create_group_node_tree(self, old_node):

        group_inputs_data = load_json(
        )[old_node.bl_idname]["group_inputs"]

        group_outputs_data = load_json(
        )[old_node.bl_idname]["group_outputs"]

        group_tree = bpy.data.node_groups.new(
            "CUSTOM_NODE_" + load_json()[old_node.bl_idname]["octane_node"], 'ShaderNodeTree')

        self.group_input_node = group_tree.nodes.new('NodeGroupInput')
        self.group_output_node = group_tree.nodes.new('NodeGroupOutput')

        self.group_input_node.location = (0, 0)
        self.group_input_node.location = (200, 0)

        for i in group_inputs_data:
            node_group_new_input = group_tree.inputs.new(
                group_inputs_data[i]["node_type"], i)

            default_value = group_inputs_data[i]["default_value"]

            if default_value:
                node_group_new_input.default_value = group_inputs_data[i]["default_value"]

        for i in group_outputs_data:
            group_tree.outputs.new(group_outputs_data[i], i)

        return group_tree


class CustomNodeGroupsGenerator(NodeGroupsGenerator):

    hue_node: Node

    node_location_y_interval: int = 0

    def _add_math_hue_node(self, input: str, multiply_value: float, operation: str = "Add", location: list = [-300, 0]):

        node_tree = self.custom_node_group.node_tree

        multiply_node = create_node(
            self.custom_node_group.node_tree, "OctaneBinaryMathOperation", [location[0], location[1] - (150 * self.node_location_y_interval)])

        multiply_node.inputs[2].default_value = operation

        value_node = create_node(
            self.custom_node_group.node_tree, "OctaneGreyscaleColor", [multiply_node.location[0] - 250, multiply_node.location[1] + 30])
        value_node.a_value = multiply_value

        float_to_greyscale = create_node(
            self.custom_node_group.node_tree, "OctaneFloatToGreyscale", [multiply_node.location[0] - 500, multiply_node.location[1] + 30])

        create_node_link(
            node_tree, multiply_node.inputs[1], float_to_greyscale.outputs[0])
        create_node_link(
            node_tree, float_to_greyscale.inputs[0], self.group_input_node.outputs[input])
        create_node_link(
            node_tree, multiply_node.outputs[0], self.hue_node.inputs[input])
        create_node_link(
            node_tree, multiply_node.inputs[0], value_node.outputs[0])

        self.node_location_y_interval += 1

    def ShaderNodeHueSaturation(self):

        node_tree = self.custom_node_group.node_tree

        self.group_input_node.location = -1000, 0
        self.group_output_node.location = 500, 0

        self.hue_node = octane_color_correction = create_node(
            node_tree, "OctaneColorCorrection")

        self._add_math_hue_node("Brightness", 0, operation="Add")
        self._add_math_hue_node("Hue", 0.5, operation="Subtract")
        self._add_math_hue_node("Saturation", 1, operation="Multiply")
        self._add_math_hue_node("Gamma", 1, operation="Multiply")
        self._add_math_hue_node("Contrast", 1, operation="Multiply")
        self._add_math_hue_node("Gain", 1, operation="Multiply")
        self._add_math_hue_node("Exposure", 1, operation="Multiply")

        create_node_link(
            node_tree, self.group_input_node.outputs[0], self.hue_node.inputs[0])

        # Saturation Link

        create_node_link(
            node_tree, octane_color_correction.outputs[0], self.group_output_node.inputs[0])

        return self.custom_node_group
