import bpy
from bpy.types import Node
from ..operators import auto_evaluate_if_enabled

from .base import FNBaseNode
from ..sockets import (
    FNSocketBool, FNSocketFloat, FNSocketInt, FNSocketString,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
)


class FNBoolInputNode(Node, FNBaseNode):
    bl_idname = "FNBoolInputNode"
    bl_label = "Boolean Input"

    value: bpy.props.BoolProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketBool', "Boolean")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Value")

    def process(self, context, inputs):
        return {"Boolean": self.value}


class FNFloatInputNode(Node, FNBaseNode):
    bl_idname = "FNFloatInputNode"
    bl_label = "Float Input"

    value: bpy.props.FloatProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketFloat', "Float")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Value")

    def process(self, context, inputs):
        return {"Float": self.value}


class FNIntInputNode(Node, FNBaseNode):
    bl_idname = "FNIntInputNode"
    bl_label = "Integer Input"

    value: bpy.props.IntProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketInt', "Integer")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Value")

    def process(self, context, inputs):
        return {"Integer": self.value}


class FNStringInputNode(Node, FNBaseNode):
    bl_idname = "FNStringInputNode"
    bl_label = "String Input"

    value: bpy.props.StringProperty(name="Value", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketString', "String")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Value")

    def process(self, context, inputs):
        return {"String": self.value}


class FNCameraInputNode(Node, FNBaseNode):
    bl_idname = "FNCameraInputNode"
    bl_label = "Camera Input"

    value: bpy.props.PointerProperty(type=bpy.types.Camera, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketCamera', "Camera")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Camera")

    def process(self, context, inputs):
        return {"Camera": self.value}


class FNImageInputNode(Node, FNBaseNode):
    bl_idname = "FNImageInputNode"
    bl_label = "Image Input"

    value: bpy.props.PointerProperty(type=bpy.types.Image, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketImage', "Image")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Image")

    def process(self, context, inputs):
        return {"Image": self.value}


class FNLightInputNode(Node, FNBaseNode):
    bl_idname = "FNLightInputNode"
    bl_label = "Light Input"

    value: bpy.props.PointerProperty(type=bpy.types.Light, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketLight', "Light")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Light")

    def process(self, context, inputs):
        return {"Light": self.value}


class FNMaterialInputNode(Node, FNBaseNode):
    bl_idname = "FNMaterialInputNode"
    bl_label = "Material Input"

    value: bpy.props.PointerProperty(type=bpy.types.Material, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketMaterial', "Material")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Material")

    def process(self, context, inputs):
        return {"Material": self.value}


class FNMeshInputNode(Node, FNBaseNode):
    bl_idname = "FNMeshInputNode"
    bl_label = "Mesh Input"

    value: bpy.props.PointerProperty(type=bpy.types.Mesh, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketMesh', "Mesh")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Mesh")

    def process(self, context, inputs):
        return {"Mesh": self.value}


class FNNodeTreeInputNode(Node, FNBaseNode):
    bl_idname = "FNNodeTreeInputNode"
    bl_label = "Node Tree Input"

    value: bpy.props.PointerProperty(type=bpy.types.NodeTree, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketNodeTree', "Node Tree")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Node Tree")

    def process(self, context, inputs):
        return {"Node Tree": self.value}


class FNTextInputNode(Node, FNBaseNode):
    bl_idname = "FNTextInputNode"
    bl_label = "Text Input"

    value: bpy.props.PointerProperty(type=bpy.types.Text, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketText', "Text")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Text")

    def process(self, context, inputs):
        return {"Text": self.value}


class FNWorkSpaceInputNode(Node, FNBaseNode):
    bl_idname = "FNWorkSpaceInputNode"
    bl_label = "WorkSpace Input"

    value: bpy.props.PointerProperty(type=bpy.types.WorkSpace, update=auto_evaluate_if_enabled)

    def init(self, context):
        self.outputs.new('FNSocketWorkSpace', "WorkSpace")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="WorkSpace")

    def process(self, context, inputs):
        return {"WorkSpace": self.value}


_classes = (
    FNBoolInputNode, FNFloatInputNode, FNIntInputNode, FNStringInputNode,
    FNCameraInputNode, FNImageInputNode, FNLightInputNode, FNMaterialInputNode,
    FNMeshInputNode, FNNodeTreeInputNode, FNTextInputNode, FNWorkSpaceInputNode,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

