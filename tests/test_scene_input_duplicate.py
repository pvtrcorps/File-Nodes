import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

# Fake bpy module setup
_bpy = sys.modules.get('bpy', pytypes.ModuleType('bpy'))

class _DummyScene:
    call_count = 0
    def __init__(self, name=""):
        self.name = name
    def copy(self):
        type(self).call_count += 1
        return _DummyScene(self.name)
    def as_pointer(self):
        return id(self)

class _Props:
    def __getattr__(self, name):
        def _f(*a, **kw):
            return None
        return _f

_bpy.types = getattr(_bpy, 'types', pytypes.SimpleNamespace())
class _NodeTree: pass
class _PropertyGroup: pass
class _Operator: pass
class _Node: pass
class _Object: pass
class _Collection: pass
class _World: pass
class _Camera: pass
class _Image: pass
class _Light: pass
class _Material: pass
class _Mesh: pass
class _Text: pass
class _WorkSpace: pass
_bpy.types.NodeTree = _NodeTree
_bpy.types.PropertyGroup = _PropertyGroup
_bpy.types.Operator = _Operator
_bpy.types.Node = _Node
_bpy.types.Object = _Object
_bpy.types.Collection = _Collection
_bpy.types.World = _World
_bpy.types.Camera = _Camera
_bpy.types.Image = _Image
_bpy.types.Light = _Light
_bpy.types.Material = _Material
_bpy.types.Mesh = _Mesh
_bpy.types.Text = _Text
_bpy.types.WorkSpace = _WorkSpace
_bpy.types.Scene = _DummyScene
_bpy.props = getattr(_bpy, 'props', _Props())
_bpy.utils = getattr(_bpy, 'utils', pytypes.SimpleNamespace(register_class=lambda c: None, unregister_class=lambda c: None))
_bpy.data = getattr(_bpy, 'data', pytypes.SimpleNamespace(node_groups=[]))
_bpy.__path__ = getattr(_bpy, '__path__', [])
sys.modules['bpy'] = _bpy
sys.modules['bpy.types'] = _bpy.types

_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
_addon.ADDON_NAME = 'addon'
sys.modules['addon'] = _addon
_nodes_pkg = pytypes.ModuleType('addon.nodes')
_nodes_pkg.__path__ = ['nodes']
sys.modules['addon.nodes'] = _nodes_pkg

_sockets = pytypes.ModuleType('addon.sockets')
_socket_names = [
    'FNSocketBool', 'FNSocketFloat', 'FNSocketInt', 'FNSocketString',
    'FNSocketScene', 'FNSocketObject', 'FNSocketCollection', 'FNSocketWorld',
    'FNSocketCamera', 'FNSocketImage', 'FNSocketLight', 'FNSocketMaterial',
    'FNSocketMesh', 'FNSocketNodeTree', 'FNSocketText', 'FNSocketWorkSpace',
    'FNSocketSceneList', 'FNSocketObjectList', 'FNSocketCollectionList',
    'FNSocketWorldList', 'FNSocketCameraList', 'FNSocketImageList',
    'FNSocketLightList', 'FNSocketMaterialList', 'FNSocketMeshList',
    'FNSocketNodeTreeList', 'FNSocketTextList', 'FNSocketWorkSpaceList'
]
for name in _socket_names:
    setattr(_sockets, name, type(name, (), {}))
sys.modules['addon.sockets'] = _sockets

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
    'addon.nodes.input_nodes', Path('nodes/input_nodes.py'),
    submodule_search_locations=['nodes'],
)
ins = importlib.util.module_from_spec(spec)
ins.__package__ = 'addon.nodes'
exec(spec.loader.get_code('addon.nodes.input_nodes'), ins.__dict__)

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


class SceneInputDuplicateTest(unittest.TestCase):
    def test_scene_copied_once(self):
        tree = tree_mod.FileNodesTree.__new__(tree_mod.FileNodesTree)
        node = ins.FNSceneInputNode.__new__(ins.FNSceneInputNode)
        node.id_data = tree
        node.inputs = [FakeSocket("Name", "FNSocketString")]
        node.outputs = [FakeSocket("Scene", "FNSocketScene", True)]
        for s in node.inputs + node.outputs:
            s.node = node
        node.value = _DummyScene("Base")
        node.inputs[0].value = "Copy"

        out = DummyOutputNode()
        link_sockets(node.outputs[0], out.inputs[0])

        tree.nodes = [node, out]

        ops_mod._evaluate_tree(tree, pytypes.SimpleNamespace())
        ops_mod._evaluate_tree(tree, pytypes.SimpleNamespace())

        self.assertEqual(_DummyScene.call_count, 1)

if __name__ == "__main__":
    unittest.main()
