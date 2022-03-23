import bpy

from .functions import get_correct_value

# Functions that will run after the replaced node were created

# PRINCIPLED NODES


def ShaderNodeBsdfPrincipled(new_node, old_node):

    return new_node

def ShaderNodeTexImage(new_node, old_node):

    new_node.image = old_node.image

    return new_node


def ShaderNodeMath(new_node, old_node):

    def update_node_operation(cycles_operaton: str, octane_operation: str) -> None:

        if old_node.inputs['Operation'].default_value == octane_operation:
            new_node.operation = cycles_operaton

    update_node_operation("ADD", "Add")
    update_node_operation("DIVIDE", "Divide")
    update_node_operation("POWER", "Exponential [a^b]")
    update_node_operation("MULTIPLY", "Multiply")
    update_node_operation("SUBTRACT", "Subtract")

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

    if old_node.bl_idname == "ShaderNodeOctMixTex":
        new_node.blend_type = 'MIX'

    if old_node.bl_idname == "ShaderNodeOctAddTex":
        new_node.blend_type = "ADD"

    if old_node.bl_idname == "ShaderNodeOctMultiplyTex":
        new_node.blend_type = "MULTIPLY"

    if old_node.bl_idname == "ShaderNodeOctSubtractTex":
        new_node.blend_type = "SUBTRACT"

    return new_node

# OCTANE NODES

def ShaderNodeOctUniversalMat(new_node, old_node):

    # Turn albedo black when detect transmission change
    if not new_node.inputs['Transmission'].default_value == (0, 0, 0, 1):
        new_node.inputs['Albedo color'].default_value = (0, 0, 0, 1)


def ShaderNodeOctImageTex(new_node, old_node):

    new_node.image = old_node.image

    return new_node


def ShaderNodeOctNullMat(new_node, old_node):

    if old_node.bl_idname == "ShaderNodeBsdfTransparent":
        new_node.inputs['Opacity'].default_value = 0

    return new_node


def ShaderNodeOctMixTex(new_node, old_node):

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
        return replace_mix_operation(new_node, 'ShaderNodeOctMultiplyTex')

    if old_node.blend_type == 'ADD':
        return replace_mix_operation(new_node, 'ShaderNodeOctAddTex')

    if old_node.blend_type == 'SUBTRACT':
        return replace_mix_operation(new_node, 'ShaderNodeOctSubtractTex')


def ShaderNodeOctAddTex(new_node, old_node):

    def replace_math_operation(math_node, to_operation):

        node_tree = math_node.id_data

        new_op_node = node_tree.nodes.new(to_operation)
        new_op_node.location = math_node.location

        new_op_node.inputs[0].default_value = get_correct_value(
            new_op_node.inputs[0], old_node.inputs[0].default_value)
        new_op_node.inputs[1].default_value = get_correct_value(
            new_op_node.inputs[0], old_node.inputs[1].default_value)

        link = node_tree.links.new

        if math_node.inputs[0].links:
            link(math_node.inputs[0].links[0].from_socket,
                 new_op_node.inputs[0])
        if math_node.inputs[1].links:
            link(math_node.inputs[1].links[0].from_socket,
                 new_op_node.inputs[1])

        if math_node.outputs[0].links:
            for i in math_node.outputs[0].links:
                link(i.to_socket, new_op_node.outputs[0])

        node_tree.nodes.remove(math_node)

        return new_op_node

    if old_node.operation == 'MULTIPLY':
        return replace_math_operation(new_node, 'ShaderNodeOctMultiplyTex')

    if old_node.operation == 'ADD':
        return replace_math_operation(new_node, 'ShaderNodeOctAddTex')

    if old_node.operation == 'SUBTRACT':
        return replace_math_operation(new_node, 'ShaderNodeOctSubtractTex')


def ShaderNodeOctColorVertexTex(new_node, old_node):

    new_node.inputs[0].default_value = old_node.layer_name

    return new_node


def ShaderNodeOctColorCorrectTex(new_node, old_node):

    new_node.inputs["Brightness"].default_value += 1
    new_node.inputs["Contrast"].default_value += 0.001
    new_node.inputs["Hue"].default_value -= 0.5

    return new_node


def OctaneBinaryMathOperation(new_node: bpy.types.Node, old_node: bpy.types.Node) -> bpy.types.Nodes:

    def update_node_operation(cycles_operaton: str, octane_operation: str) -> None:

        if old_node.operation == cycles_operaton:
            new_node.inputs['Operation'].default_value = octane_operation

    update_node_operation("ADD", "Add")
    update_node_operation("DIVIDE", "Divide")
    update_node_operation("POWER", "Exponential [a^b]")
    update_node_operation("MULTIPLY", "Multiply")
    update_node_operation("SUBTRACT", "Subtract")

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
