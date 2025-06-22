
import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketWorld, FNSocketWorldList

class FNCreateWorldList(Node, FNBaseNode):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"
    bl_idname = "FNCreateWorldList"
    bl_label = "Create World List"

    def init(self, context):
        self.inputs.new('FNSocketWorld', "World 1")
        self.inputs.new('FNSocketWorld', "World 2")
        self.outputs.new('FNSocketWorldList', "Worlds")

    def process(self, context, inputs):
        lst = []
        for sock in self.inputs:
            if sock.is_linked:
                # value will be resolved in evaluator
                lst.append(inputs.get(sock.name))
            else:
                if sock.value:
                    lst.append(sock.value)
        return {"Worlds": lst}

def register():
    bpy.utils.register_class(FNCreateWorldList)
def unregister():
    bpy.utils.unregister_class(FNCreateWorldList)