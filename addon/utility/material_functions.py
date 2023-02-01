
import bpy

from bpy.types import (Material)


def get_materials_selected() -> list[Material]:
    '''Get selected materials using as parameter the current convert method (Active Material, Active Object or Selected Objects'''

    props = bpy.context.scene.cycles2octane

    mat_data = []

    if props.select_method == "ACTIVE_MATERIAL":
        if bpy.context.active_object:
            if bpy.context.active_object.active_material:
                mat_data.append(bpy.context.active_object.active_material)

    if props.select_method == "ACTIVE_OBJECT":
        if bpy.context.active_object:
            if bpy.context.active_object.data.materials:
                mat_data = bpy.context.active_object.data.materials

    if props.select_method == "SELECTED_OBJECTS":

        mat_data = []

        objs = bpy.context.selected_objects

        for ob in objs:
            if hasattr(ob.data, "materials"):
                if ob.data.materials:
                    for mat in ob.data.materials:
                        if not mat in mat_data:
                            mat_data.append(mat)

    return mat_data
