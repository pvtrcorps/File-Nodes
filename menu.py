
import bpy
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

categories = [
    NodeCategory('FILE_NODES_GROUP', 'Group', items=[
        NodeItem('FNGroupInputNode'),
        NodeItem('FNGroupOutputNode'),
    ]),
    NodeCategory('FILE_NODES_INPUT', 'Input', items=[
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
    ]),
    NodeCategory('FILE_NODES_FILE', 'File', items=[
        NodeItem('FNReadBlendNode'),
        NodeItem('FNImportAlembicNode'),
    ]),
    NodeCategory('FILE_NODES_LIST', 'Lists', items=[
        NodeItem('FNCreateList'),
        NodeItem('FNGetItemByName'),
        NodeItem('FNGetItemByIndex'),
    ]),
    NodeCategory('FILE_NODES_SCENE', 'Scene', items=[
        NodeItem('FNLinkToScene'),
        NodeItem('FNLinkToCollection'),
        NodeItem('FNSetWorldNode'),
    ]),
    NodeCategory('FILE_NODES_PROPERTIES', 'Properties', items=[
        NodeItem('FNSetRenderEngine'),
        NodeItem('FNCyclesSceneProps'),
        NodeItem('FNEeveeSceneProps'),
        NodeItem('FNWorkbenchSceneProps'),
        NodeItem('FNOutputProps'),
        NodeItem('FNSceneProps'),
        NodeItem('FNObjectProps'),
        NodeItem('FNCyclesObjectProps'),
        NodeItem('FNEeveeObjectProps'),
        NodeItem('FNCollectionProps'),
        NodeItem('FNWorldProps'),
        NodeItem('FNCameraProps'),
        NodeItem('FNLightProps'),
        NodeItem('FNMeshProps'),
        NodeItem('FNMaterialProps'),
    ]),
]

def register():
    register_node_categories('FILE_NODES', categories)

def unregister():
    unregister_node_categories('FILE_NODES')
