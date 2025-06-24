import bpy
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

categories = [
    NodeCategory('FILE_NODES_GROUP', 'Group', items=[
        NodeItem('FNGroupInputNode', label='Interface Input'),
        NodeItem('FNGroupOutputNode'),
    ]),
    NodeCategory('FILE_NODES_FILE', 'File', items=[
        NodeItem('FNReadBlendNode'),
        NodeItem('FNImportAlembicNode'),
    ]),
    NodeCategory('FILE_NODES_LIST', 'Lists', items=[
        NodeItem('FNCreateList'),
        NodeItem('FNGetItemByName'),
        NodeItem('FNGetItemByIndex'),
        NodeItem('FNJoinStrings'),
        NodeItem('FNSplitString'),
    ]),
    NodeCategory('FILE_NODES_SCENE', 'Scene', items=[
        NodeItem('FNSceneInputNode'),
        NodeItem('FNNewScene'),
        NodeItem('FNLinkToScene'),
        NodeItem('FNSetWorldNode'),
        NodeItem('FNSetRenderEngine'),
        NodeItem('FNSetSceneName'),
        NodeItem('FNCyclesSceneProps'),
        NodeItem('FNEeveeSceneProps'),
        NodeItem('FNWorkbenchSceneProps'),
        NodeItem('FNOutputProps'),
        NodeItem('FNSceneProps'),
        NodeItem('FNRenderScenesNode'),
        NodeItem('FNOutputScenesNode'),
    ]),
    NodeCategory('FILE_NODES_OBJECT', 'Object', items=[
        NodeItem('FNObjectInputNode'),
        NodeItem('FNNewObject'),
        NodeItem('FNObjectProps'),
        NodeItem('FNCyclesObjectProps'),
        NodeItem('FNEeveeObjectProps'),
        NodeItem('FNSetObjectName'),
    ]),
    NodeCategory('FILE_NODES_COLLECTION', 'Collection', items=[
        NodeItem('FNCollectionInputNode'),
        NodeItem('FNNewCollection'),
        NodeItem('FNLinkToCollection'),
        NodeItem('FNCollectionProps'),
        NodeItem('FNSetCollectionName'),
    ]),
    NodeCategory('FILE_NODES_WORLD', 'World', items=[
        NodeItem('FNWorldInputNode'),
        NodeItem('FNNewWorld'),
        NodeItem('FNWorldProps'),
    ]),
    NodeCategory('FILE_NODES_MATERIAL', 'Material', items=[
        NodeItem('FNMaterialInputNode'),
        NodeItem('FNNewMaterial'),
        NodeItem('FNMaterialProps'),
    ]),
    NodeCategory('FILE_NODES_CAMERA', 'Camera', items=[
        NodeItem('FNCameraInputNode'),
        NodeItem('FNCameraProps'),
    ]),
    NodeCategory('FILE_NODES_LIGHT', 'Light', items=[
        NodeItem('FNLightInputNode'),
        NodeItem('FNLightProps'),
    ]),
    NodeCategory('FILE_NODES_MESH', 'Mesh', items=[
        NodeItem('FNMeshInputNode'),
        NodeItem('FNMeshProps'),
    ]),
    NodeCategory('FILE_NODES_IMAGE', 'Image', items=[
        NodeItem('FNImageInputNode'),
    ]),
    NodeCategory('FILE_NODES_NODETREE', 'Node Tree', items=[
        NodeItem('FNNodeTreeInputNode'),
    ]),
    NodeCategory('FILE_NODES_TEXT', 'Text', items=[
        NodeItem('FNTextInputNode'),
    ]),
    NodeCategory('FILE_NODES_WORKSPACE', 'WorkSpace', items=[
        NodeItem('FNWorkSpaceInputNode'),
    ]),
    NodeCategory('FILE_NODES_VALUES', 'Values', items=[
        NodeItem('FNBoolInputNode'),
        NodeItem('FNFloatInputNode'),
        NodeItem('FNIntInputNode'),
        NodeItem('FNStringInputNode'),
    ]),
]

def register():
    register_node_categories('FILE_NODES', categories)

def unregister():
    unregister_node_categories('FILE_NODES')
