import bpy

from ..utility.functions import get_materials_selected

class COC_PT_ObjPanel(bpy.types.Panel):    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Ilustraviz'
    
class COC_PT_MainPanel(COC_PT_ObjPanel):
    bl_label = "Cycles to Octane"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self,context):
        pass     

class COC_PT_NodeConverter(COC_PT_ObjPanel):
    """Convert Materials"""
    
    bl_label = "Material Converter"
    bl_parent_id = "COC_PT_MainPanel"
    
    def draw(self, context):
        
        layout = self.layout
                
        props = bpy.context.scene.cycles2octane
        
        row = layout.row()
        row.prop(props,"select_method")
        box = layout.box()
        box.label(text="Convert To:")
        box.prop(props,"convert_to",expand=True)
        
        selected_materials = len(get_materials_selected())
        
        col = layout.column(align=True)
        box = col.box()
        box.label(text=str(selected_materials) + (" Material Selected" if selected_materials == 1 else " Materials Selected"))
        row = col.row(align=True)
        
        row.scale_y = 1.3        
        row.operator("coc.convert_nodes",icon="NODETREE")
        row = layout.row()
        row.operator("coc.octanedatacheck")
        