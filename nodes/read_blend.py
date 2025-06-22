
import bpy, os
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import (
    FNSocketSceneList,
    FNSocketObjectList,
    FNSocketCollectionList,
    FNSocketWorldList,
)

class FNReadBlendNode(Node, FNBaseNode):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"
    bl_idname = "FNReadBlendNode"
    bl_label = "Read Blend File"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def init(self, context):
        self.outputs.new('FNSocketSceneList', "Scenes")
        self.outputs.new('FNSocketObjectList', "Objects")
        self.outputs.new('FNSocketCollectionList', "Collections")
        self.outputs.new('FNSocketWorldList', "Worlds")

    def draw_buttons(self, context, layout):
        layout.prop(self, "filepath", text="")

    def process(self, context, inputs):
        if not self.filepath or not os.path.isfile(bpy.path.abspath(self.filepath)):
            self.report({'WARNING'}, "Invalid filepath")
            return {"Scenes": [], "Objects": [], "Collections": [], "Worlds": []}
        scenes_out, objects_out, collections_out, worlds_out = [], [], [], []
        abs_path = bpy.path.abspath(self.filepath)
        with bpy.data.libraries.load(abs_path, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
            data_to.objects = data_from.objects
            data_to.collections = data_from.collections
            data_to.worlds = data_from.worlds
        for s in data_to.scenes:
            scenes_out.append(s if isinstance(s, bpy.types.Scene) else bpy.data.scenes.get(s))
        for o in data_to.objects:
            objects_out.append(o if isinstance(o, bpy.types.Object) else bpy.data.objects.get(o))
        for c in data_to.collections:
            collections_out.append(c if isinstance(c, bpy.types.Collection) else bpy.data.collections.get(c))
        for w in data_to.worlds:
            worlds_out.append(w if isinstance(w, bpy.types.World) else bpy.data.worlds.get(w))
        return {
            "Scenes": scenes_out,
            "Objects": objects_out,
            "Collections": collections_out,
            "Worlds": worlds_out,
        }

def register():
    bpy.utils.register_class(FNReadBlendNode)
def unregister():
    bpy.utils.unregister_class(FNReadBlendNode)