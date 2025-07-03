"""Node for creating new view layers."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketScene, FNSocketString, FNSocketViewLayer
from .. import uuid_manager


class FNNewViewLayer(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new view layer in the given scene."""
    bl_idname = "FNNewViewLayer"
    bl_label = "New ViewLayer"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "ViewLayer"
        self.outputs.new('FNSocketViewLayer', "ViewLayer")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        scene = inputs.get("Scene")
        if not scene:
            return {"ViewLayer": None}
        name = inputs.get("Name") or "ViewLayer"
        
        node_tree = self.id_data
        node_key = f"{self.name}_{scene.name}"
        
        view_layer = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            # View layers are not directly in bpy.data, so we need to search within the scene
            for vl in scene.view_layers:
                if uuid_manager.get_uuid(vl) == existing_uuid:
                    view_layer = vl
                    break

        if view_layer is None:
            view_layer = scene.view_layers.get(name)
            if view_layer and uuid_manager.get_uuid(view_layer) is None:
                pass
            else:
                view_layer = None

        if view_layer is None:
            view_layer = scene.view_layers.new(name)
            vl_uuid = uuid_manager.get_or_create_uuid(view_layer)
            node_tree.set_datablock_uuid(node_key, vl_uuid)
        else:
            if view_layer.name != name:
                view_layer.name = name
            vl_uuid = uuid_manager.get_or_create_uuid(view_layer)
            node_tree.set_datablock_uuid(node_key, vl_uuid)

        return {"ViewLayer": view_layer}


def register():
    bpy.utils.register_class(FNNewViewLayer)


def unregister():
    bpy.utils.unregister_class(FNNewViewLayer)