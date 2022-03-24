bl_info = {
    "name": "Cycles to Octane Converter",
    "description": "Node Tree Converter",
    "author": "Rodrigo Gama",
    "version": (0, 1, 3),
    "blender": (3, 0, 1),
    "location": "View3D",
    "category": "3D View"}

def register():
    from .addon.register import register_addon
    register_addon()


def unregister():
    from .addon.register import unregister_addon
    unregister_addon()
