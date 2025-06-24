import bpy, os, warnings
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketString, FNSocketObjectList
from ..operators import get_active_mod_item

class FNImportAlembicNode(Node, FNBaseNode):
    """Import objects from an Alembic file."""
    bl_idname = "FNImportAlembicNode"
    bl_label = "Import Alembic"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "File Path")
        sock.display_shape = 'SQUARE'
        sock = self.outputs.new('FNSocketObjectList', "Objects")
        sock.display_shape = 'SQUARE'

    def process(self, context, inputs):
        filepath = inputs.get("File Path", "") or ""
        abs_path = bpy.path.abspath(filepath)
        result = {"Objects": []}
        if not filepath or not os.path.isfile(abs_path):
            warnings.warn("Invalid filepath")
            return result
        before = set(bpy.data.objects)
        try:
            bpy.ops.wm.alembic_import(filepath=abs_path, as_background_job=False)
        except Exception as e:
            warnings.warn(f"Failed to import Alembic: {e}")
            return result
        after = set(bpy.data.objects)
        imported = [obj for obj in after - before]
        result["Objects"] = imported
        mod = get_active_mod_item()
        if mod:
            storage = mod._ensure_storage()
            storage.setdefault("imported_objects", []).extend(imported)
        return result

def register():
    bpy.utils.register_class(FNImportAlembicNode)

def unregister():
    bpy.utils.unregister_class(FNImportAlembicNode)
