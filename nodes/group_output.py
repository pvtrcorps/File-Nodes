
import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketScene

class FNGroupOutputNode(Node, FNBaseNode):
    bl_idname = "FNGroupOutputNode"
    bl_label = "Group Output"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        # Terminal node, no action needed
        return {}

def register():
    bpy.utils.register_class(FNGroupOutputNode)
def unregister():
    bpy.utils.unregister_class(FNGroupOutputNode)
