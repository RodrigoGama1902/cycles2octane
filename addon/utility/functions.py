import json
import os
import bpy
import colorsys

from . import cycles2octane_post_functions, cycles2octane_pre_functions
from .json_manager import load_json

from typing import List

from dataclasses import dataclass

convert_to = "OCTANE"


@dataclass
class CustomNodeGroup:

    group_inputs: List
    group_outputs: List


def node_replacer(node):

    # this functions executes the input/output action
    # When in_out appers, means that depending on the input parameter, this value represents input or output
    def in_out_mng(input=True):

        in_out_dict = replace_inputs if input else replace_outputs
        node_for = node.inputs if input else node.outputs
        new_node_in_out = new_node.inputs if input else new_node.outputs

        link = node_tree.links.new

        idx = -1
        for i in node_for:
            idx += 1

            key_name = i.name

            if not node_index:
                replace_in_out = in_out_dict[key_name] if in_out_dict.get(
                    key_name) else None
            else:
                try:
                    replace_in_out = in_out_dict[str(idx)]
                except KeyError:
                    pass

            if replace_in_out:

                if node_index:
                    replace_in_out = int(replace_in_out)

                if hasattr(i, 'default_value') and hasattr(new_node_in_out[replace_in_out], "default_value"):

                    try:
                        new_node_in_out[replace_in_out].default_value = get_correct_value(
                            new_node_in_out[replace_in_out], i.default_value)
                    except ValueError:
                        pass
                    except TypeError:
                        pass

                if i.links:
                    for link_s in i.links:
                        if input:
                            link(
                                new_node.inputs[replace_in_out], link_s.from_socket)
                        else:
                            link(
                                new_node.outputs[replace_in_out], link_s.to_socket)

    props = bpy.context.scene.cycles2octane

    json_data = load_json()

    # -----------------------------------------------
    # Getting replacement information
    # -----------------------------------------------

    convert_to_node = None
    replace_inputs = {}
    replace_outputs = {}

    # NULL NODES DATA

    null_links = {}
    # This variable tells if the node that will replace the current one will be a null node
    null_node = False

    custom_group: CustomNodeGroup

    # Convert to Cycles
    if props.convert_to == '0':

        node_item = None

        if not "NULL_NODE_" in node.name:
            for item in json_data:

                # Check if this cycle node replaces multiple octane nodes (list type)
                if isinstance(json_data[item]["octane_node"], list):
                    for i in json_data[item]["octane_node"]:
                        if i == node.bl_idname:
                            node_item = json_data[item]
                            convert_to_node = item
                    continue

                if json_data[item]["octane_node"] == node.bl_idname:
                    node_item = json_data[item]
                    convert_to_node = item
        else:
            node_item = json_data[node.name.replace("NULL_NODE_", "")]
            convert_to_node = node.name.replace("NULL_NODE_", "")

        if node_item:

            for inp in node_item["inputs"]:
                replace_inputs[node_item["inputs"][inp]] = inp
            for out in node_item["outputs"]:
                replace_outputs[node_item["outputs"][out]] = out

            if node_item.get("null_links"):
                for link in node_item["null_links"]:
                    null_links[node_item["null_links"][link]] = link

    # Convert to Octane
    if props.convert_to == '1':

        if node.bl_idname in json_data:

            node_data = json_data[node.bl_idname]

            if node_data["octane_node"] == "None":
                null_node = True

                custom_group = CustomNodeGroup
                custom_group.group_inputs = node_data["group_inputs"]
                custom_group.group_outputs = node_data["group_outputs"]

            # Check if this cycle node replaces multiple octane nodes (list type)
            if isinstance(node_data["octane_node"], list):
                convert_to_node = node_data["octane_node"][0]
            else:
                convert_to_node = node_data["octane_node"]

            for i in node_data["inputs"]:
                replace_inputs[i] = node_data["inputs"][i]

            for i in node_data["outputs"]:
                replace_outputs[i] = node_data["outputs"][i]

            if node_data.get("null_links"):
                for link in node_data["null_links"]:
                    null_links[link] = node_data["null_links"][link]

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

    # -----------------------------------------------
    # Replacement Start
    # -----------------------------------------------

    node_tree = node.id_data

    if null_node:
        new_node = create_null_node(
            node, node_tree, null_links, custom_group.group_inputs, custom_group.group_outputs)
    else:
        if convert_to_node:
            new_node = node_tree.nodes.new(convert_to_node)
        else:
            return

    new_node.location = node.location

    # creating new Links

    node_index = False
    if replace_inputs:
        node_index = True if [
            f for f in replace_inputs][0].isdigit() else False

    in_out_mng(input=True)
    in_out_mng(input=False)

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

    # Removing Old Node
    node_tree.nodes.remove(node)

    return new_node


def create_null_node(node, node_tree, null_links, group_inputs, group_outputs):

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


def get_correct_value(socket, value):

    if socket.type == "VALUE":
        if isinstance(value, float) or isinstance(value, int):
            return value
        if isinstance(value, bpy.types.bpy_prop_array):
            if len(value) == 4:
                return value[-2]
            if len(value) == 3:
                return value[-1]

    if socket.type == "RGBA":
        if isinstance(value, bpy.types.bpy_prop_array):
            return value
        if isinstance(value, float) or isinstance(value, int):
            rgb = colorsys.hsv_to_rgb(0.5, 0, value)

            rgba = [i for i in rgb]
            rgba.append(1)

            return rgba

    return value


def get_materials_selected():

    props = bpy.context.scene.cycles2octane

    mat_data = []

    if props.select_method == "0":
        if bpy.context.active_object:
            if bpy.context.active_object.active_material:
                mat_data.append(bpy.context.active_object.active_material)

    if props.select_method == "1":
        if bpy.context.active_object:
            if bpy.context.active_object.data.materials:
                mat_data = bpy.context.active_object.data.materials

    if props.select_method == "2":

        mat_data = []

        objs = bpy.context.selected_objects

        for ob in objs:
            if hasattr(ob.data, "materials"):
                if ob.data.materials:
                    for mat in ob.data.materials:
                        if not mat in mat_data:
                            mat_data.append(mat)

    return mat_data
