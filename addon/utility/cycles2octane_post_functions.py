import bpy

from .node_functions import (
    replace_node,
    move_node_link_to_socket,
    convert_old_to_new_socket_value,
    create_node_link,
    create_node)

# Functions that will run after the replaced node were created

# PRINCIPLED NODES


def ShaderNodeBsdfPrincipled(new_node, old_node):

    return new_node


def ShaderNodeTexImage(new_node, old_node):

    new_node.image = old_node.image

    if old_node.bl_idname == "ShaderNodeOctAlphaImageTex":
        move_node_link_to_socket(new_node.outputs[0], 1)

    return new_node


def ShaderNodeMath(new_node, old_node):

    # Binary Operations

    if old_node.inputs['Operation'].default_value == "Add":
        new_node.operation = "ADD"
    if old_node.inputs['Operation'].default_value == "Divide":
        new_node.operation = "DIVIDE"
    if old_node.inputs['Operation'].default_value == "Exponential [a^b]":
        new_node.operation = "POWER"
    if old_node.inputs['Operation'].default_value == "Multiply":
        new_node.operation = "MULTIPLY"
    if old_node.inputs['Operation'].default_value == "Subtract":
        new_node.operation = "SUBTRACT"

    # Unary Operations

    if old_node.inputs['Operation'].default_value == "Sine":
        new_node.operation = "SINE"
    if old_node.inputs['Operation'].default_value == "Square root":
        new_node.operation = "SQRT"
    if old_node.inputs['Operation'].default_value == "Inverse square root":
        new_node.operation = "INVERSE_SQRT"
    if old_node.inputs['Operation'].default_value == "Absolute value":
        new_node.operation = "ABSOLUTE"
    if old_node.inputs['Operation'].default_value == "Exponential [2^x]":
        new_node.operation = "EXPONENT"

    return new_node


def ShaderNodeNormalMap(new_node, old_node):

    normal_output = new_node.outputs["Normal"]
    normal_link = normal_output.links

    if normal_link:
        for i in normal_link:
            to_node = i.to_node
            if to_node.bl_idname == "ShaderNodeBsdfPrincipled":

                node_tree = to_node.id_data

                node_tree.links.remove(i)

                link = node_tree.links.new

                link(normal_output, to_node.inputs["Normal"])

    return new_node


def ShaderNodeMixRGB(new_node, old_node):

    if old_node.bl_idname == "OctaneMixTexture":
        new_node.blend_type = 'MIX'

    if old_node.bl_idname == "OctaneAddTexture":
        new_node.blend_type = "ADD"

        move_node_link_to_socket(new_node.inputs[1], 2)
        move_node_link_to_socket(new_node.inputs[0], 1)

    if old_node.bl_idname == "OctaneMultiplyTexture":
        new_node.blend_type = "MULTIPLY"

        move_node_link_to_socket(new_node.inputs[1], 2)
        move_node_link_to_socket(new_node.inputs[0], 1)

    if old_node.bl_idname == "OctaneSubtractTexture":
        new_node.blend_type = "SUBTRACT"

        move_node_link_to_socket(new_node.inputs[1], 2)
        move_node_link_to_socket(new_node.inputs[0], 1)

    return new_node


def ShaderNodeRGB(new_node, old_node):

    rgb = list(old_node.a_value)
    rgba = [i for i in rgb]
    rgba.append(1)

    new_node.outputs[0].default_value = rgba

    return new_node


def ShaderNodeMapRange(new_node, old_node):

    if old_node.inputs[1].default_value == "Linear":
        new_node.interpolation_type = 'LINEAR'

    if old_node.inputs[1].default_value == "Steps":
        new_node.interpolation_type = 'STEPPED'

    if old_node.inputs[1].default_value == "Smoothstep":
        new_node.interpolation_type = 'SMOOTHSTEP'

    if old_node.inputs[1].default_value == "Smootherstep":
        new_node.interpolation_type = "SMOOTHERSTEP"

    new_node.clamp = old_node.inputs['Clamp'].default_value

    return new_node

# OCTANE NODES


def OctaneUniversalMaterial(new_node, old_node):

    # Turn albedo black when detect transmission change
    if new_node.inputs['Transmission'].links:
        new_node.inputs['Albedo'].default_value = (0, 0, 0)

    if old_node.inputs.get('Transmission'):
        if not old_node.inputs['Transmission'].links:
            if not old_node.inputs['Transmission'].default_value == 0:
                rgb_node = create_node(
                    new_node.id_data, "OctaneRGBColor", location=[new_node.location[0] - 200, new_node.location[1]])

                rgb_node.a_value = old_node.inputs["Base Color"].default_value[:-1]

                create_node_link(
                    rgb_node.id_data, rgb_node.outputs[0], new_node.inputs["Transmission"])

                new_node.inputs['Albedo'].default_value = (0, 0, 0)

    return new_node


def OctaneRange(new_node, old_node):

    if old_node.interpolation_type == 'LINEAR':
        new_node.inputs[1].default_value = "Linear"

    if old_node.interpolation_type == 'STEPPED':
        new_node.inputs[1].default_value = "Steps"

    if old_node.interpolation_type == 'SMOOTHSTEP':
        new_node.inputs[1].default_value = "Smoothstep"

    if old_node.interpolation_type == 'SMOOTHERSTEP':
        new_node.inputs[1].default_value = "Smootherstep"

    new_node.inputs['Clamp'].default_value = old_node.clamp

    return new_node


def ShaderNodeOctImageTex(new_node, old_node):

    new_node.image = old_node.image

    old_image_color_space = old_node.image.colorspace_settings

    if old_image_color_space.name == 'sRGB':
        new_node.inputs['Gamma'].default_value = 2.2

    if old_image_color_space.name == 'Non-Color':
        new_node.inputs['Gamma'].default_value = 1

    if not new_node.outputs[0].links:
        new_node.id_data.nodes.remove(new_node)
        return

    return new_node


def OctaneRGBColor(new_node, old_node):

    new_node.a_value = old_node.outputs[0].default_value[:-1]

    return new_node


def OctaneNullMaterial(new_node, old_node):

    if old_node.bl_idname == "ShaderNodeBsdfTransparent":
        new_node.inputs['Opacity'].default_value = 0

    return new_node


def OctaneMixTexture(new_node, old_node):

    if old_node.blend_type == 'MIX':
        return new_node

    else:
        replacement_node = None

        if old_node.blend_type == 'MULTIPLY':
            replacement_node = replace_node(new_node, "OctaneMultiplyTexture", {
                "1": 0, "2": 1}, {"0": 0})

        if old_node.blend_type == 'ADD':
            replacement_node = replace_node(new_node, "OctaneAddTexture", {
                "1": 0, "2": 1}, {"0": 0})

        if old_node.blend_type == 'SUBTRACT':
            replacement_node = replace_node(new_node, "OctaneSubtractTexture", {
                "1": 0, "2": 1}, {"0": 0})

        new_node.id_data.nodes.remove(new_node)

        return replacement_node


def OctaneColorVertexAttribute(new_node, old_node):

    new_node.inputs[0].default_value = old_node.layer_name

    return new_node


def OctaneColorCorrection(new_node, old_node):

    new_node.inputs["Brightness"].default_value += 1
    new_node.inputs["Contrast"].default_value += 0.001
    new_node.inputs["Hue"].default_value -= 0.5

    return new_node


def OctaneBinaryMathOperation(new_node: bpy.types.Node, old_node: bpy.types.Node) -> bpy.types.Nodes:

    cycles_binary_math_operation = [
        "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "POWER"]

    cycles_unary_math_operation = [
        "SINE", "SQRT", "INVERSE_SQRT", "ABSOLUTE", "EXPONENT"]

    if old_node.operation in cycles_binary_math_operation:

        if old_node.operation == "ADD":
            new_node.inputs['Operation'].default_value = "Add"

        if old_node.operation == "DIVIDE":
            new_node.inputs['Operation'].default_value = "Divide"

        if old_node.operation == "POWER":
            new_node.inputs['Operation'].default_value = "Exponential [a^b]"

        if old_node.operation == "MULTIPLY":
            new_node.inputs['Operation'].default_value = "Multiply"

        if old_node.operation == "SUBTRACT":
            new_node.inputs['Operation'].default_value = "Subtract"

    if old_node.operation in cycles_unary_math_operation:

        unary_node = replace_node(
            new_node, "OctaneUnaryMathOperation", {"0": 0}, {"0": 0})

        if old_node.operation == "SINE":
            unary_node.inputs[1].default_value = "Sine"

        if old_node.operation == "SQRT":
            unary_node.inputs[1].default_value = "Square root"

        if old_node.operation == "INVERSE_SQRT":
            unary_node.inputs[1].default_value = "Inverse square root"

        if old_node.operation == "ABSOLUTE":
            unary_node.inputs[1].default_value = "Absolute value"

        if old_node.operation == "EXPONENT":
            unary_node.inputs[1].default_value = "Exponential [2^x]"

        new_node.id_data.nodes.remove(new_node)
        new_node = unary_node

    return new_node

# NULL NODES GROUP


def NULL_NODE_ShaderNodeBump(new_node, old_node):

    node_tree = new_node.id_data

    if new_node.inputs["Height"].links:

        if new_node.outputs["Normal"].links:

            for i in new_node.outputs["Normal"].links:
                if i.to_node.bl_idname == "OctaneUniversalMaterial":
                    if i.to_socket.name == "Normal":

                        link = node_tree.links.new
                        link(new_node.outputs["Bump"],
                             i.to_node.inputs["Bump"])

    return new_node


def NULL_NODE_ShaderNodeNormalMap(new_node, old_node):

    normal_output = new_node.outputs["Normal"]
    normal_link = normal_output.links

    if normal_link:
        for i in normal_link:
            to_node = i.to_node
            if to_node.bl_idname == "ShaderNodeOctUniversalMat":

                node_tree = to_node.id_data

                node_tree.links.remove(i)

                link = node_tree.links.new

                link(normal_output, to_node.inputs["Normal"])

    return new_node
