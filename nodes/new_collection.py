import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketCollection
from ..operators import auto_evaluate_if_enabled

class FNNewCollection(Node, FNBaseNode):
    bl_idname = "FNNewCollection"
    bl_label = "New Collection"

    name: bpy.props.StringProperty(name="Name", default="Collection", update=auto_evaluate_if_enabled)
    color_tag: bpy.props.EnumProperty(
        name="Color Tag",
        items=[
            ('NONE', 'None', ''),
            ('COLOR_01', '01', ''),
            ('COLOR_02', '02', ''),
            ('COLOR_03', '03', ''),
            ('COLOR_04', '04', ''),
            ('COLOR_05', '05', ''),
            ('COLOR_06', '06', ''),
            ('COLOR_07', '07', ''),
            ('COLOR_08', '08', ''),
        ],
        default='NONE',
        update=auto_evaluate_if_enabled
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.outputs.new('FNSocketCollection', "Collection")

    def draw_buttons(self, context, layout):
        layout.prop(self, "name", text="Name")
        layout.prop(self, "color_tag", text="Color Tag")

    def process(self, context, inputs):
        coll = bpy.data.collections.new(self.name)
        coll.color_tag = self.color_tag
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNNewCollection)


def unregister():
    bpy.utils.unregister_class(FNNewCollection)
