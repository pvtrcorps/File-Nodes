import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketString, FNSocketObjectList
from ..operators import get_active_mod_item


class FNImportAlembic(Node, FNBaseNode):
    bl_idname = "FNImportAlembicNode"
    bl_label = "Import Alembic"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketString', "File Path")
        sock = self.outputs.new('FNSocketObjectList', "Objects")
        sock.display_shape = 'SQUARE'

    def process(self, context, inputs):
        filepath = inputs.get("File Path") or ""
        abs_path = bpy.path.abspath(filepath)
        objects = []
        if filepath:
            scene = context.scene
            before = set(scene.objects)
            try:
                bpy.ops.wm.alembic_import(filepath=abs_path)
            except Exception:
                return {"Objects": []}
            for obj in scene.objects:
                if obj not in before:
                    objects.append(obj)
            mod = get_active_mod_item()
            if mod:
                root = scene.collection
                for obj in objects:
                    mod.remember_object_link(root, obj)
        return {"Objects": objects}


def register():
    bpy.utils.register_class(FNImportAlembic)


def unregister():
    bpy.utils.unregister_class(FNImportAlembic)
