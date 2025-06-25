
bl_info = {
    "name": "File Nodes MVP",
    "author": "ChatGPT (MVP generator)",
    "version": (0, 1, 0),
    "blender": (4, 4, 0),
    "location": "Node Editor > File Nodes",
    "description": "Prototype node-based file/scene management",
    "category": "Object",
}

# Keep a reference to the addon name so other modules can access
# preferences without guessing the package string.
ADDON_NAME = __name__

try:
    import bpy
except Exception:  # pragma: no cover - allow running tests without bpy
    bpy = None

if bpy and __package__:
    import importlib
    from . import tree, sockets, nodes, operators, ui, menu, modifiers
    modules = [tree, sockets, nodes, operators, ui, menu, modifiers]
else:  # Running outside Blender or without a package context
    modules = []


if bpy and getattr(getattr(bpy, 'types', None), 'AddonPreferences', None):
    class FileNodesPreferences(bpy.types.AddonPreferences):
        bl_idname = ADDON_NAME

        auto_evaluate: bpy.props.BoolProperty(
            name="Auto Evaluate",
            description="Automatically evaluate node trees when properties change",
            default=False,
        )

        def draw(self, context):
            layout = self.layout
            layout.prop(self, "auto_evaluate")

    def register():
        bpy.utils.register_class(FileNodesPreferences)
        for m in modules:
            importlib.reload(m)
            if hasattr(m, "register"):
                m.register()

    def unregister():
        for m in reversed(modules):
            if hasattr(m, "unregister"):
                m.unregister()
        bpy.utils.unregister_class(FileNodesPreferences)
else:  # pragma: no cover - noop if bpy is unavailable
    def register():
        pass

    def unregister():
        pass
