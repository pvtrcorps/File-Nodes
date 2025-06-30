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

    def process(self, context, inputs):
        name = inputs.get("Name") or "Text"
        cached = self.cache_get(name)
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if cached is not None:
            return {"Text": cached}

        if ctx:
            storage = getattr(ctx, "_original_values", {})
            for txt in storage.get("created_ids", []):
                if isinstance(txt, bpy.types.Text) and txt.name == name:
                    cached = txt
                    break

        if cached is None:
            existing = bpy.data.texts.get(name)
            if existing is not None:
                cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            if ctx:
                ctx.remember_created_id(cached)
            return {"Text": cached}

        text = bpy.data.texts.new(name)
        self.cache_store(name, text)
        if ctx:
            ctx.remember_created_id(text)
        return {"Text": text}


def register():
    bpy.utils.register_class(FNNewText)


def unregister():
    bpy.utils.unregister_class(FNNewText)
