import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

# Reuse fake bpy setup from other tests
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
    'FNSocketString',
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
input_mod = _load_module('group_input')
output_mod = _load_module('group_output')
group_mod = _load_module('group_node')


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

    def get(self, name):
        idx = self.find(name)
        return self[idx] if idx != -1 else None


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


class FakeInterface:
    def __init__(self):
        self.items_tree = []

    def new_socket(self, name='', in_out='INPUT', socket_type='FNSocketString'):
        item = pytypes.SimpleNamespace(name=name, in_out=in_out, socket_type=socket_type)
        self.items_tree.append(item)
        return item


class FakeTree:
    def __init__(self):
        self.links = FakeLinks()
        self.nodes = []
        self.interface = FakeInterface()
        self.fn_inputs = type('Ctx', (), {'values': {}, 'get_input_value': lambda self, n: self.values.get(n)})()


def build_group_tree():
    tree = FakeTree()
    tree.interface.new_socket('A', 'INPUT', 'FNSocketString')
    tree.interface.new_socket('B', 'INPUT', 'FNSocketString')
    tree.interface.new_socket('Result', 'OUTPUT', 'FNSocketString')

    gi = input_mod.FNGroupInputNode.__new__(input_mod.FNGroupInputNode)
    gi.id_data = tree
    gi.inputs = FakeSocketList(gi)
    gi.outputs = FakeSocketList(gi)
    gi._sync_with_interface()

    js = join_mod.FNJoinStrings.__new__(join_mod.FNJoinStrings)
    js.id_data = tree
    js.inputs = FakeSocketList(js)
    js.outputs = FakeSocketList(js)
    js.separator = ''
    js._update_sockets()

    go = output_mod.FNGroupOutputNode.__new__(output_mod.FNGroupOutputNode)
    go.id_data = tree
    go.inputs = FakeSocketList(go)
    go.outputs = FakeSocketList(go)
    go._sync_with_interface()

    tree.nodes = [gi, js, go]
    tree.links.new(gi.outputs[0], js.inputs[0])
    tree.links.new(gi.outputs[1], js.inputs[0])
    tree.links.new(js.outputs[0], go.inputs[0])

    return tree


class GroupNodeTest(unittest.TestCase):
    def test_group_node_process(self):
        sub_tree = build_group_tree()

        node = group_mod.FNGroupNode.__new__(group_mod.FNGroupNode)
        node.id_data = FakeTree()  # outer tree
        node.node_tree = sub_tree
        node.inputs = FakeSocketList(node)
        node.outputs = FakeSocketList(node)
        node._sync_sockets()

        inputs = {'A': 'Hello', 'B': 'World'}
        out = node.process(None, inputs)
        self.assertEqual(out['Result'], 'HelloWorld')


if __name__ == '__main__':
    unittest.main()
