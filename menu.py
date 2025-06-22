
import bpy
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

categories = [
    NodeCategory('FILE_NODES_CATEGORY', 'File Nodes', items=[
        NodeItem('FNGroupInputNode'),
        NodeItem('FNReadBlendNode'),
        NodeItem('FNCreateList'),
        NodeItem('FNGetItemByName'),
        NodeItem('FNSetWorldNode'),
        NodeItem('FNGroupOutputNode'),
    ]),
]

def register():
    register_node_categories('FILE_NODES', categories)

def unregister():
    unregister_node_categories('FILE_NODES')
