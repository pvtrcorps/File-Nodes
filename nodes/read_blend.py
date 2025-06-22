
import bpy, os
from bpy.types import Node
from ..operators import auto_evaluate_if_enabled
from .base import FNBaseNode
from ..sockets import (
    FNSocketSceneList, FNSocketObjectList, FNSocketCollectionList, FNSocketWorldList,
    FNSocketCameraList, FNSocketImageList, FNSocketLightList, FNSocketMaterialList,
    FNSocketMeshList, FNSocketNodeTreeList, FNSocketTextList, FNSocketWorkSpaceList,
)

class FNReadBlendNode(Node, FNBaseNode):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"
    bl_idname = "FNReadBlendNode"
    bl_label = "Read Blend File"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH', update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketSceneList', "Scenes")
        self.outputs.new('FNSocketObjectList', "Objects")
        self.outputs.new('FNSocketCollectionList', "Collections")
        self.outputs.new('FNSocketWorldList', "Worlds")
        self.outputs.new('FNSocketCameraList', "Cameras")
        self.outputs.new('FNSocketImageList', "Images")
        self.outputs.new('FNSocketLightList', "Lights")
        self.outputs.new('FNSocketMaterialList', "Materials")
        self.outputs.new('FNSocketMeshList', "Meshes")
        self.outputs.new('FNSocketNodeTreeList', "NodeTrees")
        self.outputs.new('FNSocketTextList', "Texts")
        self.outputs.new('FNSocketWorkSpaceList', "WorkSpaces")

    def draw_buttons(self, context, layout):
        layout.prop(self, "filepath", text="")

    def process(self, context, inputs):
        if not self.filepath or not os.path.isfile(bpy.path.abspath(self.filepath)):
            self.report({'WARNING'}, "Invalid filepath")
            return {
                "Scenes": [], "Objects": [], "Collections": [], "Worlds": [],
                "Cameras": [], "Images": [], "Lights": [], "Materials": [],
                "Meshes": [], "NodeTrees": [], "Texts": [], "WorkSpaces": [],
            }
        scenes_out, objects_out, collections_out, worlds_out = [], [], [], []
        cameras_out, images_out, lights_out = [], [], []
        materials_out, meshes_out, nodetrees_out = [], [], []
        texts_out, workspaces_out = [], []
        abs_path = bpy.path.abspath(self.filepath)
        with bpy.data.libraries.load(abs_path, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
            data_to.objects = data_from.objects
            data_to.collections = data_from.collections
            data_to.worlds = data_from.worlds
            data_to.cameras = data_from.cameras
            data_to.images = data_from.images
            data_to.lights = data_from.lights
            data_to.materials = data_from.materials
            data_to.meshes = data_from.meshes
            data_to.node_groups = data_from.node_groups
            data_to.texts = data_from.texts
            data_to.workspaces = data_from.workspaces
        for s in data_to.scenes:
            scenes_out.append(s if isinstance(s, bpy.types.Scene) else bpy.data.scenes.get(s))
        for o in data_to.objects:
            objects_out.append(o if isinstance(o, bpy.types.Object) else bpy.data.objects.get(o))
        for c in data_to.collections:
            collections_out.append(c if isinstance(c, bpy.types.Collection) else bpy.data.collections.get(c))
        for w in data_to.worlds:
            worlds_out.append(w if isinstance(w, bpy.types.World) else bpy.data.worlds.get(w))
        for cam in data_to.cameras:
            cameras_out.append(cam if isinstance(cam, bpy.types.Camera) else bpy.data.cameras.get(cam))
        for img in data_to.images:
            images_out.append(img if isinstance(img, bpy.types.Image) else bpy.data.images.get(img))
        for li in data_to.lights:
            lights_out.append(li if isinstance(li, bpy.types.Light) else bpy.data.lights.get(li))
        for mat in data_to.materials:
            materials_out.append(mat if isinstance(mat, bpy.types.Material) else bpy.data.materials.get(mat))
        for me in data_to.meshes:
            meshes_out.append(me if isinstance(me, bpy.types.Mesh) else bpy.data.meshes.get(me))
        for nt in data_to.node_groups:
            nodetrees_out.append(nt if isinstance(nt, bpy.types.NodeTree) else bpy.data.node_groups.get(nt))
        for txt in data_to.texts:
            texts_out.append(txt if isinstance(txt, bpy.types.Text) else bpy.data.texts.get(txt))
        for ws in data_to.workspaces:
            workspaces_out.append(ws if isinstance(ws, bpy.types.WorkSpace) else bpy.data.workspaces.get(ws))
        return {
            "Scenes": scenes_out,
            "Objects": objects_out,
            "Collections": collections_out,
            "Worlds": worlds_out,
            "Cameras": cameras_out,
            "Images": images_out,
            "Lights": lights_out,
            "Materials": materials_out,
            "Meshes": meshes_out,
            "NodeTrees": nodetrees_out,
            "Texts": texts_out,
            "WorkSpaces": workspaces_out,
        }

def register():
    bpy.utils.register_class(FNReadBlendNode)
def unregister():
    bpy.utils.unregister_class(FNReadBlendNode)