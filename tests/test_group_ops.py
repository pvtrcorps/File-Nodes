import sys
import importlib.util
import unittest
from pathlib import Path
import types as pytypes

# Fake bpy module
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
    class NodeCustomGroup: pass
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

_sockets = pytypes.ModuleType('addon.sockets')
for name in ['FNSocketString']:
    setattr(_sockets, name, type(name, (), {}))
sys.modules['addon.sockets'] = _sockets

# Load modules

def _load_node(name):
    spec = importlib.util.spec_from_file_location(f'addon.nodes.{name}', Path(f'nodes/{name}.py'), submodule_search_locations=['nodes'])
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = 'addon.nodes'
    exec(spec.loader.get_code(f'addon.nodes.{name}'), mod.__dict__)
    sys.modules[f'addon.nodes.{name}'] = mod
    return mod

group_out_mod = _load_node('group_output')
group_mod = _load_node('group_node')

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


class FakeSocket:
    def __init__(self, name, bl_idname, is_output=False):
        self.name = name
        self.bl_idname = bl_idname
        self.node = None
        self.links = []
        self.is_linked = False
        self.value = None
        self.is_output = is_output

    @property
    def link_limit(self):
        return 1


class FakeSocketList(list):
    def __init__(self, node):
        super().__init__()
        self.node = node

    def new(self, bl_idname, name):
        sock = FakeSocket(name, bl_idname, is_output=False)
        sock.node = self.node
        self.append(sock)
        return sock

    def remove(self, sock):
        if sock in self:
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
        self.nodes = []


class DummyInputNode:
    bl_idname = "DummyInput"

    def __init__(self, tree):
        self.id_data = tree
        self.inputs = FakeSocketList(self)
        self.outputs = FakeSocketList(self)
        self.outputs.new('FNSocketString', 'String')


class DummyProcessNode:
    bl_idname = "DummyProcess"

    def __init__(self, tree):
        self.id_data = tree
        self.inputs = FakeSocketList(self)
        self.outputs = FakeSocketList(self)
        self.inputs.new('FNSocketString', 'In')
        self.outputs.new('FNSocketString', 'Out')


class GroupOpsTest(unittest.TestCase):

    def test_group_make_and_ungroup(self):
        tree = FakeTree()
        inp = DummyInputNode(tree)
        join = DummyProcessNode(tree)
        out = group_out_mod.FNGroupOutputNode.__new__(group_out_mod.FNGroupOutputNode)
        out.id_data = tree
        out.inputs = FakeSocketList(out)
        out.outputs = FakeSocketList(out)
        out.init(None)

        tree.nodes.extend([inp, join, out])

        tree.links.new(inp.outputs[0], join.inputs[0])
        tree.links.new(join.outputs[0], out.inputs[0])

        join.select = True

        context = pytypes.SimpleNamespace(space_data=pytypes.SimpleNamespace(edit_tree=tree))
        op = ops_mod.FN_OT_group_make.__new__(ops_mod.FN_OT_group_make)
        op.execute(context)

        group_node = [n for n in tree.nodes if isinstance(n, group_mod.FNGroupNode)][0]
        self.assertEqual(len(tree.nodes), 3)
        self.assertIs(group_node.node_tree.nodes[-1], join)
        self.assertEqual(group_node.inputs[0].name, join.inputs[0].name)
        self.assertEqual(group_node.outputs[0].name, join.outputs[0].name)
        self.assertEqual(tree.links[0].to_node, group_node)
        self.assertEqual(tree.links[1].from_node, group_node)

        group_node.select = True
        opu = ops_mod.FN_OT_group_ungroup.__new__(ops_mod.FN_OT_group_ungroup)
        opu.execute(context)

        self.assertEqual(len(tree.nodes), 3)
        self.assertIn(join, tree.nodes)
        self.assertEqual(tree.links[0].to_node, join)
        self.assertEqual(tree.links[1].from_node, join)


if __name__ == '__main__':
    unittest.main()
