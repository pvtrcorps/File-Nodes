import sys
import os
import importlib
import importlib.util
import types

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
PKG_NAME = "addon"
spec = importlib.util.spec_from_file_location(PKG_NAME, os.path.join(ROOT, "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
sys.modules[PKG_NAME] = pkg
spec.loader.exec_module(pkg)

# ---- Fake bpy setup ----
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

    def __iter__(self):
        return iter(self.values())

class _NodeGroups(list):
    pass

def _make_bpy_module():
    bpy = types.ModuleType("bpy")
    bpy.__path__ = []  # treat as package
    # Datablock types
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

    types_mod = types.ModuleType("bpy.types")
    types_mod.Scene = Scene
    types_mod.Object = Object
    types_mod.Collection = Collection
    types_mod.World = World
    types_mod.Material = Material
    types_mod.Mesh = Mesh
    types_mod.Camera = Camera
    types_mod.Light = Light
    types_mod.NodeTree = NodeTree
    types_mod.Operator = type("Operator", (), {})
    types_mod.PropertyGroup = type("PropertyGroup", (), {})
    types_mod.Node = type("Node", (), {})
    types_mod.NodeSocket = type("NodeSocket", (), {})
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
    bpy.ops = types.SimpleNamespace(render=types.SimpleNamespace(render=lambda *a, **kw: None))
    return bpy
# ---- Fake node system ----
class FakeSocket:
    def __init__(self, name, bl_idname, identifier=None):
        self.name = name
        self.identifier = identifier or name.replace(" ", "_")
        self.bl_idname = bl_idname
        self.is_linked = False
        self.links = []
        self.is_multi_input = False
        self.value = None
        self.node = None

class FakeLink:
    def __init__(self, from_node, from_socket):
        self.from_node = from_node
        self.from_socket = from_socket

class FakeNode:
    def __init__(self, bl_idname):
        self.bl_idname = bl_idname
        self.inputs = []
        self.outputs = []
        self.id_data = None

    def process(self, context, inputs):
        return {}

class NewSceneNode(FakeNode):
    def __init__(self):
        super().__init__("FNNewScene")
        name_sock = FakeSocket("Name", "FNSocketString")
        name_sock.value = "Scene"
        out_sock = FakeSocket("Scene", "FNSocketScene")
        self.inputs.append(name_sock)
        self.outputs.append(out_sock)

    def process(self, context, inputs):
        name = inputs.get("Name") or "Scene"
        cached = bpy.data.scenes.get(name)
        if cached is None:
            cached = bpy.data.scenes.new(name)
        return {"Scene": cached}


class CachedNewSceneNode(NewSceneNode):
    """NewSceneNode variant that reuses scenes from previous evaluation."""

    def __init__(self):
        super().__init__()
        self._cache = {}

    def process(self, context, inputs):
        name = inputs.get("Name") or "Scene"
        cached = self._cache.get(name)
        if cached is not None:
            self._cache[name] = cached
            return {"Scene": cached}
        scene = bpy.data.scenes.new(name)
        self._cache[name] = scene
        return {"Scene": scene}

class OutputScenesNode(FakeNode):
    def __init__(self):
        super().__init__("FNOutputScenesNode")
        inp = FakeSocket("Scenes", "FNSocketSceneList")
        self.inputs.append(inp)

    def process(self, context, inputs):
        scenes = inputs.get("Scenes") or []
        ctx = getattr(self.id_data, "fn_inputs", None)
        if ctx:
            ctx.scenes_to_keep.extend([s for s in (scenes if isinstance(scenes, list) else [scenes]) if s])
        return {}

class OutlinerNode(FakeNode):
    def __init__(self):
        super().__init__("FNOutlinerNode")
        inp = FakeSocket("Scene", "FNSocketScene")
        self.inputs.append(inp)

    def process(self, context, inputs):
        return {}

class PassThroughNode(FakeNode):
    def __init__(self, name="Pass"):
        super().__init__("FNPass")
        inp = FakeSocket("In", "FNSocketScene")
        out = FakeSocket("Out", "FNSocketScene")
        self.inputs.append(inp)
        self.outputs.append(out)

    def process(self, context, inputs):
        return {"Out": inputs.get("In")}


class SetSceneNameNode(FakeNode):
    def __init__(self):
        super().__init__("FNSetSceneName")
        self.inputs.append(FakeSocket("Scene", "FNSocketScene"))
        name_sock = FakeSocket("Name", "FNSocketString")
        name_sock.value = ""
        self.inputs.append(name_sock)
        self.outputs.append(FakeSocket("Scene", "FNSocketScene"))

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            name = inputs.get("Name") or ""
            scene = cow_mod.ensure_mutable(scene)
            scene.name = name
        return {"Scene": scene}

class FakeInputs:
    def __init__(self, bpy_module):
        self.bpy = bpy_module
        self.eval_scene = None
        self.scenes_to_keep = []
        self.values = {}

    def sync_inputs(self, tree):
        pass

    def prepare_eval_scene(self, scene):
        self.eval_scene = scene

    def clear_eval_data(self):
        self.eval_scene = None

    def get_input_value(self, name):
        return self.values.get(name)

class FakeNodeTree:
    bl_idname = "FileNodesTreeType"

    def __init__(self):
        self.nodes = []
        self.links = []
        self.fn_enabled = True
        self.fn_inputs = FakeInputs(bpy)

# ---- setup module and operators ----
bpy = _make_bpy_module()
sys.modules['bpy'] = bpy
operators = importlib.import_module(f'{PKG_NAME}.operators')
cow_mod = importlib.import_module(f'{PKG_NAME}.cow_engine')

# ---- helper to build tree ----
def build_tree():
    bpy.data.node_groups.clear()
    bpy.data.scenes.clear()
    tree = FakeNodeTree()
    new_node = NewSceneNode()
    out_node = OutputScenesNode()
    # link
    new_node.outputs[0].node = new_node
    link = FakeLink(new_node, new_node.outputs[0])
    out_node.inputs[0].is_linked = True
    out_node.inputs[0].links.append(link)
    # id_data
    new_node.id_data = tree
    out_node.id_data = tree
    tree.nodes.extend([new_node, out_node])
    bpy.data.node_groups.append(tree)
    return tree

def build_outliner_tree():
    bpy.data.node_groups.clear()
    bpy.data.scenes.clear()
    tree = FakeNodeTree()
    new_node = NewSceneNode()
    out_node = OutlinerNode()
    new_node.outputs[0].node = new_node
    link = FakeLink(new_node, new_node.outputs[0])
    out_node.inputs[0].is_linked = True
    out_node.inputs[0].links.append(link)
    new_node.id_data = tree
    out_node.id_data = tree
    tree.nodes.extend([new_node, out_node])
    bpy.data.node_groups.append(tree)
    return tree

def build_cycle_tree():
    bpy.data.node_groups.clear()
    bpy.data.scenes.clear()
    tree = FakeNodeTree()
    n1 = PassThroughNode()
    n2 = PassThroughNode()
    out_node = OutputScenesNode()

    # create links forming a cycle n1 -> n2 -> n1
    n1.outputs[0].node = n1
    n2.outputs[0].node = n2

    link_n2_to_n1 = FakeLink(n2, n2.outputs[0])
    n1.inputs[0].is_linked = True
    n1.inputs[0].links.append(link_n2_to_n1)

    link_n1_to_n2 = FakeLink(n1, n1.outputs[0])
    n2.inputs[0].is_linked = True
    n2.inputs[0].links.append(link_n1_to_n2)

    # connect n1 to output
    link_out = FakeLink(n1, n1.outputs[0])
    out_node.inputs[0].is_linked = True
    out_node.inputs[0].links.append(link_out)

    for n in (n1, n2, out_node):
        n.id_data = tree
    tree.nodes.extend([n1, n2, out_node])
    bpy.data.node_groups.append(tree)
    return tree

def build_group_output_tree(single=True):
    bpy.data.node_groups.clear()
    bpy.data.scenes.clear()
    tree = FakeNodeTree()
    new_node = NewSceneNode()
    out_node = FakeNode("NodeGroupOutput")
    sock_type = "FNSocketScene" if single else "FNSocketSceneList"
    in_sock = FakeSocket("Scene", sock_type)
    in_sock.is_linked = True
    link = FakeLink(new_node, new_node.outputs[0])
    in_sock.links.append(link)
    out_node.inputs.append(in_sock)
    new_node.outputs[0].node = new_node
    for n in (new_node, out_node):
        n.id_data = tree
    tree.nodes.extend([new_node, out_node])
    bpy.data.node_groups.append(tree)
    return tree, new_node

def build_group_output_tree_cached(single=True):
    bpy.data.node_groups.clear()
    bpy.data.scenes.clear()
    tree = FakeNodeTree()
    new_node = CachedNewSceneNode()
    out_node = FakeNode("NodeGroupOutput")
    sock_type = "FNSocketScene" if single else "FNSocketSceneList"
    in_sock = FakeSocket("Scene", sock_type)
    in_sock.is_linked = True
    link = FakeLink(new_node, new_node.outputs[0])
    in_sock.links.append(link)
    out_node.inputs.append(in_sock)
    new_node.outputs[0].node = new_node
    for n in (new_node, out_node):
        n.id_data = tree
    tree.nodes.extend([new_node, out_node])
    bpy.data.node_groups.append(tree)
    return tree, new_node

def build_split_rename_tree():
    bpy.data.node_groups.clear()
    bpy.data.scenes.clear()
    tree = FakeNodeTree()
    new_node = NewSceneNode()
    set_a = SetSceneNameNode()
    set_b = SetSceneNameNode()
    out_node = OutputScenesNode()

    new_node.outputs[0].node = new_node
    link_a = FakeLink(new_node, new_node.outputs[0])
    link_b = FakeLink(new_node, new_node.outputs[0])
    set_a.inputs[0].is_linked = True
    set_a.inputs[0].links.append(link_a)
    set_b.inputs[0].is_linked = True
    set_b.inputs[0].links.append(link_b)

    set_a.outputs[0].node = set_a
    set_b.outputs[0].node = set_b
    out_node.inputs[0].is_linked = True
    out_node.inputs[0].is_multi_input = True
    out_node.inputs[0].links.append(FakeLink(set_a, set_a.outputs[0]))
    out_node.inputs[0].links.append(FakeLink(set_b, set_b.outputs[0]))

    for n in (new_node, set_a, set_b, out_node):
        n.id_data = tree

    tree.nodes.extend([new_node, set_a, set_b, out_node])
    bpy.data.node_groups.append(tree)
    return tree, set_a, set_b

def build_rename_chain_tree():
    bpy.data.node_groups.clear()
    bpy.data.scenes.clear()
    tree = FakeNodeTree()

    new_node = NewSceneNode()
    set_a = SetSceneNameNode()
    set_b = SetSceneNameNode()
    set_c = SetSceneNameNode()
    out_node = FakeNode("NodeGroupOutput")

    # chain connections
    new_node.outputs[0].node = new_node
    link_a = FakeLink(new_node, new_node.outputs[0])
    set_a.inputs[0].is_linked = True
    set_a.inputs[0].links.append(link_a)

    set_a.outputs[0].node = set_a
    link_b = FakeLink(set_a, set_a.outputs[0])
    set_b.inputs[0].is_linked = True
    set_b.inputs[0].links.append(link_b)

    set_b.outputs[0].node = set_b
    link_c = FakeLink(set_b, set_b.outputs[0])
    set_c.inputs[0].is_linked = True
    set_c.inputs[0].links.append(link_c)

    set_c.outputs[0].node = set_c
    in_sock = FakeSocket("Scene", "FNSocketScene")
    in_sock.is_linked = True
    in_sock.links.append(FakeLink(set_c, set_c.outputs[0]))
    out_node.inputs.append(in_sock)

    for n in (new_node, set_a, set_b, set_c, out_node):
        n.id_data = tree

    tree.nodes.extend([new_node, set_a, set_b, set_c, out_node])
    bpy.data.node_groups.append(tree)
    return tree, set_a, set_b, set_c

# ---- Tests ----
def test_evaluate_tree_creates_and_cleans():
    tree = build_tree()
    original = bpy.data.scenes.new('Original')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    count1 = operators.evaluate_tree(ctx)
    assert count1 == 1
    assert len(list(bpy.data.scenes)) == 2
    new_scene1 = [s for s in bpy.data.scenes if s is not original][0]

    count2 = operators.evaluate_tree(ctx)
    assert count2 == 1
    assert len(list(bpy.data.scenes)) == 2
    new_scene2 = [s for s in bpy.data.scenes if s is not original][0]
    assert new_scene2 is new_scene1

def test_outliner_forces_evaluation():
    tree = build_outliner_tree()
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    count = operators.evaluate_tree(ctx)
    assert count == 1
    assert len(list(bpy.data.scenes)) == 2

def test_cycle_does_not_recursively_fail():
    tree = build_cycle_tree()
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    count = operators.evaluate_tree(ctx)
    assert count == 1
    # no new scenes should be created because the cycle produces None
    assert len(list(bpy.data.scenes)) == 1


def test_reuse_scene_with_group_output():
    tree, new_node = build_group_output_tree_cached(single=True)
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    new_node.inputs[0].value = 'Persist'
    operators.evaluate_tree(ctx)
    first_scene = [s for s in bpy.data.scenes if s is not original][0]

    operators.evaluate_tree(ctx)
    assert len(list(bpy.data.scenes)) == 2
    second_scene = [s for s in bpy.data.scenes if s is not original][0]
    assert first_scene is second_scene


def test_handles_socket_identifier():
    bpy.data.node_groups.clear()
    tree = FakeNodeTree()

    inp_node = FakeNode("NodeGroupInput")
    out_sock = FakeSocket("View Layer", "FNSocketViewLayer", identifier="View_Layer")
    out_sock.node = inp_node
    inp_node.outputs.append(out_sock)

    consume = FakeNode("Consumer")
    in_sock = FakeSocket("View Layer", "FNSocketViewLayer", identifier="View_Layer")
    in_sock.is_linked = True
    link = FakeLink(inp_node, out_sock)
    in_sock.links.append(link)
    consume.inputs.append(in_sock)

    for n in (inp_node, consume):
        n.id_data = tree

    tree.nodes.extend([inp_node, consume])
    tree.fn_inputs.values["View Layer"] = "Dummy"
    bpy.data.node_groups.append(tree)

    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    count = operators.evaluate_tree(ctx)
    assert count == 1


def test_keep_scenes_from_group_output_single():
    tree, new_node = build_group_output_tree(single=True)
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    new_node.inputs[0].value = 'First'
    operators.evaluate_tree(ctx)
    first_scene = [s for s in bpy.data.scenes if s.name == 'First'][0]

    new_node.inputs[0].value = 'Second'
    operators.evaluate_tree(ctx)
    names = {s.name for s in bpy.data.scenes}
    assert {'Orig', 'First', 'Second'} == names
    assert first_scene in list(bpy.data.scenes)


def test_keep_scenes_from_group_output_list():
    tree, new_node = build_group_output_tree(single=False)
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    new_node.inputs[0].value = 'First'
    operators.evaluate_tree(ctx)
    first_scene = [s for s in bpy.data.scenes if s.name == 'First'][0]

    new_node.inputs[0].value = 'Second'
    operators.evaluate_tree(ctx)
    names = {s.name for s in bpy.data.scenes}
    assert {'Orig', 'First', 'Second'} == names
    assert first_scene in list(bpy.data.scenes)


def test_group_output_reuses_same_scene_name():
    tree, _ = build_group_output_tree(single=True)
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    operators.evaluate_tree(ctx)
    first_scene = [s for s in bpy.data.scenes if s is not original][0]

    operators.evaluate_tree(ctx)
    assert len(list(bpy.data.scenes)) == 2
    second_scene = [s for s in bpy.data.scenes if s is not original][0]
    assert second_scene is first_scene


def test_split_scene_renames_are_independent():
    tree, set_a, set_b = build_split_rename_tree()
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    set_a.inputs[1].value = 'A'
    set_b.inputs[1].value = 'B'

    operators.evaluate_tree(ctx)
    names = {sc.name for sc in tree.fn_inputs.scenes_to_keep}
    assert {'A', 'B'} == names


def test_cleanup_intermediate_scene_names():
    tree, set_a, set_b, set_c = build_rename_chain_tree()
    original = bpy.data.scenes.new('Orig')
    bpy.context.scene = original
    ctx = types.SimpleNamespace(scene=original)

    set_a.inputs[1].value = 'A'
    set_b.inputs[1].value = 'B'
    set_c.inputs[1].value = 'C'

    for _ in range(3):
        operators.evaluate_tree(ctx)

    names = {sc.name for sc in bpy.data.scenes}
    assert names == {'Orig', 'C'}

