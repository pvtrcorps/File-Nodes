import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

_bpy = sys.modules.get('bpy', pytypes.ModuleType('bpy'))

class _Scenes:
    call_count = 0
    def new(self, name=""):
        self.__class__.call_count += 1
        return pytypes.SimpleNamespace(name=f"{name}")

if not hasattr(_bpy, 'data'):
    _bpy.data = pytypes.SimpleNamespace(node_groups=[], scenes=_Scenes())
else:
    _bpy.data.node_groups = []
    _bpy.data.scenes = _Scenes()

class _Props:
    def __getattr__(self, name):
        def _f(*a, **kw):
            return None
        return _f

_bpy.props = getattr(_bpy, 'props', _Props())

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

_bpy.types = getattr(_bpy, 'types', _Types())
_bpy.utils = getattr(_bpy, 'utils', pytypes.SimpleNamespace(register_class=lambda c: None, unregister_class=lambda c: None))
_bpy.__path__ = getattr(_bpy, '__path__', [])
sys.modules['bpy.types'] = _bpy.types
sys.modules['bpy'] = _bpy

_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
_addon.ADDON_NAME = 'addon'
sys.modules['addon'] = _addon
_nodes_pkg = pytypes.ModuleType('addon.nodes')
_nodes_pkg.__path__ = ['nodes']
sys.modules['addon.nodes'] = _nodes_pkg

_sockets = sys.modules.get('addon.sockets')
if not _sockets:
    _sockets = pytypes.ModuleType('addon.sockets')
    sys.modules['addon.sockets'] = _sockets
class FNSocketScene: pass
class FNSocketString: pass
_sockets.FNSocketScene = FNSocketScene
_sockets.FNSocketString = FNSocketString

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

spec = importlib.util.spec_from_file_location(
    'addon.nodes.new_scene', Path('nodes/new_scene.py'),
    submodule_search_locations=['nodes']
)
ns = importlib.util.module_from_spec(spec)
ns.__package__ = 'addon.nodes'
exec(spec.loader.get_code('addon.nodes.new_scene'), ns.__dict__)

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
        self.inputs = [FakeSocket("Scene", "FNSocketScene")]
        self.outputs = []
        for s in self.inputs:
            s.node = self

    def process(self, context, inputs):
        return {}


def setup_module(module):
    global _context
    _context = pytypes.SimpleNamespace()


class NewSceneCacheTest(unittest.TestCase):
    def test_scene_cached(self):
        tree = tree_mod.FileNodesTree.__new__(tree_mod.FileNodesTree)
        node = ns.FNNewScene.__new__(ns.FNNewScene)
        node.id_data = tree
        node.inputs = [FakeSocket("Name", "FNSocketString")]
        node.outputs = [FakeSocket("Scene", "FNSocketScene", True)]
        for s in node.inputs + node.outputs:
            s.node = node
        node.inputs[0].value = "Scene"

        out = DummyOutputNode()
        link_sockets(node.outputs[0], out.inputs[0])

        tree.nodes = [node, out]

        ops_mod._evaluate_tree(tree, _context)
        ops_mod._evaluate_tree(tree, _context)

        self.assertEqual(_bpy.data.scenes.call_count, 1)


if __name__ == "__main__":
    unittest.main()
