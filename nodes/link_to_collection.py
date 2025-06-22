import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketObjectList, FNSocketCollectionList
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
        self.inputs.new('FNSocketCollectionList', "Collections")
        self.outputs.new('FNSocketCollection', "Collection")

    def process(self, context, inputs):
        collection = inputs.get("Collection")
        objects = inputs.get("Objects", []) or []
        collections = inputs.get("Collections", []) or []
        if collection:
            mod = get_active_mod_item()
            for obj in objects:
                if obj and not collection.objects.get(obj.name):
                    collection.objects.link(obj)
                    if mod:
                        storage = mod._ensure_storage()
                        storage['linked_objects'].append((collection, obj))
            for child in collections:
                if child and not collection.children.get(child.name):
                    collection.children.link(child)
                    if mod:
                        storage = mod._ensure_storage()
                        storage['linked_collections'].append((collection, child))
        return {"Collection": collection}

def register():
    bpy.utils.register_class(FNLinkToCollection)

def unregister():
    bpy.utils.unregister_class(FNLinkToCollection)
