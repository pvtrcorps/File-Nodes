import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketMaterial
from ..operators import auto_evaluate_if_enabled

class FNNewMaterial(Node, FNBaseNode):
    bl_idname = "FNNewMaterial"
    bl_label = "New Material"

    name: bpy.props.StringProperty(name="Name", default="Material", update=auto_evaluate_if_enabled)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.outputs.new('FNSocketMaterial', "Material")

    def draw_buttons(self, context, layout):
        layout.prop(self, "name", text="Name")

    def process(self, context, inputs):
        mat = bpy.data.materials.new(self.name)
        return {"Material": mat}


def register():
    bpy.utils.register_class(FNNewMaterial)


def unregister():
    bpy.utils.unregister_class(FNNewMaterial)
