import bpy
from bpy.types import PropertyGroup, UIList, Operator
from .tree import FileNodesTree
from .operators import auto_evaluate_if_enabled

class FileNodeModInput(PropertyGroup):
    """Store one exposed input value for a modifier."""

    name: bpy.props.StringProperty()
    socket_type: bpy.props.StringProperty()

    # Primitive values
    bool_value: bpy.props.BoolProperty(update=auto_evaluate_if_enabled)
    int_value: bpy.props.IntProperty(update=auto_evaluate_if_enabled)
    float_value: bpy.props.FloatProperty(update=auto_evaluate_if_enabled)
    string_value: bpy.props.StringProperty(update=auto_evaluate_if_enabled)

    # ID datablock values
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

class FileNodeModItem(PropertyGroup):
    def _update_node_tree(self, context):
        self.sync_inputs()
        auto_evaluate_if_enabled(context)

    # -- Evaluation copies --
    eval_scene = None

    def clear_eval_data(self):
        """Remove the temporary evaluation scene if it exists."""
        if getattr(self, "eval_scene", None):
            try:
                bpy.data.scenes.remove(self.eval_scene)
            except Exception:
                pass
            self.eval_scene = None

    def prepare_eval_scene(self, scene):
        """Duplicate the given scene for evaluation."""
        self.clear_eval_data()
        eval_scene = bpy.data.scenes.new(name=f"{scene.name}_FN_Eval")
        # Copy basic settings that may affect node output
        try:
            eval_scene.unit_settings.system = scene.unit_settings.system
            eval_scene.unit_settings.system_rotation = scene.unit_settings.system_rotation
            eval_scene.unit_settings.scale_length = scene.unit_settings.scale_length
            eval_scene.unit_settings.use_separate = scene.unit_settings.use_separate
        except Exception:
            pass
        try:
            eval_scene.render.engine = scene.render.engine
        except Exception:
            pass
        eval_scene.world = scene.world
        self.eval_scene = eval_scene

    # --- Non destructive storage helpers ---
    def _ensure_storage(self):
        if not hasattr(self, "_original_values"):
            self._original_values = {}
        if "linked_objects" not in self._original_values:
            self._original_values["linked_objects"] = []
        if "linked_collections" not in self._original_values:
            self._original_values["linked_collections"] = []
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

    def reset_to_originals(self):
        self.clear_eval_data()
        storage = getattr(self, "_original_values", None)
        if not storage:
            return
        # Remove dynamically linked objects/collections
        for coll, obj in storage.get("linked_objects", []):
            try:
                c = bpy.data.collections.get(coll.name)
                if c and c.objects.get(obj.name):
                    c.objects.unlink(obj)
            except Exception:
                pass
        for coll, child in storage.get("linked_collections", []):
            try:
                c = bpy.data.collections.get(coll.name)
                if c and c.children.get(child.name):
                    c.children.unlink(child)
            except Exception:
                pass
        for k, v in list(storage.items()):
            if isinstance(k, tuple):
                (ptr, attr) = k
                data, value = v
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
            # remove key entries that hold property values
            for k in list(storage.keys()):
                if isinstance(k, tuple):
                    storage.pop(k)
        self.clear_eval_data()

    node_tree: bpy.props.PointerProperty(
        type=FileNodesTree,
        update=_update_node_tree,
    )
    enabled: bpy.props.BoolProperty(
        name="Enabled",
        default=True,
        update=auto_evaluate_if_enabled,
    )
    name: bpy.props.StringProperty(name="Name", default="")
    stack_index: bpy.props.IntProperty(name="Stack Index", default=0, min=0)
    inputs: bpy.props.CollectionProperty(type=FileNodeModInput)

    def sync_inputs(self):
        """Sync the inputs collection with the node group's interface."""
        tree = self.node_tree
        if not tree:
            self.inputs.clear()
            return
        iface = getattr(tree, "interface", None)
        if not iface:
            self.inputs.clear()
            return
        iface_items = [i for i in iface.items_tree if getattr(i, "in_out", None) == 'INPUT']
        names = [i.name for i in iface_items]
        # remove missing
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

class FileNodesProject(PropertyGroup):
    """Global storage for File Nodes data."""

    modifiers: bpy.props.CollectionProperty(type=FileNodeModItem)


class FILE_NODES_UL_modifiers(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "enabled", text="")
            row.prop(item, "node_tree", text="", icon='NODETREE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "enabled", text="")

class FN_OT_mod_add(Operator):
    bl_idname = "file_nodes.mod_add"
    bl_label = "Add File Node Modifier"

    def execute(self, context):
        mods = bpy.data.file_node_modifiers.modifiers
        item = mods.add()
        tree = bpy.data.node_groups.new("File Nodes", 'FileNodesTreeType')
        tree.use_fake_user = True
        iface = tree.interface
        iface.new_socket(name="Scene", in_out='INPUT', socket_type='FNSocketScene')
        iface.new_socket(name="Scene", in_out='OUTPUT', socket_type='FNSocketScene')
        # Add default Group Input/Output nodes for new trees
        in_node = tree.nodes.new('FNGroupInputNode')
        out_node = tree.nodes.new('FNGroupOutputNode')
        in_node.location = (-200, 0)
        out_node.location = (200, 0)
        in_sock = in_node.outputs.get('Scene')
        out_sock = out_node.inputs.get('Scene')
        if in_sock and out_sock:
            tree.links.new(in_sock, out_sock)
        item.node_tree = tree
        item.name = tree.name
        item.stack_index = len(mods) - 1
        context.scene.file_node_mod_index = len(mods) - 1
        return {'FINISHED'}

class FN_OT_mod_remove(Operator):
    bl_idname = "file_nodes.mod_remove"
    bl_label = "Remove File Node Modifier"

    def execute(self, context):
        mods = bpy.data.file_node_modifiers.modifiers
        idx = context.scene.file_node_mod_index
        if 0 <= idx < len(mods):
            mods[idx].restore_and_clear()
            mods.remove(idx)
            context.scene.file_node_mod_index = max(0, idx-1)
            for i, m in enumerate(mods):
                m.stack_index = i
        return {'FINISHED'}

class FN_OT_mod_move(Operator):
    bl_idname = "file_nodes.mod_move"
    bl_label = "Move File Node Modifier"

    direction: bpy.props.EnumProperty(items=[('UP','Up',''),('DOWN','Down','')])

    def execute(self, context):
        mods = bpy.data.file_node_modifiers.modifiers
        idx = context.scene.file_node_mod_index
        if self.direction == 'UP' and idx > 0:
            mods.move(idx, idx-1)
            context.scene.file_node_mod_index = idx-1
        elif self.direction == 'DOWN' and idx < len(mods)-1:
            mods.move(idx, idx+1)
            context.scene.file_node_mod_index = idx+1
        for i, m in enumerate(mods):
            m.stack_index = i
        return {'FINISHED'}

classes = (
    FileNodeModInput,
    FileNodeModItem,
    FileNodesProject,
    FILE_NODES_UL_modifiers,
    FN_OT_mod_add,
    FN_OT_mod_remove,
    FN_OT_mod_move,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.BlendData.file_node_modifiers = bpy.props.PointerProperty(type=FileNodesProject)
    bpy.types.Scene.file_node_mod_index = bpy.props.IntProperty(default=0)

def unregister():
    del bpy.types.BlendData.file_node_modifiers
    del bpy.types.Scene.file_node_mod_index
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
