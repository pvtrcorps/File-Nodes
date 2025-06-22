
import bpy
from bpy.types import NodeSocket

### Helpers ###
def _color(r,g,b): return (r,g,b,1.0)

# Single datablock sockets
class FNSocketScene(NodeSocket):
    bl_idname = "FNSocketScene"
    bl_label = "Scene"
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='SCENE_DATA')
    def draw_color(self, context, node): return _color(0.6,0.9,1.0)
    value: bpy.props.PointerProperty(type=bpy.types.Scene)

class FNSocketWorld(NodeSocket):
    bl_idname = "FNSocketWorld"
    bl_label = "World"
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='WORLD')
    def draw_color(self, context, node): return _color(0.8,0.8,0.3)
    value: bpy.props.PointerProperty(type=bpy.types.World)

# List sockets just pass python lists at runtime
class FNSocketWorldList(NodeSocket):
    bl_idname = "FNSocketWorldList"
    bl_label = "World List"
    def draw(self, context, layout, node, text):
        layout.label(text=text or self.name, icon='WORLD')
    def draw_color(self, context, node): return _color(0.8,0.8,0.3)

def register():
    for cls in (FNSocketScene, FNSocketWorld, FNSocketWorldList):
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed((FNSocketScene, FNSocketWorld, FNSocketWorldList)):
        bpy.utils.unregister_class(cls)