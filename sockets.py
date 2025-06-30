
import bpy
from bpy.types import NodeSocket
from .operators import auto_evaluate_if_enabled

### Helpers ###
def _color(r,g,b): return (r,g,b,1.0)

# Draw helper for value sockets. When the socket is not linked and is an input,
# expose its 'value' property so users can pick a value directly from the node.
def _draw_value_socket(sock, layout, text, icon='NONE'):
    show = getattr(sock, 'show_selector', True)
    if sock.is_output or sock.is_linked or not show:
        layout.label(text=text or sock.name, icon=icon)
    else:
        layout.prop(sock, 'value', text=text or sock.name, icon=icon)

# Basic value sockets
class FNSocketBool(NodeSocket):
    bl_idname = "FNSocketBool"
    bl_label = "Boolean"
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text)
    def draw_color(self, context, node):
        return _color(1.0, 0.4118, 0.8627)
    value: bpy.props.BoolProperty(update=auto_evaluate_if_enabled)

class FNSocketExec(NodeSocket):
    bl_idname = "FNSocketExec"
    bl_label = "Execution"
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'PLAY')
    def draw_color(self, context, node):
        return _color(1.0, 0.5, 0.0)
    value: bpy.props.BoolProperty(update=auto_evaluate_if_enabled)

class FNSocketFloat(NodeSocket):
    bl_idname = "FNSocketFloat"
    bl_label = "Float"
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text)
    def draw_color(self, context, node):
        return _color(0.7765, 0.7765, 0.7765)
    value: bpy.props.FloatProperty(update=auto_evaluate_if_enabled)

class FNSocketVector(NodeSocket):
    bl_idname = "FNSocketVector"
    bl_label = "Vector"
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text)
    def draw_color(self, context, node):
        return _color(0.3882, 0.3882, 0.7804)
    value: bpy.props.FloatVectorProperty(size=3, update=auto_evaluate_if_enabled)

class FNSocketInt(NodeSocket):
    bl_idname = "FNSocketInt"
    bl_label = "Integer"
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text)
    def draw_color(self, context, node):
        return _color(0.1765, 0.6392, 0.4078)
    value: bpy.props.IntProperty(update=auto_evaluate_if_enabled)

class FNSocketString(NodeSocket):
    bl_idname = "FNSocketString"
    bl_label = "String"
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text)
    def draw_color(self, context, node):
        return _color(0.3137, 0.6667, 1.0)
    value: bpy.props.StringProperty(update=auto_evaluate_if_enabled)

class FNSocketStringList(NodeSocket):
    bl_idname = "FNSocketStringList"
    bl_label = "String List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name)
    def draw_color(self, context, node):
        return _color(0.3137, 0.6667, 1.0)

# Single datablock sockets
class FNSocketScene(NodeSocket):
    bl_idname = "FNSocketScene"
    bl_label = "Scene"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'SCENE_DATA')
    def draw_color(self, context, node):
        return _color(1.0, 1.0, 1.0)
    value: bpy.props.PointerProperty(type=bpy.types.Scene, update=auto_evaluate_if_enabled)


class FNSocketObject(NodeSocket):
    bl_idname = "FNSocketObject"
    bl_label = "Object"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'OBJECT_DATA')
    def draw_color(self, context, node):
        return _color(0.9608, 0.5529, 0.0824)
    value: bpy.props.PointerProperty(type=bpy.types.Object, update=auto_evaluate_if_enabled)

class FNSocketCollection(NodeSocket):
    bl_idname = "FNSocketCollection"
    bl_label = "Collection"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'OUTLINER_COLLECTION')
    def draw_color(self, context, node):
        return _color(0.8, 0.8, 0.8)
    value: bpy.props.PointerProperty(type=bpy.types.Collection, update=auto_evaluate_if_enabled)

class FNSocketCamera(NodeSocket):
    bl_idname = "FNSocketCamera"
    bl_label = "Camera"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'CAMERA_DATA')
    def draw_color(self, context, node):
        return _color(0.8, 0.6, 0.4)
    value: bpy.props.PointerProperty(type=bpy.types.Camera, update=auto_evaluate_if_enabled)

class FNSocketImage(NodeSocket):
    bl_idname = "FNSocketImage"
    bl_label = "Image"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'IMAGE_DATA')
    def draw_color(self, context, node):
        return _color(0.6, 0.6, 0.6)
    value: bpy.props.PointerProperty(type=bpy.types.Image, update=auto_evaluate_if_enabled)

class FNSocketLight(NodeSocket):
    bl_idname = "FNSocketLight"
    bl_label = "Light"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'LIGHT_DATA')
    def draw_color(self, context, node):
        return _color(1.0, 0.9, 0.3)
    value: bpy.props.PointerProperty(type=bpy.types.Light, update=auto_evaluate_if_enabled)

class FNSocketMaterial(NodeSocket):
    bl_idname = "FNSocketMaterial"
    bl_label = "Material"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'MATERIAL_DATA')
    def draw_color(self, context, node):
        return _color(0.8863, 0.3137, 0.3137)
    value: bpy.props.PointerProperty(type=bpy.types.Material, update=auto_evaluate_if_enabled)

class FNSocketMesh(NodeSocket):
    bl_idname = "FNSocketMesh"
    bl_label = "Mesh"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'MESH_DATA')
    def draw_color(self, context, node):
        return _color(0.2118, 0.7529, 0.4471)
    value: bpy.props.PointerProperty(type=bpy.types.Mesh, update=auto_evaluate_if_enabled)

class FNSocketNodeTree(NodeSocket):
    bl_idname = "FNSocketNodeTree"
    bl_label = "Node Tree"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'NODETREE')
    def draw_color(self, context, node):
        return _color(0.7, 0.9, 0.7)
    value: bpy.props.PointerProperty(type=bpy.types.NodeTree, update=auto_evaluate_if_enabled)

class FNSocketText(NodeSocket):
    bl_idname = "FNSocketText"
    bl_label = "Text"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'TEXT')
    def draw_color(self, context, node):
        return _color(0.9, 0.9, 0.6)
    value: bpy.props.PointerProperty(type=bpy.types.Text, update=auto_evaluate_if_enabled)

class FNSocketWorkSpace(NodeSocket):
    bl_idname = "FNSocketWorkSpace"
    bl_label = "WorkSpace"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'WORKSPACE')
    def draw_color(self, context, node):
        return _color(0.5, 0.7, 0.9)
    value: bpy.props.PointerProperty(type=bpy.types.WorkSpace, update=auto_evaluate_if_enabled)

class FNSocketViewLayer(NodeSocket):
    bl_idname = "FNSocketViewLayer"
    bl_label = "View Layer"
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='RENDERLAYERS')
    def draw_color(self, context, node):
        return _color(0.6, 0.6, 0.6)
    # Blender does not support PointerProperty for ViewLayer, store the name instead.
    value: bpy.props.StringProperty(update=auto_evaluate_if_enabled)

class FNSocketWorld(NodeSocket):
    bl_idname = "FNSocketWorld"
    bl_label = "World"
    show_selector: bpy.props.BoolProperty(default=False)
    def draw(self, context, layout, node, text):
        _draw_value_socket(self, layout, text, 'WORLD')
    def draw_color(self, context, node):
        return _color(0.8, 0.8, 0.3)
    value: bpy.props.PointerProperty(type=bpy.types.World, update=auto_evaluate_if_enabled)

# List sockets just pass python lists at runtime
class FNSocketSceneList(NodeSocket):
    bl_idname = "FNSocketSceneList"
    bl_label = "Scene List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='SCENE_DATA')
    def draw_color(self, context, node):
        return _color(1.0, 1.0, 1.0)

class FNSocketObjectList(NodeSocket):
    bl_idname = "FNSocketObjectList"
    bl_label = "Object List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='OBJECT_DATA')
    def draw_color(self, context, node):
        return _color(0.9608, 0.5529, 0.0824)

class FNSocketCollectionList(NodeSocket):
    bl_idname = "FNSocketCollectionList"
    bl_label = "Collection List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='OUTLINER_COLLECTION')
    def draw_color(self, context, node):
        return _color(1.0, 1.0, 1.0)

class FNSocketWorldList(NodeSocket):
    bl_idname = "FNSocketWorldList"
    bl_label = "World List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='WORLD')
    def draw_color(self, context, node):
        return _color(0.8, 0.8, 0.3)

class FNSocketCameraList(NodeSocket):
    bl_idname = "FNSocketCameraList"
    bl_label = "Camera List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='CAMERA_DATA')
    def draw_color(self, context, node):
        return _color(0.8, 0.6, 0.4)

class FNSocketImageList(NodeSocket):
    bl_idname = "FNSocketImageList"
    bl_label = "Image List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='IMAGE_DATA')
    def draw_color(self, context, node):
        return _color(0.6, 0.6, 0.6)

class FNSocketLightList(NodeSocket):
    bl_idname = "FNSocketLightList"
    bl_label = "Light List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='LIGHT_DATA')
    def draw_color(self, context, node):
        return _color(1.0, 0.9, 0.3)

class FNSocketMaterialList(NodeSocket):
    bl_idname = "FNSocketMaterialList"
    bl_label = "Material List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='MATERIAL_DATA')
    def draw_color(self, context, node):
        return _color(0.8863, 0.3137, 0.3137)

class FNSocketMeshList(NodeSocket):
    bl_idname = "FNSocketMeshList"
    bl_label = "Mesh List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='MESH_DATA')
    def draw_color(self, context, node):
        return _color(0.2118, 0.7529, 0.4471)

class FNSocketNodeTreeList(NodeSocket):
    bl_idname = "FNSocketNodeTreeList"
    bl_label = "Node Tree List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='NODETREE')
    def draw_color(self, context, node):
        return _color(0.7, 0.9, 0.7)

class FNSocketTextList(NodeSocket):
    bl_idname = "FNSocketTextList"
    bl_label = "Text List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='TEXT')
    def draw_color(self, context, node):
        return _color(0.9, 0.9, 0.6)

class FNSocketWorkSpaceList(NodeSocket):
    bl_idname = "FNSocketWorkSpaceList"
    bl_label = "WorkSpace List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='WORKSPACE')
    def draw_color(self, context, node):
        return _color(0.5, 0.7, 0.9)

class FNSocketViewLayerList(NodeSocket):
    bl_idname = "FNSocketViewLayerList"
    bl_label = "View Layer List"
    display_shape = 'SQUARE'
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='RENDERLAYERS')
    def draw_color(self, context, node):
        return _color(0.6, 0.6, 0.6)

_all_sockets = (
    FNSocketBool, FNSocketExec, FNSocketFloat, FNSocketVector, FNSocketInt,
    FNSocketString, FNSocketStringList,
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
    FNSocketViewLayer,
    FNSocketSceneList, FNSocketObjectList, FNSocketCollectionList, FNSocketWorldList,
    FNSocketCameraList, FNSocketImageList, FNSocketLightList, FNSocketMaterialList,
    FNSocketMeshList, FNSocketNodeTreeList, FNSocketTextList, FNSocketWorkSpaceList,
    FNSocketViewLayerList,
)

def register():
    for cls in _all_sockets:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(_all_sockets):
        bpy.utils.unregister_class(cls)
