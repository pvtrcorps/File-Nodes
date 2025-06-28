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
    class NodeTree: pass
    class PropertyGroup: pass
    class Scene: pass
    class Object: pass
    class Collection: pass
    class World: pass
    class Camera: pass
    class Image: pass
    class Light: pass
    class Material: pass
    class Mesh: pass
    class Text: pass
    class WorkSpace: pass

_bpy.types = _Types()
_bpy.utils = pytypes.SimpleNamespace(register_class=lambda c: None, unregister_class=lambda c: None)
_bpy.data = pytypes.SimpleNamespace(node_groups=[])
_bpy.__path__ = []

sys.modules['bpy'] = _bpy
sys.modules['bpy.types'] = _bpy.types

# Fake addon package
_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
_addon.ADDON_NAME = 'addon'
sys.modules['addon'] = _addon

# Fake operators module
_ops = pytypes.ModuleType('addon.operators')
_ops.auto_evaluate_if_enabled = lambda *a, **kw: None
sys.modules['addon.operators'] = _ops

# Fake sockets module with a couple of classes
_sockets = pytypes.ModuleType('addon.sockets')
class FNSocketString: pass
class FNSocketInt: pass
_sockets.FNSocketString = FNSocketString
_sockets.FNSocketInt = FNSocketInt
sys.modules['addon.sockets'] = _sockets

# Load tree module
spec = importlib.util.spec_from_file_location('addon.tree', Path('tree.py'))
tree_mod = importlib.util.module_from_spec(spec)
tree_mod.__package__ = 'addon'
exec(spec.loader.get_code('addon.tree'), tree_mod.__dict__)
sys.modules['addon.tree'] = tree_mod


class TreeUtilsTests(unittest.TestCase):
    def test_get_from_context(self):
        cls = tree_mod.FileNodesTree
        tree = cls.__new__(cls)
        scene = pytypes.SimpleNamespace(file_nodes_tree=tree)
        ctx = pytypes.SimpleNamespace(scene=scene)
        self.assertEqual(cls.get_from_context(ctx), (tree, scene, scene))

        ctx2 = pytypes.SimpleNamespace(scene=pytypes.SimpleNamespace(file_nodes_tree=None))
        self.assertEqual(cls.get_from_context(ctx2), (None, None, None))

    def test_valid_socket_type(self):
        cls = tree_mod.FileNodesTree
        self.assertTrue(cls.valid_socket_type('FNSocketString'))
        self.assertTrue(cls.valid_socket_type('NodeSocketVirtual'))
        self.assertFalse(cls.valid_socket_type('NotASocket'))


if __name__ == '__main__':
    unittest.main()
