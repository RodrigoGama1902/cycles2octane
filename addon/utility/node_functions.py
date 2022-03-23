import bpy

from typing import List, Dict

from bpy.types import (NodeSocket,
                       Node
                       )


def create_node(original_node: Node, replace_bl_idname: str, location) -> Node:

    node_tree = original_node.id_data

    node = node_tree.nodes.new(replace_bl_idname)
    node.location = location

    return node


def create_node_link(node: Node, link1: NodeSocket, link2: NodeSocket) -> None:

    node_tree = node.id_data
    link = node_tree.links.new
    link(link1, link2)


def replace_node(original_node: Node, replace_bl_idname: str, input_replace: Dict, output_replace: Dict) -> Node:

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
