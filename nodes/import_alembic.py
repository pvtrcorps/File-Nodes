"""Node to import objects from an Alembic file."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketString, FNSocketObjectList
from ..cow_engine import ensure_mutable


_abc_cache = {}


class FNImportAlembic(Node, FNBaseNode):
    """Load objects from an Alembic archive."""
    bl_idname = "FNImportAlembicNode"
    bl_label = "Import Alembic"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketString', "File Path")
        sock = self.outputs.new('FNSocketObjectList', "Objects")
        sock.display_shape = 'SQUARE'

    def free(self):
        self._invalidate_cache()

    def _invalidate_cache(self, path=None):
        path = path or getattr(self, "_cached_filepath", None)
        if path:
            _abc_cache.pop(path, None)
            self._cached_filepath = None

    def process(self, context, inputs):
        filepath = inputs.get("File Path") or ""
        abs_path = bpy.path.abspath(filepath)
        if filepath != getattr(self, "_cached_filepath", None):
            self._invalidate_cache()
        objects = []
        if not filepath:
            self._cached_filepath = None
            return {"Objects": objects}

        cached = _abc_cache.get(abs_path)
        if cached is not None:
            self._cached_filepath = abs_path
            return {"Objects": cached}

        scene = context.scene
        before = set(scene.objects)
        try:
            bpy.ops.wm.alembic_import(filepath=abs_path)
        except Exception:
            self._cached_filepath = None
            return {"Objects": objects}
        for obj in scene.objects:
            if obj not in before:
                objects.append(obj)
        ensure_mutable(scene)
        _abc_cache[abs_path] = objects
        self._cached_filepath = abs_path
        return {"Objects": objects}


def register():
    bpy.utils.register_class(FNImportAlembic)


def unregister():
    bpy.utils.unregister_class(FNImportAlembic)
