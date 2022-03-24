
import bpy


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
