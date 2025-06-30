"""Node for creating new lights."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketLight, FNSocketString


class FNNewLight(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new light datablock."""
    bl_idname = "FNNewLight"
    bl_label = "New Light"

    light_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('POINT', 'Point', ''),
            ('SUN', 'Sun', ''),
            ('SPOT', 'Spot', ''),
            ('AREA', 'Area', ''),
        ],
        default='POINT',
        update=lambda self, context: None,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Light"
        self.outputs.new('FNSocketLight', "Light")

    def draw_buttons(self, context, layout):
        layout.prop(self, "light_type", text="Type")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        name = inputs.get("Name") or "Light"
        key = (name, self.light_type)
        cached = self.cache_get(key)
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if cached is not None:
            return {"Light": cached}

        if ctx:
            storage = getattr(ctx, "_original_values", {})
            for lt in storage.get("created_ids", []):
                if isinstance(lt, bpy.types.Light) and lt.name == name:
                    cached = lt
                    break

        if cached is None:
            existing = bpy.data.lights.get(name)
            if existing is not None:
                cached = existing

        if cached is not None:
            self.cache_store(key, cached)
            if ctx:
                ctx.remember_created_id(cached)
            return {"Light": cached}

        light = bpy.data.lights.new(name, type=self.light_type)
        self.cache_store(key, light)
        if ctx:
            ctx.remember_created_id(light)
        return {"Light": light}


def register():
    bpy.utils.register_class(FNNewLight)


def unregister():
    bpy.utils.unregister_class(FNNewLight)
