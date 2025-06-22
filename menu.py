
import bpy
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

categories = [
    NodeCategory('FILE_NODES_CATEGORY', 'File Nodes', items=[
        NodeItem('FNGroupInputNode'),
        NodeItem('FNBoolInputNode'),
        NodeItem('FNFloatInputNode'),
        NodeItem('FNIntInputNode'),
        NodeItem('FNStringInputNode'),
        NodeItem('FNSceneInputNode'),
        NodeItem('FNObjectInputNode'),
        NodeItem('FNCollectionInputNode'),
        NodeItem('FNWorldInputNode'),
        NodeItem('FNCameraInputNode'),
        NodeItem('FNImageInputNode'),
        NodeItem('FNLightInputNode'),
        NodeItem('FNMaterialInputNode'),
        NodeItem('FNMeshInputNode'),
        NodeItem('FNNodeTreeInputNode'),
        NodeItem('FNTextInputNode'),
        NodeItem('FNWorkSpaceInputNode'),
        NodeItem('FNReadBlendNode'),
        NodeItem('FNCreateList'),
        NodeItem('FNGetItemByName'),
        NodeItem('FNGetItemByIndex'),
        NodeItem('FNLinkToScene'),
        NodeItem('FNLinkToCollection'),
        NodeItem('FNSetWorldNode'),
        NodeItem('FNGroupOutputNode'),
    ]),
]

def register():
    register_node_categories('FILE_NODES', categories)

def unregister():
    unregister_node_categories('FILE_NODES')
