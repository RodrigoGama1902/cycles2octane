import bpy

from .functions import get_correct_value
from .node_functions import replace_node

# Functions that will run after the replaced node were created

# PRINCIPLED NODES


def ShaderNodeBsdfPrincipled(new_node, old_node):

    return new_node


def ShaderNodeTexImage(new_node, old_node):

    new_node.image = old_node.image

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

    if old_node.bl_idname == "OctaneMultiplyTexture":
        new_node.blend_type = "MULTIPLY"

    if old_node.bl_idname == "OctaneSubtractTexture":
        new_node.blend_type = "SUBTRACT"

    return new_node

# OCTANE NODES


def OctaneUniversalMaterial(new_node, old_node):

    # Turn albedo black when detect transmission change
    if not new_node.inputs['Transmission'].links:
        new_node.inputs['Albedo color'].default_value = (0, 0, 0, 1)


def ShaderNodeOctImageTex(new_node, old_node):

    new_node.image = old_node.image

    return new_node


def OctaneNullMaterial(new_node, old_node):

    if old_node.bl_idname == "ShaderNodeBsdfTransparent":
        new_node.inputs['Opacity'].default_value = 0

    return new_node


def OctaneMixTexture(new_node, old_node):

    def replace_mix_operation(mix_node, to_operation):

        node_tree = mix_node.id_data

        new_op_node = node_tree.nodes.new(to_operation)
        new_op_node.location = mix_node.location

        new_op_node.inputs[0].default_value = get_correct_value(
            new_op_node.inputs[0], old_node.inputs[1].default_value)
        new_op_node.inputs[1].default_value = get_correct_value(
            new_op_node.inputs[0], old_node.inputs[2].default_value)

        link = node_tree.links.new

        if mix_node.inputs[1].links:
            link(mix_node.inputs[1].links[0].from_socket,
                 new_op_node.inputs[0])
        if mix_node.inputs[2].links:
            link(mix_node.inputs[2].links[0].from_socket,
                 new_op_node.inputs[1])

        if mix_node.outputs[0].links:
            for i in mix_node.outputs[0].links:
                link(i.to_socket, new_op_node.outputs[0])

        node_tree.nodes.remove(mix_node)

        return new_op_node

    if old_node.blend_type == 'MULTIPLY':
        return replace_mix_operation(new_node, 'OctaneMultiplyTexture')

    if old_node.blend_type == 'ADD':
        return replace_mix_operation(new_node, 'OctaneAddTexture')

    if old_node.blend_type == 'SUBTRACT':
        return replace_mix_operation(new_node, 'OctaneSubtractTexture')


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
                if i.to_node.type == "OCT_UNIVERSAL_MAT":
                    if i.to_socket.name == "Normal":

                        link = node_tree.links.new
                        link(new_node.outputs["Bump"],
                             i.to_node.inputs["Bump"])

    # if not new_node.inputs["Normal"].links:
    #    if new_node.outputs["Normal"].links:
    #        for i in new_node.outputs["Normal"].links:
    #            node_tree.links.remove(i)

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
