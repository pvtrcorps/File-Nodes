import bpy
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

categories = [
    NodeCategory('FILE_NODES_GROUP', 'Group', items=[
        NodeItem('NodeGroupInput', label='Group Input'),
        NodeItem('NodeGroupOutput', label='Group Output'),
        NodeItem('FNGroupNode'),
    ]),
    NodeCategory('FILE_NODES_FILE', 'File', items=[
        NodeItem('FNReadBlendNode'),
        NodeItem('FNImportAlembicNode'),
    ]),
    NodeCategory('FILE_NODES_LIST', 'Utils', items=[
        NodeItem('FNCreateList'),
        NodeItem('FNGetItemByName'),
        NodeItem('FNGetItemByIndex'),
        NodeItem('FNGetItemInList'),
        NodeItem('FNJoinStrings'),
        NodeItem('FNSplitString'),
        NodeItem('FNCombineXYZ'),
        NodeItem('FNSeparateXYZ'),
        NodeItem('FNSwitch'),
        NodeItem('FNIndexSwitch'),
        NodeItem('FNSetCustomProperty'),
        NodeItem('FNExecLogic'),
    ]),
    NodeCategory('FILE_NODES_SCENE', 'Scene', items=[
        NodeItem('FNSceneInputNode'),
        NodeItem('FNNewScene'),
        NodeItem('FNLinkToScene'),
        NodeItem('FNSetWorldNode'),
        NodeItem('FNSetRenderEngine'),
        NodeItem('FNSetSceneName'),
        NodeItem('FNSetSceneViewlayers'),
        NodeItem('FNCyclesSceneProps'),
        NodeItem('FNEeveeSceneProps'),
        NodeItem('FNWorkbenchSceneProps'),
        NodeItem('FNOutputProps'),
        NodeItem('FNSceneProps'),
        NodeItem('FNSceneViewlayers'),
        NodeItem('FNRenderScenesNode'),
        NodeItem('FNOutputScenesNode'),
        NodeItem('FNOutlinerNode'),
    ]),
    NodeCategory('FILE_NODES_VIEWLAYER', 'Viewlayer', items=[
        NodeItem('FNViewLayerVisibility'),
        NodeItem('FNNewViewLayer'),
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
        NodeItem('FNNewCamera'),
        NodeItem('FNCameraProps'),
    ]),
    NodeCategory('FILE_NODES_LIGHT', 'Light', items=[
        NodeItem('FNLightInputNode'),
        NodeItem('FNNewLight'),
        NodeItem('FNLightProps'),
    ]),
    NodeCategory('FILE_NODES_MESH', 'Mesh', items=[
        NodeItem('FNMeshInputNode'),
        NodeItem('FNNewMesh'),
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
        NodeItem('FNNewText'),
    ]),
    NodeCategory('FILE_NODES_WORKSPACE', 'WorkSpace', items=[
        NodeItem('FNWorkSpaceInputNode'),
    ]),
    NodeCategory('FILE_NODES_VALUES', 'Values', items=[
        NodeItem('FNBoolInputNode'),
        NodeItem('FNExecInputNode'),
        NodeItem('FNFloatInputNode'),
        NodeItem('FNIntInputNode'),
        NodeItem('FNStringInputNode'),
        NodeItem('FNVectorInputNode'),
        NodeItem('FNColorInputNode'),
    ]),
]

def register():
    register_node_categories('FILE_NODES', categories)

def unregister():
    unregister_node_categories('FILE_NODES')
