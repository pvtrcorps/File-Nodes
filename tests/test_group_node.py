import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

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
    class NodeCustomGroup(Node):
        pass
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
class FNSocketString: pass
sys.modules['addon.sockets'] = _sockets
_sockets.FNSocketString = FNSocketString

# Load required modules
spec_ops = importlib.util.spec_from_file_location('addon.operators', Path('operators.py'))
ops_mod = importlib.util.module_from_spec(spec_ops)
ops_mod.__package__ = 'addon'
exec(spec_ops.loader.get_code('addon.operators'), ops_mod.__dict__)
sys.modules['addon.operators'] = ops_mod

spec_group = importlib.util.spec_from_file_location('addon.nodes.group', Path('nodes/group.py'), submodule_search_locations=['nodes'])
group_mod = importlib.util.module_from_spec(spec_group)
group_mod.__package__ = 'addon.nodes'
exec(spec_group.loader.get_code('addon.nodes.group'), group_mod.__dict__)
sys.modules['addon.nodes.group'] = group_mod


class FakeSocket:
    def __init__(self, name, bl_idname, is_output=False):
        self.name = name
        self.bl_idname = bl_idname
        self.is_output = is_output
        self.links = []
        self.is_linked = False
        self.node = None
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
        sock = FakeSocket(name, bl_idname, is_output=self is getattr(self.node, 'outputs', None))
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
        for s in self:
            if s.name == name:
                return s
        return None

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
    def new_socket(self, name, in_out='INPUT', socket_type='FNSocketString'):
        item = pytypes.SimpleNamespace(name=name, in_out=in_out, socket_type=socket_type)
        self.items_tree.append(item)
        return item

class DummyInputs:
    def __init__(self):
        self.inputs = []
    def sync_inputs(self, tree):
        self.inputs = []
        for item in tree.interface.items_tree:
            if item.in_out == 'INPUT':
                inp = pytypes.SimpleNamespace(name=item.name, socket_type=item.socket_type, value=None)
                inp.prop_name = lambda n=inp: 'value'
                self.inputs.append(inp)
    def get_input_value(self, name):
        for i in self.inputs:
            if i.name == name:
                return i.value
        return None
    def prepare_eval_scene(self, scene):
        pass
    def reset_to_originals(self):
        pass

class NodeGroupInput:
    bl_idname = "NodeGroupInput"

    def __init__(self):
        self.inputs = FakeSocketList(self)
        self.outputs = FakeSocketList(self)

    def init(self, context=None):
        tree = self.id_data
        for item in tree.interface.items_tree:
            if item.in_out == 'INPUT':
                self.outputs.new(item.socket_type, item.name)

    def process(self, context, inputs):
        out = {}
        tree = self.id_data
        for item in tree.interface.items_tree:
            if item.in_out == 'INPUT':
                out[item.name] = tree.fn_inputs.get_input_value(item.name)
        return out


class NodeGroupOutput:
    bl_idname = "NodeGroupOutput"

    def __init__(self):
        self.inputs = FakeSocketList(self)
        self.outputs = FakeSocketList(self)

    def init(self, context=None):
        tree = self.id_data
        for item in tree.interface.items_tree:
            if item.in_out == 'OUTPUT':
                self.inputs.new(item.socket_type, item.name)

    def process(self, context, inputs):
        return {}

class FakeTree:
    bl_idname = 'FileNodesTreeType'
    def __init__(self):
        self.links = FakeLinks()
        self.nodes = []
        self.interface = FakeInterface()
        self.fn_inputs = DummyInputs()

    def contains_tree(self, sub_tree):
        if not sub_tree:
            return False

        visited = set()

        def walk(tree):
            if tree == sub_tree:
                return True
            if tree in visited:
                return False
            visited.add(tree)
            for node in getattr(tree, "nodes", []):
                if getattr(node, "bl_idname", "") == "FNGroupNode":
                    child = getattr(node, "node_tree", None)
                    if child and walk(child):
                        return True
            return False

        return walk(self)


def link_sockets(from_socket, to_socket, tree):
    tree.links.new(from_socket, to_socket)


class GroupInstanceTests(unittest.TestCase):
    def test_basic_instance(self):
        sub_tree = FakeTree()
        sub_tree.interface.new_socket('Value', 'INPUT', 'FNSocketString')
        sub_tree.interface.new_socket('Result', 'OUTPUT', 'FNSocketString')
        sub_tree.fn_inputs.sync_inputs(sub_tree)

        g_in = NodeGroupInput()
        g_in.id_data = sub_tree
        g_in.init(None)

        g_out = NodeGroupOutput()
        g_out.id_data = sub_tree
        g_out.init(None)

        link_sockets(g_in.outputs[0], g_out.inputs[0], sub_tree)
        sub_tree.nodes = [g_in, g_out]

        root_tree = FakeTree()
        node = group_mod.FNGroupNode.__new__(group_mod.FNGroupNode)
        node.id_data = root_tree
        node.inputs = FakeSocketList(node)
        node.outputs = FakeSocketList(node)
        node.node_tree = sub_tree
        node._sync_sockets()

        context = pytypes.SimpleNamespace(scene=None)
        out = node.process(context, {'Value': 'Hello'})
        self.assertEqual(out['Result'], 'Hello')

    def test_recursion_prevention(self):
        tree = FakeTree()
        tree.interface.new_socket('Value', 'INPUT', 'FNSocketString')
        tree.interface.new_socket('Result', 'OUTPUT', 'FNSocketString')
        tree.fn_inputs.sync_inputs(tree)

        g_in = NodeGroupInput()
        g_in.id_data = tree
        g_in.init(None)

        g_out = NodeGroupOutput()
        g_out.id_data = tree
        g_out.init(None)

        link_sockets(g_in.outputs[0], g_out.inputs[0], tree)
        tree.nodes = [g_in, g_out]

        node = group_mod.FNGroupNode.__new__(group_mod.FNGroupNode)
        node.id_data = tree
        node.inputs = FakeSocketList(node)
        node.outputs = FakeSocketList(node)
        node.node_tree = tree  # self-reference
        node._sync_sockets()

        context = pytypes.SimpleNamespace(scene=None)
        out = node.process(context, {'Value': 'Hello'})
        self.assertIsNone(out['Result'])


if __name__ == '__main__':
    unittest.main()
