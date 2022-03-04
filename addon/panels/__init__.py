import bpy

from .main_panel import COC_PT_MainPanel, COC_PT_NodeConverter

classes = (
    COC_PT_MainPanel, COC_PT_NodeConverter
)


def register_panels():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    

def unregister_panels():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)