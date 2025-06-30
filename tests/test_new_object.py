import sys
import os
import importlib.util
import types

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

# ---- fake bpy ----
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
    def __iter__(self):
        return iter(self.values())


def _make_bpy_module():
    bpy = types.ModuleType("bpy")
    bpy.__path__ = []

    class Object(_FakeID):
        def __init__(self, name, data=None):
            super().__init__(name)
            self.data = data

    class Mesh(_FakeID):
        pass

    class Light(_FakeID):
        pass

    class Camera(_FakeID):
        pass

    types_mod = types.ModuleType("bpy.types")
    types_mod.Object = Object
    types_mod.Mesh = Mesh
    types_mod.Light = Light
    types_mod.Camera = Camera
    types_mod.Node = type("Node", (), {})
    types_mod.NodeSocket = type("NodeSocket", (), {})
    bpy.types = types_mod
    sys.modules["bpy.types"] = types_mod

    bpy.data = types.SimpleNamespace(
        objects=_DataCollection(Object),
        meshes=_DataCollection(Mesh),
        lights=_DataCollection(Light),
        cameras=_DataCollection(Camera),
    )

    bpy.props = types.SimpleNamespace(
        EnumProperty=lambda **k: None,
        StringProperty=lambda **k: None,
        BoolProperty=lambda **k: None,
        PointerProperty=lambda **k: None,
    )
    bpy.utils = types.SimpleNamespace(register_class=lambda cls: None, unregister_class=lambda cls: None)
    bpy.context = types.SimpleNamespace()
    return bpy

bpy = _make_bpy_module()
sys.modules["bpy"] = bpy

# ---- stub modules for relative imports ----
# base module
spec_base = importlib.util.spec_from_file_location("addon.nodes.base", os.path.join(ROOT, "nodes", "base.py"))
base_mod = importlib.util.module_from_spec(spec_base)
base_mod.bpy = bpy
spec_base.loader.exec_module(base_mod)
sys.modules["addon.nodes.base"] = base_mod

# operators stub
ops_mod = types.ModuleType("addon.operators")
ops_mod.auto_evaluate_if_enabled = lambda *a, **k: None
sys.modules["addon.operators"] = ops_mod

# sockets stub
sockets_mod = types.ModuleType("addon.sockets")
for cls in ["FNSocketObject", "FNSocketMesh", "FNSocketLight", "FNSocketCamera", "FNSocketString"]:
    setattr(sockets_mod, cls, type(cls, (), {}))
sys.modules["addon.sockets"] = sockets_mod

# ---- load new_object module ----
spec = importlib.util.spec_from_file_location("addon.nodes.new_object", os.path.join(ROOT, "nodes", "new_object.py"))
new_object = importlib.util.module_from_spec(spec)
spec.loader.exec_module(new_object)
FNNewObject = new_object.FNNewObject

import types as _types

def test_existing_object_updates_data():
    created = []
    ctx = _types.SimpleNamespace(_original_values={}, remember_created_id=lambda x: created.append(x))
    node = FNNewObject()
    node.obj_type = 'MESH'
    node.id_data = _types.SimpleNamespace(fn_inputs=ctx)

    mesh_a = bpy.data.meshes.new('MeshA')
    obj = bpy.data.objects.new('Obj', mesh_a)

    mesh_b = bpy.data.meshes.new('MeshB')
    out = node.process(None, {'Name': 'Obj', 'Data': mesh_b})
    assert out['Object'] is obj
    assert obj.data is mesh_b

    mesh_c = bpy.data.meshes.new('MeshC')
    out2 = node.process(None, {'Name': 'Obj', 'Data': mesh_c})
    assert out2['Object'] is obj
    assert obj.data is mesh_c
