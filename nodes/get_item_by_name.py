
import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketWorld, FNSocketWorldList

class FNGetWorldByName(Node, FNBaseNode):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"
    bl_idname = "FNGetWorldByName"
    bl_label = "Get World by Name"

    world_name: bpy.props.StringProperty(name='Name', default='')

    def init(self, context):
        self.inputs.new('FNSocketWorldList', "Worlds")
        self.outputs.new('FNSocketWorld', "World")

    def draw_buttons(self, context, layout):
        layout.prop(self, "world_name", text="Name")

    def process(self, context, inputs):
        lst = inputs.get("Worlds", [])
        target = None
        for w in lst:
            if w and w.name == self.world_name:
                target = w
                break
        return {"World": target}

def register():
    bpy.utils.register_class(FNGetWorldByName)
def unregister():
    bpy.utils.unregister_class(FNGetWorldByName)