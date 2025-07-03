"""Node for creating new scenes."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketScene, FNSocketString
from .. import uuid_manager


class FNNewScene(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new scene with the given name."""
    bl_idname = "FNNewScene"
    bl_label = "New Scene"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Scene"
        self.outputs.new('FNSocketScene', "Scene")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Scene"
        
        node_tree = self.id_data
        node_key = f"{self.name}"
        
        scene = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            scene = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.scenes)

        if scene is None:
            scene = bpy.data.scenes.get(name)
            if scene and uuid_manager.get_uuid(scene) is None:
                pass
            else:
                scene = None

        if scene is None:
            scene = bpy.data.scenes.new(name)
            scene.use_extra_user = True
            scene_uuid = uuid_manager.get_or_create_uuid(scene)
            node_tree.set_datablock_uuid(node_key, scene_uuid)
        else:
            if scene.name != name:
                scene.name = name
            scene_uuid = uuid_manager.get_or_create_uuid(scene)
            node_tree.set_datablock_uuid(node_key, scene_uuid)

        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNNewScene)


def unregister():
    bpy.utils.unregister_class(FNNewScene)