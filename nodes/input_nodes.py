"""Nodes that provide constant input values for node trees."""

import bpy
from bpy.types import Node
from ..operators import auto_evaluate_if_enabled

from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import (
    FNSocketBool, FNSocketFloat, FNSocketVector, FNSocketInt, FNSocketString,
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
)


class FNBoolInputNode(Node, FNBaseNode):
    """Output a boolean value."""
    bl_idname = "FNBoolInputNode"
    bl_label = "Boolean Input"

    value: bpy.props.BoolProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketBool', "Boolean")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Boolean": self.value}


class FNFloatInputNode(Node, FNBaseNode):
    """Output a float value."""
    bl_idname = "FNFloatInputNode"
    bl_label = "Float Input"

    value: bpy.props.FloatProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketFloat', "Float")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Float": self.value}


class FNIntInputNode(Node, FNBaseNode):
    """Output an integer value."""
    bl_idname = "FNIntInputNode"
    bl_label = "Integer Input"

    value: bpy.props.IntProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketInt', "Integer")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Integer": self.value}


class FNStringInputNode(Node, FNBaseNode):
    """Output a string value."""
    bl_idname = "FNStringInputNode"
    bl_label = "String Input"

    value: bpy.props.StringProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketString', "String")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"String": self.value}


"""Nodes that provide constant input values for node trees."""

import bpy
from bpy.types import Node
from ..operators import auto_evaluate_if_enabled

from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import (
    FNSocketBool, FNSocketFloat, FNSocketVector, FNSocketInt, FNSocketString,
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
    FNSocketColor,
)


class FNBoolInputNode(Node, FNBaseNode):
    """Output a boolean value."""
    bl_idname = "FNBoolInputNode"
    bl_label = "Boolean Input"

    value: bpy.props.BoolProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketBool', "Boolean")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Boolean": self.value}


class FNFloatInputNode(Node, FNBaseNode):
    """Output a float value."""
    bl_idname = "FNFloatInputNode"
    bl_label = "Float Input"

    value: bpy.props.FloatProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketFloat', "Float")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Float": self.value}


class FNIntInputNode(Node, FNBaseNode):
    """Output an integer value."""
    bl_idname = "FNIntInputNode"
    bl_label = "Integer Input"

    value: bpy.props.IntProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketInt', "Integer")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Integer": self.value}


class FNStringInputNode(Node, FNBaseNode):
    """Output a string value."""
    bl_idname = "FNStringInputNode"
    bl_label = "String Input"

    value: bpy.props.StringProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketString', "String")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"String": self.value}


class FNVectorInputNode(Node, FNBaseNode):
    """Output a 3D vector."""
    bl_idname = "FNVectorInputNode"
    bl_label = "Vector Input"

    value: bpy.props.FloatVectorProperty(name="Value", size=3, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketVector', "Vector")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Vector": self.value}


class FNColorInputNode(Node, FNBaseNode):
    """Output a color value (RGBA)."""
    bl_idname = "FNColorInputNode"
    bl_label = "Color Input"

    value: bpy.props.FloatVectorProperty(name="Value", size=4, subtype='COLOR', default=(1.0, 1.0, 1.0, 1.0), update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketColor', "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    def process(self, context, inputs, manager):
        return {"Color": self.value}


class FNSceneInputNode(Node, FNCacheIDMixin, FNBaseNode):
    """Duplicate a scene with a new name."""
    bl_idname = "FNSceneInputNode"
    bl_label = "Scene Input"

    def init(self, context):
        sock = self.inputs.new('FNSocketScene', "Scene")
        sock.show_selector = True
        self.inputs.new('FNSocketString', "Name")
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs, manager):
        scene = inputs.get("Scene")
        if not scene:
            return {"Scene": None}
        name = inputs.get("Name") or scene.name
        key = (scene.as_pointer(), name)
        cached = self.cache_get(key)
        if cached is not None:
            return {"Scene": cached}

        if cached is None:
            cached = bpy.data.scenes.get(name)

        if cached is not None:
            self.cache_store(key, cached)
            return {"Scene": cached}

        dup = scene.copy()
        dup.name = name
        dup.use_extra_user = True
        self.cache_store(key, dup)
        return {"Scene": dup}


class FNObjectInputNode(Node, FNBaseNode):
    """Provide a reference to an object."""
    bl_idname = "FNObjectInputNode"
    bl_label = "Object Input"

    value: bpy.props.PointerProperty(type=bpy.types.Object, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketObject', "Object")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Object")

    def process(self, context, inputs, manager):
        return {"Object": self.value}


class FNCollectionInputNode(Node, FNBaseNode):
    """Provide a reference to a collection."""
    bl_idname = "FNCollectionInputNode"
    bl_label = "Collection Input"

    value: bpy.props.PointerProperty(type=bpy.types.Collection, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketCollection', "Collection")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Collection")

    def process(self, context, inputs, manager):
        return {"Collection": self.value}


class FNWorldInputNode(Node, FNBaseNode):
    """Provide a reference to a world."""
    bl_idname = "FNWorldInputNode"
    bl_label = "World Input"

    value: bpy.props.PointerProperty(type=bpy.types.World, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketWorld', "World")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="World")

    def process(self, context, inputs, manager):
        return {"World": self.value}


class FNCameraInputNode(Node, FNBaseNode):
    """Provide a reference to a camera."""
    bl_idname = "FNCameraInputNode"
    bl_label = "Camera Input"

    value: bpy.props.PointerProperty(type=bpy.types.Camera, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketCamera', "Camera")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Camera")

    def process(self, context, inputs, manager):
        return {"Camera": self.value}


class FNImageInputNode(Node, FNBaseNode):
    """Provide a reference to an image."""
    bl_idname = "FNImageInputNode"
    bl_label = "Image Input"

    value: bpy.props.PointerProperty(type=bpy.types.Image, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketImage', "Image")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Image")

    def process(self, context, inputs, manager):
        return {"Image": self.value}


class FNLightInputNode(Node, FNBaseNode):
    """Provide a reference to a light."""
    bl_idname = "FNLightInputNode"
    bl_label = "Light Input"

    value: bpy.props.PointerProperty(type=bpy.types.Light, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketLight', "Light")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Light")

    def process(self, context, inputs, manager):
        return {"Light": self.value}


class FNMaterialInputNode(Node, FNBaseNode):
    """Provide a reference to a material."""
    bl_idname = "FNMaterialInputNode"
    bl_label = "Material Input"

    value: bpy.props.PointerProperty(type=bpy.types.Material, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketMaterial', "Material")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Material")

    def process(self, context, inputs, manager):
        return {"Material": self.value}


class FNMeshInputNode(Node, FNBaseNode):
    """Provide a reference to a mesh."""
    bl_idname = "FNMeshInputNode"
    bl_label = "Mesh Input"

    value: bpy.props.PointerProperty(type=bpy.types.Mesh, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketMesh', "Mesh")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Mesh")

    def process(self, context, inputs, manager):
        return {"Mesh": self.value}


class FNNodeTreeInputNode(Node, FNBaseNode):
    """Provide a reference to a node tree."""
    bl_idname = "FNNodeTreeInputNode"
    bl_label = "Node Tree Input"

    value: bpy.props.PointerProperty(type=bpy.types.NodeTree, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketNodeTree', "Node Tree")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Node Tree")

    def process(self, context, inputs, manager):
        return {"Node Tree": self.value}


class FNTextInputNode(Node, FNBaseNode):
    """Provide a reference to a text block."""
    bl_idname = "FNTextInputNode"
    bl_label = "Text Input"

    value: bpy.props.PointerProperty(type=bpy.types.Text, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketText', "Text")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Text")

    def process(self, context, inputs, manager):
        return {"Text": self.value}


class FNWorkSpaceInputNode(Node, FNBaseNode):
    """Provide a reference to a workspace."""
    bl_idname = "FNWorkSpaceInputNode"
    bl_label = "WorkSpace Input"

    value: bpy.props.PointerProperty(type=bpy.types.WorkSpace, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketWorkSpace', "WorkSpace")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="WorkSpace")

    def process(self, context, inputs, manager):
        return {"WorkSpace": self.value}


_classes = (
    FNBoolInputNode, FNFloatInputNode, FNIntInputNode, FNStringInputNode,
    FNVectorInputNode, FNColorInputNode,
    FNSceneInputNode, FNObjectInputNode, FNCollectionInputNode,
    FNWorldInputNode, FNCameraInputNode, FNImageInputNode, FNLightInputNode, FNMaterialInputNode,
    FNMeshInputNode, FNNodeTreeInputNode, FNTextInputNode, FNWorkSpaceInputNode,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)