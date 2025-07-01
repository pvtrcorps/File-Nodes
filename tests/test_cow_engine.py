import types
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)


class _FakeID:
    def __init__(self, name):
        self.name = name
    def as_pointer(self):
        return id(self)

class _DataCollection(dict):
    def __init__(self, cls):
        super().__init__()
        self.cls = cls
    def new(self, name):
        obj = self.cls(name)
        self[name] = obj
        return obj
    def remove(self, obj):
        self.pop(obj.name, None)

class _NodeGroups(list):
    pass

def _make_bpy_module():
    bpy = types.ModuleType('bpy')
    bpy.__path__ = []
    class Scene(_FakeID):
        pass
    class Object(_FakeID):
        pass
    class Collection(_FakeID):
        pass
    class World(_FakeID):
        pass
    class Material(_FakeID):
        pass
    class Mesh(_FakeID):
        pass
    class Camera(_FakeID):
        pass
    class Light(_FakeID):
        pass
    class NodeTree(_FakeID):
        pass
    class Image(_FakeID):
        pass
    class Text(_FakeID):
        pass
    class WorkSpace(_FakeID):
        pass
    class UIList(_FakeID):
        pass
    class NodeCustomGroup(_FakeID):
        pass
    class Panel(_FakeID):
        pass

    types_mod = types.ModuleType('bpy.types')
    types_mod.Scene = Scene
    types_mod.Object = Object
    types_mod.Collection = Collection
    types_mod.World = World
    types_mod.Material = Material
    types_mod.Mesh = Mesh
    types_mod.Camera = Camera
    types_mod.Light = Light
    types_mod.NodeTree = NodeTree
    types_mod.Image = Image
    types_mod.Text = Text
    types_mod.WorkSpace = WorkSpace
    types_mod.UIList = UIList
    types_mod.NodeCustomGroup = NodeCustomGroup
    types_mod.Panel = Panel
    types_mod.Operator = type('Operator', (), {})
    types_mod.PropertyGroup = type('PropertyGroup', (), {})
    types_mod.Node = type('Node', (), {})
    types_mod.NodeSocket = type('NodeSocket', (), {})
    bpy.types = types_mod
    sys.modules['bpy.types'] = types_mod
    bpy.data = types.SimpleNamespace(
        scenes=_DataCollection(Scene),
        objects=_DataCollection(Object),
        collections=_DataCollection(Collection),
        worlds=_DataCollection(World),
        materials=_DataCollection(Material),
        meshes=_DataCollection(Mesh),
        cameras=_DataCollection(Camera),
        lights=_DataCollection(Light),
        images=_DataCollection(Image),
        texts=_DataCollection(Text),
        workspaces=_DataCollection(WorkSpace),
        node_groups=_NodeGroups(),
    )
    bpy.props = types.SimpleNamespace(
        BoolProperty=lambda **k: None,
        IntProperty=lambda **k: None,
        FloatProperty=lambda **k: None,
        FloatVectorProperty=lambda **k: None,
        StringProperty=lambda **k: None,
        CollectionProperty=lambda **k: None,
        PointerProperty=lambda **k: None,
        EnumProperty=lambda **k: None,
    )
    bpy.utils = types.SimpleNamespace(register_class=lambda cls: None, unregister_class=lambda cls: None)
    bpy.context = types.SimpleNamespace(scene=None)
    bpy.ops = types.SimpleNamespace()
    return bpy


def _load_cow_engine():
    bpy_mod = _make_bpy_module()
    sys.modules['bpy'] = bpy_mod
    sys.modules['bpy.types'] = bpy_mod.types

    spec_common = importlib.util.spec_from_file_location('addon.common', os.path.join(ROOT, 'common.py'))
    common_mod = importlib.util.module_from_spec(spec_common)
    spec_common.loader.exec_module(common_mod)
    sys.modules['addon.common'] = common_mod

    spec = importlib.util.spec_from_file_location('addon.cow_engine', os.path.join(ROOT, 'cow_engine.py'))
    cow_mod = importlib.util.module_from_spec(spec)
    cow_mod.bpy = bpy_mod
    spec.loader.exec_module(cow_mod)
    sys.modules['addon.cow_engine'] = cow_mod
    return cow_mod

class DummyData:
    def __init__(self, name):
        self.name = name
    def as_pointer(self):
        return id(self)
    def copy(self):
        return DummyData(self.name + '_copy')

def test_wrap_updates_refcount_and_clone_independent():
    cow = _load_cow_engine()
    data = DummyData('orig')
    proxy = cow.DataProxy(data)
    wrapped = cow._wrap(proxy, 2)
    assert wrapped is proxy
    assert proxy.refcount == 2

    first = cow._clone(wrapped)
    second = cow._clone(wrapped)
    assert first is not second
    # first should be a clone of original, second should hold original data
    assert first.data.name == 'orig_copy'
    assert second.data.name == 'orig'

    cow.ensure_mutable(first)
    cow.ensure_mutable(second)
    first.name = 'changed'
    assert second.name == 'orig'

def teardown_module(module):
    for name in ['addon.cow_engine', 'addon.common', 'addon.nodes', 'addon.sockets',
                 'addon.operators', 'addon.tree', 'addon.menu', 'addon.ui', 'addon']:
        sys.modules.pop(name, None)
    sys.modules.pop('bpy', None)
    sys.modules.pop('bpy.types', None)
    sys.modules.pop('nodeitems_utils', None)
