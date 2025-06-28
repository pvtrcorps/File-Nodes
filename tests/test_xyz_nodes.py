import types as pytypes
import sys
import importlib.util
from pathlib import Path
import unittest

# Minimal fake bpy module
_bpy = pytypes.ModuleType('bpy')

class _Props:
    def __getattr__(self, name):
        def _f(*a, **kw):
            return None
        return _f

_bpy.props = _Props()

class _Types:
    class Node: pass
    class Scene: pass
    class Object: pass
    class Collection: pass
    class World: pass
    class Camera: pass
    class Image: pass
    class Light: pass
    class Material: pass
    class Mesh: pass
    class NodeTree: pass
    class Text: pass
    class WorkSpace: pass

_bpy.types = _Types()
_bpy.utils = pytypes.SimpleNamespace(register_class=lambda c: None, unregister_class=lambda c: None)
_bpy.data = pytypes.SimpleNamespace(node_groups=[])
_bpy.__path__ = []

sys.modules['bpy'] = _bpy
sys.modules['bpy.types'] = _bpy.types

# Fake addon package hierarchy
_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
_addon.ADDON_NAME = 'addon'
sys.modules['addon'] = _addon
_nodes_pkg = pytypes.ModuleType('addon.nodes')
_nodes_pkg.__path__ = ['nodes']
sys.modules['addon.nodes'] = _nodes_pkg

# Fake sockets module with required classes
_sockets = pytypes.ModuleType('addon.sockets')
_socket_names = [
    'FNSocketBool', 'FNSocketFloat', 'FNSocketVector', 'FNSocketInt', 'FNSocketString',
    'FNSocketScene', 'FNSocketObject', 'FNSocketCollection', 'FNSocketWorld',
    'FNSocketCamera', 'FNSocketImage', 'FNSocketLight', 'FNSocketMaterial',
    'FNSocketMesh', 'FNSocketNodeTree', 'FNSocketText', 'FNSocketWorkSpace',
]
for name in _socket_names:
    setattr(_sockets, name, type(name, (), {}))
sys.modules['addon.sockets'] = _sockets

# Load the combine_xyz module
spec = importlib.util.spec_from_file_location(
    'addon.nodes.combine_xyz', Path('nodes/combine_xyz.py'),
    submodule_search_locations=['nodes']
)
combine_mod = importlib.util.module_from_spec(spec)
combine_mod.__package__ = 'addon.nodes'
exec(spec.loader.get_code('addon.nodes.combine_xyz'), combine_mod.__dict__)
sys.modules['addon.nodes.combine_xyz'] = combine_mod

# Load the separate_xyz module
spec = importlib.util.spec_from_file_location(
    'addon.nodes.separate_xyz', Path('nodes/separate_xyz.py'),
    submodule_search_locations=['nodes']
)
separate_mod = importlib.util.module_from_spec(spec)
separate_mod.__package__ = 'addon.nodes'
exec(spec.loader.get_code('addon.nodes.separate_xyz'), separate_mod.__dict__)
sys.modules['addon.nodes.separate_xyz'] = separate_mod

FakeList = type('FakeList', (), {'new': lambda self, idname, name: None})


class XYZNodesTest(unittest.TestCase):
    def test_combine_xyz(self):
        cls = combine_mod.FNCombineXYZ
        node = cls.__new__(cls)
        node.inputs = FakeList()
        node.outputs = FakeList()
        node.id_data = None
        node.init(None)
        out = node.process(None, {'X': 1.0, 'Y': 2.0, 'Z': 3.0})
        self.assertEqual(out['Vector'], (1.0, 2.0, 3.0))

    def test_separate_xyz(self):
        cls = separate_mod.FNSeparateXYZ
        node = cls.__new__(cls)
        node.inputs = FakeList()
        node.outputs = FakeList()
        node.id_data = None
        node.init(None)
        out = node.process(None, {'Vector': (4.0, 5.0, 6.0)})
        self.assertEqual(out['X'], 4.0)
        self.assertEqual(out['Y'], 5.0)
        self.assertEqual(out['Z'], 6.0)


if __name__ == '__main__':
    unittest.main()
