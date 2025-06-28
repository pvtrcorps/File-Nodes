
import bpy
from bpy.types import NodeTree, PropertyGroup
from .operators import auto_evaluate_if_enabled

class FileNodeTreeInput(PropertyGroup):
    name: bpy.props.StringProperty()
    socket_type: bpy.props.StringProperty()

    bool_value: bpy.props.BoolProperty(update=auto_evaluate_if_enabled)
    int_value: bpy.props.IntProperty(update=auto_evaluate_if_enabled)
    float_value: bpy.props.FloatProperty(update=auto_evaluate_if_enabled)
    string_value: bpy.props.StringProperty(update=auto_evaluate_if_enabled)

    scene_value: bpy.props.PointerProperty(type=bpy.types.Scene, update=auto_evaluate_if_enabled)
    object_value: bpy.props.PointerProperty(type=bpy.types.Object, update=auto_evaluate_if_enabled)
    collection_value: bpy.props.PointerProperty(type=bpy.types.Collection, update=auto_evaluate_if_enabled)
    world_value: bpy.props.PointerProperty(type=bpy.types.World, update=auto_evaluate_if_enabled)
    camera_value: bpy.props.PointerProperty(type=bpy.types.Camera, update=auto_evaluate_if_enabled)
    image_value: bpy.props.PointerProperty(type=bpy.types.Image, update=auto_evaluate_if_enabled)
    light_value: bpy.props.PointerProperty(type=bpy.types.Light, update=auto_evaluate_if_enabled)
    material_value: bpy.props.PointerProperty(type=bpy.types.Material, update=auto_evaluate_if_enabled)
    mesh_value: bpy.props.PointerProperty(type=bpy.types.Mesh, update=auto_evaluate_if_enabled)
    nodetree_value: bpy.props.PointerProperty(type=bpy.types.NodeTree, update=auto_evaluate_if_enabled)
    text_value: bpy.props.PointerProperty(type=bpy.types.Text, update=auto_evaluate_if_enabled)
    workspace_value: bpy.props.PointerProperty(type=bpy.types.WorkSpace, update=auto_evaluate_if_enabled)

    _prop_map = {
        'FNSocketBool': 'bool_value',
        'FNSocketInt': 'int_value',
        'FNSocketFloat': 'float_value',
        'FNSocketString': 'string_value',
        'FNSocketScene': 'scene_value',
        'FNSocketObject': 'object_value',
        'FNSocketCollection': 'collection_value',
        'FNSocketWorld': 'world_value',
        'FNSocketCamera': 'camera_value',
        'FNSocketImage': 'image_value',
        'FNSocketLight': 'light_value',
        'FNSocketMaterial': 'material_value',
        'FNSocketMesh': 'mesh_value',
        'FNSocketNodeTree': 'nodetree_value',
        'FNSocketText': 'text_value',
        'FNSocketWorkSpace': 'workspace_value',
    }

    def prop_name(self):
        return self._prop_map.get(self.socket_type, None)


class FileNodesTreeInputs(PropertyGroup):
    eval_scene = None
    scenes_to_keep = None

    inputs: bpy.props.CollectionProperty(type=FileNodeTreeInput)

    def clear_eval_data(self):
        if getattr(self, "eval_scene", None):
            self.eval_scene = None

    def prepare_eval_scene(self, scene):
        self.clear_eval_data()
        self.eval_scene = scene
        self.scenes_to_keep = []

    def _ensure_storage(self):
        if not hasattr(self, "_original_values"):
            self._original_values = {}
        if "linked_objects" not in self._original_values:
            self._original_values["linked_objects"] = []
        if "linked_collections" not in self._original_values:
            self._original_values["linked_collections"] = []
        if "new_scenes" not in self._original_values:
            self._original_values["new_scenes"] = []
        if "created_ids" not in self._original_values:
            self._original_values["created_ids"] = []
        return self._original_values

    def store_original(self, data, attr):
        storage = self._ensure_storage()
        key = (data.as_pointer(), attr)
        if key not in storage:
            storage[key] = (data, getattr(data, attr))

    def remember_object_link(self, collection, obj):
        self._ensure_storage()["linked_objects"].append((collection, obj))

    def remember_collection_link(self, collection, child):
        self._ensure_storage()["linked_collections"].append((collection, child))

    def remember_created_scene(self, scene):
        self._ensure_storage()["new_scenes"].append(scene)

    def remember_created_id(self, data):
        if data:
            self._ensure_storage()["created_ids"].append(data)

    def _remove_id(self, data):
        try:
            remove_map = {
                bpy.types.Scene: bpy.data.scenes.remove,
                bpy.types.Object: bpy.data.objects.remove,
                bpy.types.Collection: bpy.data.collections.remove,
                bpy.types.World: bpy.data.worlds.remove,
                bpy.types.Material: bpy.data.materials.remove,
                bpy.types.Mesh: bpy.data.meshes.remove,
                bpy.types.Camera: bpy.data.cameras.remove,
                bpy.types.Light: bpy.data.lights.remove,
            }
            fn = remove_map.get(type(data))
            if fn:
                fn(data)
        except Exception:
            pass

    def reset_to_originals(self):
        self.clear_eval_data()
        storage = getattr(self, "_original_values", None)
        if not storage:
            return
        keep_ids = {s.as_pointer() for s in getattr(self, "scenes_to_keep", []) if s}

        new_ids = []
        for id_data in list(storage.get("created_ids", [])):
            if not id_data:
                continue
            try:
                if isinstance(id_data, bpy.types.Scene) and id_data.as_pointer() in keep_ids:
                    new_ids.append(id_data)
                    continue
                self._remove_id(id_data)
            except Exception:
                pass
        storage["created_ids"] = new_ids

        for coll, obj in storage.get("linked_objects", []):
            try:
                if coll.objects.get(obj.name):
                    coll.objects.unlink(obj)
            except Exception:
                pass
        for coll, child in storage.get("linked_collections", []):
            try:
                if coll.children.get(child.name):
                    coll.children.unlink(child)
            except Exception:
                pass
        for k, v in list(storage.items()):
            if isinstance(k, tuple):
                (ptr, attr) = k
                data, value = v
                if isinstance(data, bpy.types.Scene) and data.as_pointer() in keep_ids:
                    continue
                try:
                    setattr(data, attr, value)
                except Exception:
                    pass

    def restore_and_clear(self):
        self.reset_to_originals()
        storage = getattr(self, "_original_values", None)
        if storage:
            storage.get("linked_objects", []).clear()
            storage.get("linked_collections", []).clear()
            storage.get("new_scenes", []).clear()
            storage.get("created_ids", []).clear()
            for k in list(storage.keys()):
                if isinstance(k, tuple):
                    storage.pop(k)
        self.clear_eval_data()
        self.scenes_to_keep = []

    def sync_inputs(self, tree):
        iface = getattr(tree, "interface", None)
        if not iface:
            self.inputs.clear()
            return
        iface_items = [i for i in iface.items_tree if getattr(i, "in_out", None) == 'INPUT']
        names = [i.name for i in iface_items]
        for inp in list(self.inputs):
            if inp.name not in names:
                self.inputs.remove(self.inputs.find(inp.name))
        for item in iface_items:
            inp = self.inputs.get(item.name)
            if inp is None:
                inp = self.inputs.add()
                inp.name = item.name
            inp.socket_type = item.socket_type

    def get_input_value(self, name):
        inp = self.inputs.get(name)
        if not inp:
            return None
        prop = inp.prop_name()
        return getattr(inp, prop) if prop else None

class FileNodesTree(NodeTree):
    bl_idname = "FileNodesTreeType"
    bl_label = "File Nodes"
    bl_icon = 'NODETREE'
    bl_description = "Node tree for managing data across files"
    bl_use_group_interface = True

    fn_enabled: bpy.props.BoolProperty(name='Enabled', default=True)
    fn_inputs: bpy.props.PointerProperty(type=FileNodesTreeInputs)

    def interface_update(self, context):
        if getattr(self, "fn_inputs", None):
            self.fn_inputs.sync_inputs(self)

    # Poll: always available
    @classmethod
    def poll(cls, context):
        return True

    @classmethod
    def get_from_context(cls, context):
        scene = getattr(context, "scene", None)
        tree = getattr(scene, "file_nodes_tree", None) if scene else None
        if tree:
            return tree, scene, scene
        return None, None, None

    @classmethod
    def valid_socket_type(cls, idname):
        """Return True if ``idname`` refers to a valid socket type.

        Blender expects this method to accept builtin socket types in
        addition to those provided by the addon.  The previous
        implementation only allowed sockets defined in ``addon.sockets``
        which caused crashes when the UI queried other socket types,
        e.g. while dragging a link.  The new version falls back to any
        type present in ``bpy.types``.
        """
        if not idname:
            return False
        try:
            from . import sockets
            if hasattr(sockets, idname):
                return True
        except Exception:
            pass
        types_mod = getattr(bpy, "types", None)
        if types_mod and hasattr(types_mod, idname):
            return True
        if idname.startswith("NodeSocket"):
            return True
        return False

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

    def update(self):
        self.interface_update(bpy.context)
        if getattr(self, "fn_inputs", None):
            self.fn_inputs.restore_and_clear()

classes = (
    FileNodeTreeInput,
    FileNodesTreeInputs,
    FileNodesTree,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
