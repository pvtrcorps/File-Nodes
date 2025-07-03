import bpy
from bpy.types import NodeTree, PropertyGroup
from .operators import auto_evaluate_if_enabled

class FileNodeTreeInput(PropertyGroup):
    name: bpy.props.StringProperty()
    socket_type: bpy.props.StringProperty()

    bool_value: bpy.props.BoolProperty(update=auto_evaluate_if_enabled)
    exec_value: bpy.props.BoolProperty(update=auto_evaluate_if_enabled)
    int_value: bpy.props.IntProperty(update=auto_evaluate_if_enabled)
    float_value: bpy.props.FloatProperty(update=auto_evaluate_if_enabled)
    vector_value: bpy.props.FloatVectorProperty(size=3, update=auto_evaluate_if_enabled)
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
    # Using PointerProperty with ViewLayer is not supported in Blender 4.4,
    # store the view layer name instead.
    viewlayer_value: bpy.props.StringProperty(update=auto_evaluate_if_enabled)

    _prop_map = {
        'FNSocketBool': 'bool_value',
        'FNSocketExec': 'exec_value',
        'FNSocketInt': 'int_value',
        'FNSocketFloat': 'float_value',
        'FNSocketVector': 'vector_value',
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
        'FNSocketViewLayer': 'viewlayer_value',
    }

    def prop_name(self):
        return self._prop_map.get(self.socket_type, None)


class FNSceneReference(PropertyGroup):
    scene: bpy.props.PointerProperty(type=bpy.types.Scene)


class FileNodesTreeInputs(PropertyGroup):
    eval_scene = None
    # Change scenes_to_keep to a CollectionProperty
    scenes_to_keep: bpy.props.CollectionProperty(type=FNSceneReference)

    inputs: bpy.props.CollectionProperty(type=FileNodeTreeInput)

    def clear_eval_data(self):
        if getattr(self, "eval_scene", None):
            self.eval_scene = None
        # Clear the collection instead of setting to None
        self.scenes_to_keep.clear()

    def prepare_eval_scene(self, scene):
        self.clear_eval_data()
        self.eval_scene = scene


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

class FNStateMapItem(PropertyGroup):
    name: bpy.props.StringProperty()
    datablock_uuid: bpy.props.StringProperty()

class FileNodesTree(NodeTree):
    bl_idname = "FileNodesTreeType"
    bl_label = "File Nodes"
    bl_icon = 'NODETREE'
    bl_use_group_interface = True

    fn_enabled: bpy.props.BoolProperty(name='Enabled', default=True)
    fn_inputs: bpy.props.PointerProperty(type=FileNodesTreeInputs)
    fn_state_map: bpy.props.CollectionProperty(type=FNStateMapItem)

    def get_datablock_uuid(self, node_key):
        item = self.fn_state_map.get(node_key)
        return item.datablock_uuid if item else None

    def set_datablock_uuid(self, node_key, datablock_uuid):
        item = self.fn_state_map.get(node_key)
        if item:
            item.datablock_uuid = datablock_uuid
        else:
            item = self.fn_state_map.add()
            item.name = node_key
            item.datablock_uuid = datablock_uuid

    def clear_state_map(self):
        self.fn_state_map.clear()

    def interface_update(self, context):
        if getattr(self, "fn_inputs", None):
            self.fn_inputs.sync_inputs(self)

    def update(self):
        """Keep inputs in sync when the node tree changes."""
        if getattr(self, "fn_inputs", None):
            self.fn_inputs.sync_inputs(self)

    # Poll: always available
    @classmethod
    def poll(cls, context):
        return True

classes = (
    FNStateMapItem,
    FileNodeTreeInput,
    FNSceneReference,
    FileNodesTreeInputs,
    FileNodesTree,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)