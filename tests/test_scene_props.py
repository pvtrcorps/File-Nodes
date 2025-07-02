import sys
import os
import importlib.util
import types

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

# -- fake bpy --
class _FakeID:
    def __init__(self, name):
        self.name = name
    def as_pointer(self):
        return id(self)

class _DataCollection(dict):
    def __init__(self, cls):
        super().__init__()
        self.cls = cls
    def new(self, name, *args, **kwargs):
        obj = self.cls(name, *args, **kwargs)
        self[name] = obj
        return obj
    def remove(self, obj):
        self.pop(obj.name, None)

class Scene(_FakeID):
    def __init__(self, name):
        super().__init__(name)
        self.frame_start = 1
        self.frame_end = 250
        self.camera = None

class Object(_FakeID):
    pass

class Camera(_FakeID):
    pass

def _make_bpy_module():
    bpy = types.ModuleType("bpy")
    bpy.__path__ = []
    types_mod = types.ModuleType("bpy.types")
    types_mod.Scene = Scene
    types_mod.Object = Object
    types_mod.Camera = Camera
    types_mod.Node = type("Node", (), {})
    types_mod.NodeSocket = type("NodeSocket", (), {})
    bpy.types = types_mod
    sys.modules["bpy.types"] = types_mod

    bpy.data = types.SimpleNamespace(
        scenes=_DataCollection(Scene),
        objects=_DataCollection(Object),
        cameras=_DataCollection(Camera),
    )

    bpy.props = types.SimpleNamespace(
        BoolProperty=lambda **k: None,
        IntProperty=lambda **k: None,
        FloatProperty=lambda **k: None,
        FloatVectorProperty=lambda **k: None,
        StringProperty=lambda **k: None,
        PointerProperty=lambda **k: None,
        CollectionProperty=lambda **k: None,
        EnumProperty=lambda **k: None,
    )
    bpy.utils = types.SimpleNamespace(register_class=lambda cls: None, unregister_class=lambda cls: None)
    bpy.context = types.SimpleNamespace(scene=None)
    return bpy

bpy = _make_bpy_module()
sys.modules["bpy"] = bpy

# -- stub modules --
spec_base = importlib.util.spec_from_file_location("addon.nodes.base", os.path.join(ROOT, "nodes", "base.py"))
base_mod = importlib.util.module_from_spec(spec_base)
base_mod.bpy = bpy
spec_base.loader.exec_module(base_mod)
sys.modules["addon.nodes.base"] = base_mod

ops_mod = types.ModuleType("addon.operators")
ops_mod.auto_evaluate_if_enabled = lambda *a, **k: None
sys.modules["addon.operators"] = ops_mod

sockets_mod = types.ModuleType("addon.sockets")
for cls_name in ["FNSocketScene", "FNSocketInt", "FNSocketObject"]:
    setattr(sockets_mod, cls_name, type(cls_name, (), {}))
sys.modules["addon.sockets"] = sockets_mod

# -- load scene_props module --
spec = importlib.util.spec_from_file_location("addon.nodes.scene_props", os.path.join(ROOT, "nodes", "scene_props.py"))
scene_props_mod = importlib.util.module_from_spec(spec)
scene_props_mod.bpy = bpy
spec.loader.exec_module(scene_props_mod)
FNSceneProps = scene_props_mod.FNSceneProps

def test_sets_camera_on_scene():
    node = FNSceneProps()
    scene = bpy.data.scenes.new("Scene")
    cam_obj = bpy.data.objects.new("Cam")
    out = node.process(None, {"Scene": scene, "Camera": cam_obj, "Start": 1, "End": 5}, None)
    assert out["Scene"] is scene
    assert scene.camera is cam_obj
