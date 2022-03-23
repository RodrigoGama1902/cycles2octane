import bpy

from .convert_nodes import COC_OP_ConvertNodes
from .octane_data_check import COC_OP_OctaneDataCheck


classes = (
    COC_OP_ConvertNodes, COC_OP_OctaneDataCheck
)

def register_operators():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister_operators():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)