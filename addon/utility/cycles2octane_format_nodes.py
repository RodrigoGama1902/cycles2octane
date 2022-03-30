import bpy

from .node_functions import (create_node,
                             remove_node_and_pass_link_through,
                             create_node_link)

from bpy.types import (Node,
                       NodeSocket)


def ShaderNodeBsdfPrincipled(node: Node):

    props = bpy.context.scene.cycles2octane
    node_tree = node.id_data

    if props.convert_to == "1":

        # Detect Translucent Material Setup

        if node.outputs[0].links:
            for link in node.outputs[0].links:
                if link.to_node.bl_idname == "ShaderNodeMixShader" or link.to_node.bl_idname == "ShaderNodeAddShader":

                    join_node = link.to_node
                    translucent_node = None

                    for idx, input in enumerate(join_node.inputs):
                        if input.links:
                            if input.links[0].from_node.bl_idname == "ShaderNodeBsdfPrincipled":
                                principled_idx = idx

                            if input.links[0].from_node.bl_idname == "ShaderNodeBsdfTranslucent":
                                translucent_node = input.links[0].from_node

                    if translucent_node and join_node:

                        # Translucent Setup Detected

                        remove_node_and_pass_link_through(
                            join_node, principled_idx, 0)

                        if translucent_node.inputs["Color"].links:
                            # Forcing the principled transmission input to be connected to a color input type
                            # So when this node is converted to Universal Material, the color input will be used

                            create_node_link(
                                node, node.inputs["Transmission"], translucent_node.inputs["Color"].links[0].from_socket)

                            node_tree.nodes.remove(translucent_node)

                        else:
                            input_rgb = create_node(node, "ShaderNodeRGB", [
                                node.location[0] - 300, node.location[1]])

                            input_rgb.outputs["Color"].default_value = translucent_node.inputs["Color"].default_value

                            create_node_link(
                                input_rgb, node.inputs["Transmission"], input_rgb.outputs["Color"])

                            node_tree.nodes.remove(translucent_node)
