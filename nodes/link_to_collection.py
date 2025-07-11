"""Node that links objects or collections to a target collection."""

import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketObjectList, FNSocketCollectionList


class FNLinkToCollection(Node, FNBaseNode):
    """Link provided objects or collections to another collection."""
    bl_idname = "FNLinkToCollection"
    bl_label = "Link to Collection"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCollection', "Collection")
        sock = self.inputs.new('FNSocketObjectList', "Objects")
        sock.is_mutable = False
        sock.display_shape = 'SQUARE'
        sock = self.inputs.new('FNSocketCollectionList', "Collections")
        sock.is_mutable = False
        sock.display_shape = 'SQUARE'
        self.outputs.new('FNSocketCollection', "Collection")

    def process(self, context, inputs, manager):
        collection = inputs.get("Collection")
        objects = inputs.get("Objects", []) or []
        collections = inputs.get("Collections", []) or []
        if collection:
            for obj in objects:
                if not obj:
                    continue
                try:
                    name = obj.name
                except ReferenceError:
                    continue  # Object was removed
                if not collection.objects.get(name):
                    collection.objects.link(obj)
            for child in collections:
                if not child:
                    continue
                try:
                    name = child.name
                except ReferenceError:
                    continue  # Collection was removed
                if not collection.children.get(name):
                    collection.children.link(child)
        return {"Collection": collection}

def register():
    bpy.utils.register_class(FNLinkToCollection)

def unregister():
    bpy.utils.unregister_class(FNLinkToCollection)