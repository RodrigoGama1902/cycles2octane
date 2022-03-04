bl_info = {
    "name": "Cycles to Octane Converter",
    "description": "Node Tree Converter",
    "author": "Rodrigo Gama",
    "version": (0, 1, 2),
    "blender": (2, 93, 0),
    "location": "View3D",
    "category": "3D View"}

def register():
    from .addon.register import register_addon
    register_addon()

def unregister():
    from .addon.register import unregister_addon
    unregister_addon()