import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import (
    FNSocketScene, FNSocketObjectList, FNSocketCollectionList
)


class FNLinkToScene(Node, FNBaseNode):
    bl_idname = "FNLinkToScene"
    bl_label = "Link to Scene"
    color_tag = 'OUTPUT'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketObjectList', "Objects")
        sock.display_shape = 'SQUARE'
        sock = self.inputs.new('FNSocketCollectionList', "Collections")
        sock.display_shape = 'SQUARE'
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        objects = inputs.get("Objects", []) or []
        collections = inputs.get("Collections", []) or []
        if scene:
            root = scene.collection
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            for obj in objects:
                if not obj:
                    continue
                try:
                    name = obj.name
                except ReferenceError:
                    continue  # Object was removed
                if not root.objects.get(name):
                    root.objects.link(obj)
                    if ctx:
                        ctx.remember_object_link(root, obj)
            for coll in collections:
                if not coll:
                    continue
                try:
                    name = coll.name
                except ReferenceError:
                    continue  # Collection was removed
                if not root.children.get(name):
                    root.children.link(coll)
                    if ctx:
                        ctx.remember_collection_link(root, coll)
        return {"Scene": scene}

def register():
    bpy.utils.register_class(FNLinkToScene)

def unregister():
    bpy.utils.unregister_class(FNLinkToScene)
