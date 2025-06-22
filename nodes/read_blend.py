
import bpy, os
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketWorldList

class FNReadBlendNode(Node, FNBaseNode):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"
    bl_idname = "FNReadBlendNode"
    bl_label = "Read Blend File"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def init(self, context):
        self.outputs.new('FNSocketWorldList', "Worlds")

    def draw_buttons(self, context, layout):
        layout.prop(self, "filepath", text="")

    def process(self, context, inputs):
        if not self.filepath or not os.path.isfile(bpy.path.abspath(self.filepath)):
            self.report({'WARNING'}, "Invalid filepath")
            return {"Worlds": []}
        worlds_out = []
        abs_path = bpy.path.abspath(self.filepath)
        with bpy.data.libraries.load(abs_path, link=True) as (data_from, data_to):
            data_to.worlds = data_from.worlds
        for w in data_to.worlds:
            worlds_out.append(bpy.data.worlds.get(w))
        return {"Worlds": worlds_out}

def register():
    bpy.utils.register_class(FNReadBlendNode)
def unregister():
    bpy.utils.unregister_class(FNReadBlendNode)