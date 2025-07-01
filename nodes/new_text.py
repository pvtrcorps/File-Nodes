"""Node for creating new text datablocks."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketText, FNSocketString


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
        cached = self.cache_get(name)
        if cached is not None:
            return {"Text": cached}

        existing = bpy.data.texts.get(name)
        if existing is not None:
            cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            return {"Text": cached}

        text = bpy.data.texts.new(name)
        self.cache_store(name, text)
        return {"Text": text}


def register():
    bpy.utils.register_class(FNNewText)


def unregister():
    bpy.utils.unregister_class(FNNewText)