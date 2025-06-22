
import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketScene

class FNGroupInputNode(Node, FNBaseNode):
    bl_idname = "FNGroupInputNode"
    bl_label = "Group Input"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        # Provide current scene as default input
        return {"Scene": context.scene}

def register():
    bpy.utils.register_class(FNGroupInputNode)
def unregister():
    bpy.utils.unregister_class(FNGroupInputNode)
