
import bpy

from bpy.types import (Node,

                       )

from . import cycles2octane_post_functions, cycles2octane_pre_functions

from .node_functions import create_null_node, get_correct_value

from .json_manager import load_json

from typing import List, Dict

from dataclasses import dataclass


@dataclass
class NullNode:

    group_inputs: List
    group_outputs: List
    null_links: Dict


@dataclass
class ReplaceNodeData:

    convert_to_node: str
    replace_inputs: List
    replace_outputs: List


class NodeReplacer:

    new_node: Node

    def __init__(self, node: Node):

        self.new_node = None
        null_node = None

        props = bpy.context.scene.cycles2octane
        json_data = load_json()

        # Generate Octane To Cycles Node Data
        if props.convert_to == '0':
            replace_node_data = self._octane_to_cycles_node_data(
                node, json_data)

        # Generate Cycles To Octane Node Data
        if props.convert_to == '1':
            replace_node_data, null_node = self._cycles_to_octane_node_data(
                node, json_data)

        # Starting Replacement
        if replace_node_data:

            # Running Pre Node Function
            node = self._run_node_pre_function(node)

            new_node = self._replace_node(node, null_node, replace_node_data)

            if new_node:

                new_node = self._run_node_post_function(
                    node, new_node, null_node)

                self.new_node = new_node
                node.id_data.nodes.remove(node)

    def _replace_node(self, node: Node, null_node: NullNode, replace_node_data: Dict) -> Node:

        node_tree = node.id_data

        if null_node:
            new_node = create_null_node(
                node, node_tree, null_node.null_links, null_node.group_inputs, null_node.group_outputs)
        else:
            if replace_node_data.convert_to_node:
                new_node = node_tree.nodes.new(
                    replace_node_data.convert_to_node)
            else:
                return

        new_node.location = node.location

        self._replace_node_links(node, new_node,
                                 replace_node_data.replace_inputs, "INPUT")

        self._replace_node_links(node, new_node,
                                 replace_node_data.replace_outputs, "OUTPUT")

        return new_node

    @staticmethod
    def _octane_to_cycles_node_data(node: Node, json_data: Dict) -> Dict:

        node_item = None

        replace_node_data = ReplaceNodeData(None, {}, {})

        if not "NULL_NODE_" in node.name:
            for item in json_data:

                # Check if this cycle node replaces multiple octane nodes (list type)
                if isinstance(json_data[item]["octane_node"], list):
                    for i in json_data[item]["octane_node"]:
                        if i == node.bl_idname:
                            node_item = json_data[item]
                            replace_node_data.convert_to_node = item
                    continue

                if json_data[item]["octane_node"] == node.bl_idname:
                    node_item = json_data[item]
                    replace_node_data.convert_to_node = item

        else:
            node_item = json_data[node.name.replace("NULL_NODE_", "")]
            replace_node_data.convert_to_node = node.name.replace(
                "NULL_NODE_", "")

        if node_item:

            for inp in node_item["inputs"]:
                replace_node_data.replace_inputs[node_item["inputs"][inp]] = inp
            for out in node_item["outputs"]:
                replace_node_data.replace_outputs[node_item["outputs"][out]] = out

        return replace_node_data

    @staticmethod
    def _cycles_to_octane_node_data(node: Node, json_data: Dict) -> Dict:

        replace_node_data = ReplaceNodeData(None, {}, {})
        null_node = False

        if node.bl_idname in json_data:

            node_data = json_data[node.bl_idname]

            if node_data["octane_node"] == "None":

                null_node = NullNode(
                    node_data["group_inputs"], node_data["group_outputs"], {})

            # Check if this cycle node replaces multiple octane nodes (list type)
            if isinstance(node_data["octane_node"], list):
                replace_node_data.convert_to_node = node_data["octane_node"][0]
            else:
                replace_node_data.convert_to_node = node_data["octane_node"]

            for i in node_data["inputs"]:
                replace_node_data.replace_inputs[i] = node_data["inputs"][i]

            for i in node_data["outputs"]:
                replace_node_data.replace_outputs[i] = node_data["outputs"][i]

            if node_data.get("null_links"):
                for link in node_data["null_links"]:
                    null_node.null_links[link] = node_data["null_links"][link]

            return replace_node_data, null_node
        return None, None

    @staticmethod
    def _run_node_pre_function(node: Node) -> Node:

        # Operation Pre Functions
        if hasattr(cycles2octane_pre_functions, node.bl_idname if not "NULL_NODE_" in node.name else node.name):

            if not "NULL_NODE_" in node.name:
                node_pre_function = getattr(
                    cycles2octane_pre_functions, node.bl_idname, False)
            else:
                node_pre_function = getattr(
                    cycles2octane_pre_functions, node.name, False)

            if node_pre_function:
                node = node_pre_function(node)

        return node

    @staticmethod
    def _run_node_post_function(node: Node, new_node: Node, null_node: NullNode) -> Node:
        # Operation Post Functions

        if hasattr(cycles2octane_post_functions, new_node.bl_idname if not null_node else new_node.name):

            if not null_node:
                node_function = getattr(
                    cycles2octane_post_functions, new_node.bl_idname, False)
            else:
                node_function = getattr(
                    cycles2octane_post_functions, new_node.name, False)

            if node_function:
                new_node = node_function(new_node, node)

            return new_node

    @staticmethod
    def _replace_node_links(node: Node, new_node: Node, node_socket_data: Dict, socket_type: str) -> None:

        node_tree = node.id_data

        if socket_type == "INPUT":
            old_node_sockets = node.inputs
            new_node_sockets = new_node.inputs

        if socket_type == "OUTPUT":
            old_node_sockets = node.outputs
            new_node_sockets = new_node.outputs

        for idx, old_node_socket in enumerate(old_node_sockets):

            # Getting Correct Replace Socket Identifier
            if [key for key in node_socket_data][0].isdigit():
                try:
                    replace_socket_identifier = int(node_socket_data[str(idx)])
                except KeyError:
                    continue

            else:
                old_socket_name = old_node_socket.name

                replace_socket_identifier = node_socket_data[old_socket_name] if node_socket_data.get(
                    old_socket_name) else None
                if not replace_socket_identifier:
                    continue

            # Getting Correct Socket Value, Any Error Will Result In Only Default Value Replacement
            if hasattr(old_node_socket, 'default_value') and hasattr(new_node_sockets[replace_socket_identifier], "default_value"):

                try:
                    new_node_sockets[replace_socket_identifier].default_value = get_correct_value(
                        new_node_sockets[replace_socket_identifier], old_node_socket.default_value)
                except ValueError:
                    pass
                except TypeError:
                    pass

            # Replace Links
            if old_node_socket.links:

                link = node_tree.links.new

                for link_s in old_node_socket.links:
                    if socket_type == "INPUT":
                        link(
                            new_node.inputs[replace_socket_identifier], link_s.from_socket)
                    else:
                        link(
                            new_node.outputs[replace_socket_identifier], link_s.to_socket)
