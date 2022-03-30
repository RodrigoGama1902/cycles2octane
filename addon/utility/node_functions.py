import colorsys
import bpy

from typing import Any

from bpy.types import (NodeSocket,
                       Node,
                       NodeLink,
                       NodeSocket
                       )


def create_node(original_node: Node, bl_idname: str, location: list[float] = [0, 0, 0]) -> Node:
    '''Create new node using original node as reference'''

    node_tree = original_node.id_data

    node = node_tree.nodes.new(bl_idname)
    node.location = location

    return node


def create_node_link(node: Node, link1: NodeSocket, link2: NodeSocket) -> None:
    '''Create Node Link'''

    node_tree = node.id_data
    link = node_tree.links.new
    link(link1, link2)


def replace_node(original_node: Node, replace_bl_idname: str, input_replace: dict, output_replace: dict) -> Node:
    '''Create a new node, update the links from the old node, and deletes it'''

    replacement_node = create_node(
        original_node, replace_bl_idname, original_node.location)

    if input_replace:
        for i in input_replace:
            if original_node.inputs[int(i)].links:
                create_node_link(
                    original_node, original_node.inputs[int(i)].links[0].from_socket, replacement_node.inputs[input_replace[i]])

    if output_replace:
        for i in output_replace:
            for link in original_node.outputs[int(i)].links:
                create_node_link(
                    original_node, link.to_socket, replacement_node.outputs[output_replace[i]])

    return replacement_node


def move_node_link_to_socket(node_socket: NodeSocket, to_socket_index: int) -> None:
    '''Move a link from NodeSocket to another index'''

    node = node_socket.node
    node_tree = node.id_data

    for link in node_socket.links:
        if link.from_node == node:  # Meaning that is an output node
            create_node_link(
                node, node.outputs[to_socket_index], link.to_socket)
        else:
            create_node_link(
                node, link.from_socket, node.inputs[to_socket_index])

            node_tree.links.remove(link)


def remove_node_and_pass_link_through(node: Node, input_index: int = 0, output_index: int = 0) -> None:
    '''remove inputted node, and pass the link through the input.from_socket to output.from_socket'''

    node_tree = node.id_data

    for link in node.outputs[output_index].links:
        create_node_link(
            node, node.inputs[input_index].links[0].from_socket, link.to_socket)

    node_tree.nodes.remove(node)


def create_null_node(node: Node, node_tree, null_links, group_inputs, group_outputs):
    '''Create null node, used when there is no replacement for the original node on conversion'''

    group_tree = bpy.data.node_groups.new(
        "NULL_NODE_" + node.bl_idname, 'ShaderNodeTree')

    group_in = group_tree.nodes.new('NodeGroupInput')
    group_out = group_tree.nodes.new('NodeGroupOutput')

    for i in group_inputs:
        group_tree.inputs.new(group_inputs[i], i)

    for i in group_outputs:
        group_tree.outputs.new(group_outputs[i], i)

    group_in.location = (0, 0)
    group_out.location = (200, 0)

    null_node_tree = group_tree

    null_group = node_tree.nodes.new('ShaderNodeGroup')
    null_group.node_tree = bpy.data.node_groups[null_node_tree.name]
    null_group.name = "NULL_NODE_" + node.bl_idname
    null_group.label = node.name
    null_group.location = node.location
    null_group.hide = True

    link = null_node_tree.links.new

    for i in null_links:
        link(group_in.outputs[i], group_out.inputs[null_links[i]])

    return null_group


def convert_old_to_new_socket_value(new_socket: NodeSocket, old_value: Any) -> Any:
    '''correctly convert the old node value, to the new node value'''

    if new_socket.type == "VALUE":
        if isinstance(old_value, (float, int)):
            return old_value

        if isinstance(old_value, bpy.types.bpy_prop_array):
            if len(old_value) == 4:
                return old_value[-2]
            if len(old_value) == 3:
                return old_value[-1]

    if new_socket.type == "RGBA":

        if isinstance(old_value, (float, int)):
            rgb = colorsys.hsv_to_rgb(0.5, 0, old_value)
            rgba = [i for i in rgb]
            rgba.append(1)

            return rgba

        if len(old_value) == 3:
            rgb = list(old_value)
            rgba = [i for i in rgb]
            rgba.append(1)

            return rgba

        if len(old_value) == 4:
            rgba = [i for i in list(old_value)]

            return rgba

    # New Socket always will be CUSTOM when converting to Octane
    if new_socket.type == "CUSTOM":

        if hasattr(new_socket, "default_value"):
            new_default_value = new_socket.default_value

            # Handeling Int, Float Cases
            if isinstance(new_default_value, (float, int)):
                if isinstance(old_value, (float, int)):
                    return old_value

            # Handeling Color List Cases
            if len(new_default_value) == 3:
                if isinstance(old_value, (float, int)):
                    rgb = [i for i in colorsys.hsv_to_rgb(0.5, 0, old_value)]
                    return rgb

                if len(old_value) == 3:
                    rgb = [i for i in list(old_value)]

                    return rgb

                if len(old_value) == 4:
                    rgba = [i for i in list(old_value)]
                    return rgba[:-1]

    return old_value


def get_correct_custom_group_original_node_name(node_name, prefix):

    node_name = get_node_name_without_duplicate(node_name)

    if node_name.startswith(prefix):
        node_name = node_name.replace(
            prefix, "")

    return node_name


def get_node_name_without_duplicate(node_name):

    if len(node_name) >= 5:
        if node_name[-4] == "." and node_name[-3].isdigit() and node_name[-2].isdigit() and node_name[-1].isdigit():
            node_name = node_name[:-4]

    return node_name


def remove_reroute_node_from_node_tree(node_tree):

    for node in node_tree.nodes:

        if node.type == "GROUP":
            remove_reroute_node_from_node_tree(node.node_tree)

        if node.type == "REROUTE":
            remove_node_and_pass_link_through(node, 0, 0)
