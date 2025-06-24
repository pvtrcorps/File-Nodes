import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketObject, FNSocketString


class FNCollectionInstance(Node, FNBaseNode):
    bl_idname = "FNCollectionInstance"
    bl_label = "Collection Instance"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        name_sock = self.inputs.new('FNSocketString', "Name")
        name_sock.value = "Collection Instance"
        self.inputs.new('FNSocketCollection', "Collection")
        self.outputs.new('FNSocketObject', "Object")

    def process(self, context, inputs):
        name = inputs.get("Name") or "Collection Instance"
        collection = inputs.get("Collection")
        obj = bpy.data.objects.new(name, None)
        obj.instance_type = 'COLLECTION'
        obj.instance_collection = collection
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNCollectionInstance)


def unregister():
    bpy.utils.unregister_class(FNCollectionInstance)
