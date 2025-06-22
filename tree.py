
import bpy
from bpy.types import NodeTree

class FileNodesTree(NodeTree):
    bl_idname = "FileNodesTreeType"
    bl_label = "File Nodes"
    bl_icon = 'NODETREE'

    fn_enabled: bpy.props.BoolProperty(name='Enabled', default=True)
    fn_stack_index: bpy.props.IntProperty(name='Stack Index', default=0, min=0)

    # Poll: always available
    @classmethod
    def poll(cls, context):
        return True

def register():
    bpy.utils.register_class(FileNodesTree)

def unregister():
    bpy.utils.unregister_class(FileNodesTree)
