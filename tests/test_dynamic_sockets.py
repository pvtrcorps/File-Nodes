import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

# Fake minimal bpy module
_bpy = pytypes.ModuleType('bpy')

class _Props:
    def __getattr__(self, name):
        def _f(*a, **kw):
            return None
        return _f
_bpy.props = _Props()

class _Types:
    class Node: pass
    class NodeTree: pass
    class PropertyGroup: pass
    class Operator: pass
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

# Fake addon package hierarchy
_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
_addon.ADDON_NAME = 'addon'
sys.modules['addon'] = _addon
_nodes_pkg = pytypes.ModuleType('addon.nodes')
_nodes_pkg.__path__ = ['nodes']
sys.modules['addon.nodes'] = _nodes_pkg

# Fake sockets
_sockets = pytypes.ModuleType('addon.sockets')
_socket_names = [
    'FNSocketScene', 'FNSocketObject', 'FNSocketCollection', 'FNSocketWorld',
    'FNSocketCamera', 'FNSocketImage', 'FNSocketLight', 'FNSocketMaterial',
    'FNSocketMesh', 'FNSocketNodeTree', 'FNSocketText', 'FNSocketWorkSpace',
    'FNSocketSceneList', 'FNSocketObjectList', 'FNSocketCollectionList',
    'FNSocketWorldList', 'FNSocketCameraList', 'FNSocketImageList',
    'FNSocketLightList', 'FNSocketMaterialList', 'FNSocketMeshList',
    'FNSocketNodeTreeList', 'FNSocketTextList', 'FNSocketWorkSpaceList',
    'FNSocketString'
]
for name in _socket_names:
    setattr(_sockets, name, type(name, (), {}))
sys.modules['addon.sockets'] = _sockets


def _load_module(name):
    spec = importlib.util.spec_from_file_location(
        f'addon.nodes.{name}', Path(f'nodes/{name}.py'),
        submodule_search_locations=['nodes']
    )
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = 'addon.nodes'
    exec(spec.loader.get_code(f'addon.nodes.{name}'), mod.__dict__)
    sys.modules[f'addon.nodes.{name}'] = mod
    return mod

join_mod = _load_module('join_strings')
create_mod = _load_module('create_list')


class FakeSocket:
    def __init__(self, name, bl_idname):
        self.name = name
        self.bl_idname = bl_idname
        self.node = None
        self.links = []
        self.is_linked = False
        self.value = None
        self.link_limit = 1
        self.display_shape = 'CIRCLE'

    @property
    def is_multi_input(self):
        return self.link_limit != 1


class FakeSocketList(list):
    def __init__(self, node):
        super().__init__()
        self.node = node

    def new(self, bl_idname, name):
        sock = FakeSocket(name, bl_idname)
        sock.node = self.node
        self.append(sock)
        return sock

    def remove(self, sock):
        list.remove(self, sock)

    def move(self, from_index, to_index):
        sock = self.pop(from_index)
        self.insert(to_index, sock)

    def find(self, name):
        for i, s in enumerate(self):
            if s.name == name:
                return i
        return -1


class FakeLink:
    def __init__(self, from_socket, to_socket):
        self.from_socket = from_socket
        self.to_socket = to_socket
        self.from_node = from_socket.node
        self.to_node = to_socket.node


class FakeLinks(list):
    def new(self, from_socket, to_socket):
        link = FakeLink(from_socket, to_socket)
        list.append(self, link)
        from_socket.links.append(link)
        to_socket.links.append(link)
        to_socket.is_linked = True
        return link

    def remove(self, link):
        if link in self:
            list.remove(self, link)
        if link in link.from_socket.links:
            link.from_socket.links.remove(link)
        if link in link.to_socket.links:
            link.to_socket.links.remove(link)
            link.to_socket.is_linked = bool(link.to_socket.links)


class FakeTree:
    def __init__(self):
        self.links = FakeLinks()


class DynamicSocketTests(unittest.TestCase):
    def _setup_node(self, cls):
        tree = FakeTree()
        node = cls.__new__(cls)
        node.id_data = tree
        node.inputs = FakeSocketList(node)
        node.outputs = FakeSocketList(node)
        if hasattr(cls, 'data_type'):
            object.__setattr__(node, 'data_type', 'WORLD')
        if hasattr(cls, 'separator'):
            object.__setattr__(node, 'separator', '')
        node._update_sockets()
        if hasattr(cls, 'separator'):
            object.__setattr__(node, 'separator', '')
        return node, tree

    def test_join_strings_multi_input(self):
        node, _ = self._setup_node(join_mod.FNJoinStrings)
        self.assertEqual(len(node.inputs), 1)
        sock = node.inputs[0]
        self.assertEqual(sock.link_limit, 0)
        self.assertEqual(sock.display_shape, 'CIRCLE_DOT')

        node.separator = ''
        result = node.process(None, {"String": ["A", "B", "C"]})
        self.assertEqual(result["String"], "ABC")


if __name__ == '__main__':
    unittest.main()
