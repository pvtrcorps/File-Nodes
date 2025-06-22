import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketObjectList
from ..operators import get_active_mod_item

class FNLinkToCollection(Node, FNBaseNode):
    bl_idname = "FNLinkToCollection"
    bl_label = "Link to Collection"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCollection', "Collection")
        self.inputs.new('FNSocketObjectList', "Objects")
        self.outputs.new('FNSocketCollection', "Collection")

    def process(self, context, inputs):
        collection = inputs.get("Collection")
        objects = inputs.get("Objects", []) or []
        if collection:
            mod = get_active_mod_item()
            for obj in objects:
                if obj and not collection.objects.get(obj.name):
                    collection.objects.link(obj)
                    if mod:
                        storage = mod._ensure_storage()
                        storage['linked_objects'].append((collection, obj))
        return {"Collection": collection}

def register():
    bpy.utils.register_class(FNLinkToCollection)

def unregister():
    bpy.utils.unregister_class(FNLinkToCollection)
