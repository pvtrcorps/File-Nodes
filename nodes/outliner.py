"""Node to display scene hierarchy similar to Blender's Outliner."""

import bpy
from bpy.types import Node, PropertyGroup, UIList

from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import auto_evaluate_if_enabled


class FNOutlinerItem(PropertyGroup):
    """Representation of a collection or object for the UI list."""

    name: bpy.props.StringProperty()
    icon: bpy.props.StringProperty(default='NONE')
    depth: bpy.props.IntProperty()
    parent_index: bpy.props.IntProperty(default=-1)
    expanded: bpy.props.BoolProperty(name="Expanded", default=True)
    has_children: bpy.props.BoolProperty(default=False)


class FN_UL_outliner(UIList):
    bl_idname = "FN_UL_outliner"

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = []
        for item in items:
            visible = True
            parent_idx = item.parent_index
            while parent_idx != -1:
                parent = items[parent_idx]
                if not parent.expanded:
                    visible = False
                    break
                parent_idx = parent.parent_index
            flt_flags.append(self.bitflag_filter_item if visible else 0)
        return flt_flags, []

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            for _ in range(item.depth):
                row.label(icon='BLANK1', text="")
            if item.has_children:
                row.prop(item, "expanded", text="", icon='TRIA_DOWN' if item.expanded else 'TRIA_RIGHT', emboss=False)
            else:
                row.label(icon='BLANK1', text="")
            row.label(text=item.name, icon=item.icon or 'DOT')


def _icon_for_object(obj):
    return {
        'CAMERA': 'CAMERA_DATA',
        'LIGHT': 'LIGHT_DATA',
        'MESH': 'MESH_DATA',
        'CURVE': 'CURVE_DATA',
        'POINTCLOUD': 'POINTCLOUD_DATA',
    }.get(obj.type, 'OBJECT_DATA')


class FNOutlinerNode(Node, FNBaseNode):
    """Display the hierarchy of a scene."""
    bl_idname = "FNOutlinerNode"
    bl_label = "Outliner"

    items: bpy.props.CollectionProperty(type=FNOutlinerItem)
    active_index: bpy.props.IntProperty()
    show_objects: bpy.props.BoolProperty(name="Show Objects", default=False, update=auto_evaluate_if_enabled)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")

    def update(self):
        auto_evaluate_if_enabled(bpy.context)

    def _collect(self, coll, depth=0, parent=-1, items=None):
        if items is None:
            items = []
        idx = len(items)
        items.append((coll.name, 'OUTLINER_COLLECTION', depth, parent, bool(coll.children) or (self.show_objects and coll.objects)))
        for child in coll.children:
            self._collect(child, depth + 1, idx, items)
        if self.show_objects:
            for obj in coll.objects:
                items.append((obj.name, _icon_for_object(obj), depth + 1, idx, False))
        return items

    def _sync_items(self, scene):
        self.items.clear()
        if not scene:
            return
        data = self._collect(scene.collection)
        for name, icon, depth, parent, has_children in data:
            item = self.items.add()
            item.name = name
            item.icon = icon
            item.depth = depth
            item.parent_index = parent
            item.has_children = has_children

    def draw_buttons(self, context, layout):
        layout.prop(self, "show_objects", toggle=True)
        if not self.items:
            layout.label(text="No Scene")
            return
        layout.template_list("FN_UL_outliner", "", self, "items", self, "active_index", rows=5)

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            self._sync_items(scene)
        else:
            self.items.clear()
        return {}


_classes = (
    FNOutlinerItem,
    FN_UL_outliner,
    FNOutlinerNode,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

