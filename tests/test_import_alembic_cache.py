import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

# Create fake bpy module with minimal API
_bpy = pytypes.ModuleType('bpy')

class _OpsWM:
    call_count = 0

    @staticmethod
    def alembic_import(filepath=""):
        _OpsWM.call_count += 1
        class DummyObj:
            def __init__(self, name):
                self.name = name
                self.data = pytypes.SimpleNamespace()
            def __hash__(self):
                return hash(id(self))
        obj = DummyObj(f"Obj{_OpsWM.call_count}")
        _context.scene.objects.append(obj)

_bpy.ops = pytypes.SimpleNamespace(wm=_OpsWM)

class _Path:
    @staticmethod
    def abspath(path):
        return path

_bpy.path = _Path()

class _Props:
    def __getattr__(self, name):
        def _f(*a, **kw):
            return None
        return _f

_bpy.props = _Props()

class _Types:
    class Node:
        pass
    class NodeTree:
        pass
    class PropertyGroup:
        pass
    class Operator:
        pass
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
_bpy.data = pytypes.SimpleNamespace(node_groups=[], scenes=pytypes.SimpleNamespace())
_bpy.__path__ = []
sys.modules['bpy'] = _bpy
sys.modules['bpy.types'] = _bpy.types

# Fake addon package hierarchy for relative imports
_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
_addon.ADDON_NAME = 'addon'
sys.modules['addon'] = _addon
_nodes_pkg = pytypes.ModuleType('addon.nodes')
_nodes_pkg.__path__ = ['nodes']
sys.modules['addon.nodes'] = _nodes_pkg

_sockets = pytypes.ModuleType('addon.sockets')
class FNSocketObjectList: pass
class FNSocketString: pass
sys.modules['addon.sockets'] = _sockets
_sockets.FNSocketObjectList = FNSocketObjectList
_sockets.FNSocketString = FNSocketString

# Load tree and operators modules using the fake bpy package
spec_tree = importlib.util.spec_from_file_location('addon.tree', Path('tree.py'))
tree_mod = importlib.util.module_from_spec(spec_tree)
tree_mod.__package__ = 'addon'
exec(spec_tree.loader.get_code('addon.tree'), tree_mod.__dict__)
sys.modules['addon.tree'] = tree_mod

spec_ops = importlib.util.spec_from_file_location('addon.operators', Path('operators.py'))
ops_mod = importlib.util.module_from_spec(spec_ops)
ops_mod.__package__ = 'addon'
exec(spec_ops.loader.get_code('addon.operators'), ops_mod.__dict__)
sys.modules['addon.operators'] = ops_mod

# Load node under test
spec = importlib.util.spec_from_file_location(
    'addon.nodes.import_alembic', Path('nodes/import_alembic.py'),
    submodule_search_locations=['nodes']
)
ia = importlib.util.module_from_spec(spec)
ia.__package__ = 'addon.nodes'
exec(spec.loader.get_code('addon.nodes.import_alembic'), ia.__dict__)


# Helpers for fake node tree evaluation
class FakeSocket:
    def __init__(self, name, bl_idname, is_output=False):
        self.name = name
        self.bl_idname = bl_idname
        self.is_output = is_output
        self.links = []
        self.is_linked = False
        self.node = None
        self.value = None


def link_sockets(from_socket, to_socket):
    link = pytypes.SimpleNamespace(from_socket=from_socket, from_node=from_socket.node,
                                   to_socket=to_socket, to_node=to_socket.node)
    to_socket.links.append(link)
    to_socket.is_linked = True


class DummyOutputNode:
    bl_idname = "FNGroupOutputNode"

    def __init__(self):
        self.inputs = [FakeSocket("Objects", "FNSocketObjectList")]
        self.outputs = []
        for s in self.inputs:
            s.node = self

    def process(self, context, inputs):
        return {}


def setup_module(module):
    global _context
    _context = pytypes.SimpleNamespace()
    _context.scene = pytypes.SimpleNamespace(objects=[], collection=[])


class AlembicCacheTest(unittest.TestCase):
    def test_alembic_cached(self):
        tree = tree_mod.FileNodesTree.__new__(tree_mod.FileNodesTree)
        node = ia.FNImportAlembic.__new__(ia.FNImportAlembic)
        node.id_data = tree
        node.inputs = [FakeSocket("File Path", "FNSocketString")]
        node.outputs = [FakeSocket("Objects", "FNSocketObjectList", True)]
        for s in node.inputs + node.outputs:
            s.node = node
        node.inputs[0].value = "some.abc"

        out = DummyOutputNode()
        link_sockets(node.outputs[0], out.inputs[0])

        tree.nodes = [node, out]

        ops_mod._evaluate_tree(tree, _context)
        ops_mod._evaluate_tree(tree, _context)

        self.assertEqual(_OpsWM.call_count, 1)
        self.assertEqual(len(_context.scene.objects), 1)


if __name__ == "__main__":
    unittest.main()
