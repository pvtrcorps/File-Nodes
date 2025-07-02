import bpy
from bpy.types import Node
from ..operators import auto_evaluate_if_enabled
from .base import FNBaseNode
from ..sockets import (
    FNSocketScene,
    FNSocketObject,
    FNSocketCollection,
    FNSocketWorld,
    FNSocketCamera,
    FNSocketImage,
    FNSocketLight,
    FNSocketMaterial,
    FNSocketMesh,
    FNSocketNodeTree,
    FNSocketText,
    FNSocketWorkSpace,
    FNSocketViewLayer,
)

# Mapping for single datablock sockets
_socket_single = {
    "SCENE": "FNSocketScene",
    "OBJECT": "FNSocketObject",
    "COLLECTION": "FNSocketCollection",
    "WORLD": "FNSocketWorld",
    "CAMERA": "FNSocketCamera",
    "IMAGE": "FNSocketImage",
    "LIGHT": "FNSocketLight",
    "MATERIAL": "FNSocketMaterial",
    "MESH": "FNSocketMesh",
    "NODETREE": "FNSocketNodeTree",
    "TEXT": "FNSocketText",
    "WORKSPACE": "FNSocketWorkSpace",
    "VIEW_LAYER": "FNSocketViewLayer",
}


class FNSetCustomProperty(Node, FNBaseNode):
    """Set a custom property on a chosen datablock."""

    bl_idname = "FNSetCustomProperty"
    bl_label = "Set Custom Property"

    data_block_type: bpy.props.EnumProperty(
        name="Datablock Type",
        items=[
            ("SCENE", "Scene", "Apply custom property to a Scene datablock"),
            ("OBJECT", "Object", "Apply custom property to an Object datablock"),
            ("COLLECTION", "Collection", "Apply custom property to a Collection datablock"),
            ("WORLD", "World", "Apply custom property to a World datablock"),
            ("CAMERA", "Camera", "Apply custom property to a Camera datablock"),
            ("IMAGE", "Image", "Apply custom property to an Image datablock"),
            ("LIGHT", "Light", "Apply custom property to a Light datablock"),
            ("MATERIAL", "Material", "Apply custom property to a Material datablock"),
            ("MESH", "Mesh", "Apply custom property to a Mesh datablock"),
            ("NODETREE", "Node Tree", "Apply custom property to a Node Tree datablock"),
            ("TEXT", "Text", "Apply custom property to a Text datablock"),
            ("WORKSPACE", "WorkSpace", "Apply custom property to a WorkSpace datablock"),
            ("VIEW_LAYER", "View Layer", "Apply custom property to a View Layer datablock"),
        ],
        default="OBJECT",
        update=lambda self, context: self.update_data_block_type(context),
    )

    property_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("BOOLEAN", "Boolean", "Boolean property (True/False)"),
            ("INT", "Integer", "Integer property"),
            ("FLOAT", "Float", "Float property"),
            ("STRING", "String", "String property"),
            ("VECTOR", "Vector", "Vector property (e.g., XYZ coordinates)"),
            ("COLOR", "Color", "Color property (e.g., RGBA values)"),
        ],
        default="STRING",
        update=lambda self, context: self.update_property_type(context),
    )

    def update_data_block_type(self, context):
        self._update_sockets(context)
        auto_evaluate_if_enabled(context)

    def update_property_type(self, context):
        self._update_sockets(context)  # Update sockets when property type changes
        auto_evaluate_if_enabled(context)

    def _update_sockets(self, context=None):
        # Clear existing sockets
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])

        # Add input socket for the selected datablock type
        datablock_socket_id = _socket_single.get(self.data_block_type)
        if datablock_socket_id:
            socket = self.inputs.new(datablock_socket_id, self.data_block_type.replace("_", " ").title())
            socket.show_selector = True

        # Add input for property Name, with default value
        name_socket = self.inputs.new("FNSocketString", "Name")
        name_socket.value = "custom_prop"

        # Add input for the custom property value based on property_type
        if self.property_type == "BOOLEAN":
            self.inputs.new("FNSocketBool", "Value")
            self.inputs.new("FNSocketBool", "Default Value")
        elif self.property_type == "INT":
            self.inputs.new("FNSocketInt", "Value")
            self.inputs.new("FNSocketInt", "Default Value")
            self.inputs.new("FNSocketInt", "Min")
            self.inputs.new("FNSocketInt", "Max")
        elif self.property_type == "FLOAT":
            self.inputs.new("FNSocketFloat", "Value")
            self.inputs.new("FNSocketFloat", "Default Value")
            self.inputs.new("FNSocketFloat", "Min")
            self.inputs.new("FNSocketFloat", "Max")
        elif self.property_type == "STRING":
            self.inputs.new("FNSocketString", "Value")
            self.inputs.new("FNSocketString", "Default Value")
            # Subtype for string
            self.inputs.new("FNSocketString", "Subtype").value = "NONE"  # Placeholder for enum
        elif self.property_type == "VECTOR":
            self.inputs.new("FNSocketVector", "Value")
            self.inputs.new("FNSocketVector", "Default Value")
            # Subtype for vector
            self.inputs.new("FNSocketString", "Subtype").value = "NONE"  # Placeholder for enum
        elif self.property_type == "COLOR":
            self.inputs.new("FNSocketColor", "Value")
            self.inputs.new("FNSocketColor", "Default Value")

        # Add input for Description
        self.inputs.new("FNSocketString", "Description")

        # Add input for Library Override
        self.inputs.new("FNSocketBool", "Library Override")

        # Add output socket for the modified datablock
        if datablock_socket_id:
            self.outputs.new(datablock_socket_id, self.data_block_type.replace("_", " ").title())

        if context is not None:
            auto_evaluate_if_enabled(context)

    def init(self, context):
        self._update_sockets(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_block_type", text="Datablock")
        layout.prop(self, "property_type", text="Type")

    def process(self, context, inputs, manager):
        datablock = inputs.get(self.data_block_type.replace("_", " ").title())
        prop_name = inputs.get("Name")  # This will now correctly get the value from the socket or its default
        prop_description = inputs.get("Description")
        library_override = inputs.get("Library Override")

        print(f"[DEBUG] Processing Set Custom Property node.")
        print(f"[DEBUG] Datablock: {datablock}")
        print(f"[DEBUG] Property Name: {prop_name}")

        prop_value = inputs.get("Value")
        value_socket = self.inputs.get("Value")
        if value_socket and not value_socket.is_linked:
            prop_value = inputs.get("Default Value")

        print(f"[DEBUG] Property Value to set: {prop_value}")

        if datablock and prop_name:
            try:
                id_props = datablock.id_properties_ensure()
                id_props[prop_name] = prop_value

                if "_RNA_UI" not in id_props.keys():
                    id_props["_RNA_UI"] = {}
                if prop_name not in id_props["_RNA_UI"].keys():
                    id_props["_RNA_UI"][prop_name] = {}

                prop_metadata = id_props["_RNA_UI"][prop_name]
                print(f"[DEBUG] Metadata before update: {prop_metadata}")

                if self.property_type == "INT":
                    prop_metadata["min"] = inputs.get("Min")
                    prop_metadata["max"] = inputs.get("Max")
                elif self.property_type == "FLOAT":
                    prop_metadata["min"] = inputs.get("Min")
                    prop_metadata["max"] = inputs.get("Max")
                elif self.property_type == "STRING":
                    prop_metadata["subtype"] = inputs.get("Subtype")
                elif self.property_type == "VECTOR":
                    prop_metadata["subtype"] = inputs.get("Subtype")

                if prop_description:
                    prop_metadata["description"] = prop_description

                print(f"[DEBUG] Metadata after update: {prop_metadata}")

            except Exception as e:
                print(f"[ERROR] Error setting custom property: {e}")
                pass
        out_name = self.data_block_type.replace("_", " ").title()
        return {out_name: datablock}

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"


def register():
    bpy.utils.register_class(FNSetCustomProperty)


def unregister():
    bpy.utils.unregister_class(FNSetCustomProperty)
