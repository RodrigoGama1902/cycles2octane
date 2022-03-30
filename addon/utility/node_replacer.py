
import bpy

from bpy.types import (Node,
                       NodeSocket

                       )

from . import cycles2octane_post_functions, cycles2octane_pre_functions

from .node_functions import create_null_node, convert_old_to_new_socket_value, get_correct_custom_group_original_node_name

from .json_manager import load_json

from dataclasses import dataclass


@dataclass
class NullNode:
    '''Null Node Type, created when there is no replacement for particular node when converting'''

    group_inputs: list
    group_outputs: list
    null_links: dict

    def __bool__(self):

        if not self.group_inputs and not self.group_outputs:
            return False
        return True


@dataclass
class ReplaceNodeData:
    '''ReplaceNodeData will store all information necessary to correctly convert the node'''

    convert_to_node: str
    replace_inputs: dict
    replace_outputs: dict

    def __bool__(self):

        if not self.replace_inputs and not self.replace_outputs:
            return False
        return True


class NodeReplacer:
    '''The main class the executes the node replacement/conversion'''

    new_node: Node

    def __init__(self, node: Node):

        self.new_node = None

        replace_node_data = ReplaceNodeData("", {}, {})
        null_node = NullNode([], [], {})

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

    def _replace_node(self, node: Node, null_node: NullNode, replace_node_data: ReplaceNodeData) -> Node:
        '''Execute the replace process using the ReplaceNodeData and NullNode data when exists '''

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

        if replace_node_data.replace_inputs:
            self._replace_node_links(node, new_node,
                                     replace_node_data.replace_inputs, "INPUT")

        if replace_node_data.replace_outputs:
            self._replace_node_links(node, new_node,
                                     replace_node_data.replace_outputs, "OUTPUT")

        return new_node

    @staticmethod
    def _octane_to_cycles_node_data(node: Node, json_data: dict) -> ReplaceNodeData:
        '''Generate Replacement Node Data for Octane to Cycles conversion '''

        node_item = None

        replace_node_data = ReplaceNodeData("", {}, {})

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
            
            original_null_node_name = get_correct_custom_group_original_node_name(
                node.name, "NULL_NODE_")
            
            node_item = json_data[original_null_node_name]
            replace_node_data.convert_to_node = original_null_node_name

        if node_item:

            for inp in node_item["inputs"]:
                replace_node_data.replace_inputs[node_item["inputs"][inp]] = inp
            for out in node_item["outputs"]:
                replace_node_data.replace_outputs[node_item["outputs"][out]] = out

        return replace_node_data

    @staticmethod
    def _cycles_to_octane_node_data(node: Node, json_data: dict) -> tuple[ReplaceNodeData, NullNode]:
        '''Generate Replacement Node Data for Cycles to Octane conversion '''

        replace_node_data = ReplaceNodeData("", {}, {})
        null_node = NullNode([], [], {})

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

        return replace_node_data, null_node

    @staticmethod
    def _run_node_pre_function(node: Node) -> Node:
        '''Executes the Pre Node Function If exists in cycles2octane_pre_functions.py'''

        # Operation Pre Functions
        if hasattr(cycles2octane_pre_functions, node.bl_idname if not "NULL_NODE_" in node.name else node.name):

            node_pre_function: Node

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
        '''Executes the Post Node Function If exists in cycles2octane_post_functions.py'''

        if hasattr(cycles2octane_post_functions, new_node.bl_idname if not null_node else new_node.name):

            node_function: Node = None

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
    def _replace_node_links(node: Node, new_node: Node, node_socket_data: dict, socket_type: str) -> None:
        '''Executes the correct link replacement from the old node to the new node'''

        node_tree = node.id_data

        old_node_sockets: NodeSocket = None
        new_node_sockets: NodeSocket = None

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

            # Getting Correct Socket Value, Any Error Will just Result in no default socket value replacement, can be ignored for now
            if hasattr(old_node_socket, 'default_value') and hasattr(new_node_sockets[replace_socket_identifier], "default_value"):

                try:
                    new_node_sockets[replace_socket_identifier].default_value = convert_old_to_new_socket_value(
                        new_node_sockets[replace_socket_identifier], old_node_socket.default_value)
                except ValueError:
                    pass
                except TypeError:
                    pass
                except AttributeError:
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
