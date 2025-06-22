import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import (
    FNSocketScene, FNSocketObjectList, FNSocketCollectionList
)
from ..operators import get_active_mod_item

class FNLinkToScene(Node, FNBaseNode):
    bl_idname = "FNLinkToScene"
    bl_label = "Link to Scene"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        self.inputs.new('FNSocketObjectList', "Objects")
        self.inputs.new('FNSocketCollectionList', "Collections")
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        objects = inputs.get("Objects", []) or []
        collections = inputs.get("Collections", []) or []
        if scene:
            root = scene.collection
            mod = get_active_mod_item()
            for obj in objects:
                if obj and not root.objects.get(obj.name):
                    root.objects.link(obj)
                    if mod:
                        storage = mod._ensure_storage()
                        storage['linked_objects'].append((root, obj))
            for coll in collections:
                if coll and not root.children.get(coll.name):
                    root.children.link(coll)
                    if mod:
                        storage = mod._ensure_storage()
                        storage['linked_collections'].append((root, coll))
        return {"Scene": scene}

def register():
    bpy.utils.register_class(FNLinkToScene)

def unregister():
    bpy.utils.unregister_class(FNLinkToScene)
