"""Node for creating new text datablocks."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketText, FNSocketString
from .. import uuid_manager


class FNNewText(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new text datablock."""
    bl_idname = "FNNewText"
    bl_label = "New Text"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Text"
        self.outputs.new('FNSocketText', "Text")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Text"
        
        node_tree = self.id_data
        node_key = f"{self.name}"
        
        text = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            text = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.texts)

        if text is None:
            text = bpy.data.texts.get(name)
            if text and uuid_manager.get_uuid(text) is None:
                pass
            else:
                text = None

        if text is None:
            text = bpy.data.texts.new(name)
            text_uuid = uuid_manager.get_or_create_uuid(text)
            node_tree.set_datablock_uuid(node_key, text_uuid)
        else:
            if text.name != name:
                text.name = name
            text_uuid = uuid_manager.get_or_create_uuid(text)
            node_tree.set_datablock_uuid(node_key, text_uuid)

        return {"Text": text}


def register():
    bpy.utils.register_class(FNNewText)


def unregister():
    bpy.utils.unregister_class(FNNewText)