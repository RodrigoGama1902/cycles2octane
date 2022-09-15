bl_info = {
    "name": "Cycles2Octane Converter",
    "description": "Convert material nodes from cycles to octane",
    "author": "Rodrigo Gama",
    "version": (0, 1, 6, 2),
    "blender": (3, 0, 1),
    "location": "View3D",
    "category": "3D View"}


def register():
    from .addon.register import register_addon
    register_addon()


def unregister():
    from .addon.register import unregister_addon
    unregister_addon()
