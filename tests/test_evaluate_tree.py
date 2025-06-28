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
    def __init__(self, name, bl_idname):
        self.name = name
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
        scene = bpy.data.scenes.new(name)
        ctx = getattr(self.id_data, "fn_inputs", None)
        if ctx:
            ctx.remember_created_scene(scene)
            ctx.remember_created_id(scene)
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

class FakeInputs:
    def __init__(self, bpy_module):
        self.bpy = bpy_module
        self.scenes_to_keep = []
        self.created_ids = []
        self.eval_scene = None

    def sync_inputs(self, tree):
        pass

    def prepare_eval_scene(self, scene):
        self.eval_scene = scene

    def clear_eval_data(self):
        self.eval_scene = None

    def remember_created_scene(self, scene):
        self.created_ids.append(scene)

    def remember_created_id(self, data):
        self.created_ids.append(data)

    def reset_to_originals(self):
        keep = {id(s) for s in self.scenes_to_keep if s}
        remaining = []
        for data in list(self.created_ids):
            if id(data) in keep:
                remaining.append(data)
                continue
            if isinstance(data, bpy.types.Scene):
                bpy.data.scenes.remove(data)
            elif isinstance(data, bpy.types.Object):
                bpy.data.objects.remove(data)
            elif isinstance(data, bpy.types.Collection):
                bpy.data.collections.remove(data)
            elif isinstance(data, bpy.types.World):
                bpy.data.worlds.remove(data)
            elif isinstance(data, bpy.types.Material):
                bpy.data.materials.remove(data)
            elif isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)
            elif isinstance(data, bpy.types.Light):
                bpy.data.lights.remove(data)
        self.created_ids = remaining

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

# ---- helper to build tree ----
def build_tree():
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
    assert new_scene1 not in list(bpy.data.scenes)
    assert new_scene2 is not new_scene1
