# Copyright (c) 2019-2020 Elie Michel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose and noninfringement. In no event shall
# the authors or copyright holders be liable for any claim, damages or other
# liability, whether in an action of contract, tort or otherwise, arising from,
# out of or in connection with the software or the use or other dealings in the
# Software.
#
# This file is part of LilySurfaceScrapper, a Blender add-on to import materials
# from a single URL

import bpy

addon_idname = __package__.split(".")[0]

# -----------------------------------------------------------------------------

def getPreferences(context=None):
    if context is None: context = bpy.context
    preferences = context.preferences
    addon_preferences = preferences.addons[addon_idname].preferences
    return addon_preferences

# -----------------------------------------------------------------------------

class LilySurfaceScrapperPreferences(bpy.types.AddonPreferences):
    bl_idname = addon_idname

    texture_dir: bpy.props.StringProperty(
        name="Texture Directory",
        subtype='DIR_PATH',
        default="LilySurface",
    )

    use_ao: bpy.props.BoolProperty(
        name="Use AO map",
        default=False,
    )

    use_ground_hdri: bpy.props.BoolProperty(
        name="Use Ground HDRI",
        default=False,
    )

    use_strength: bpy.props.BoolProperty(
        name="Use Energy Value",
        default=True,
    )

    light_strength: bpy.props.BoolProperty(
        name="Use in strength node",
        default=False,
    )

    load_map: bpy.props.BoolProperty(
        name="Load map internally",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="The texture directory where the textures are downloaded.")
        layout.label(text="It can either be relative to the blend file, or global to all files.")
        layout.label(text="If it is relative, you must always save the blend file before importing materials and worlds.")
        layout.prop(self, "texture_dir")

        layout.separator()
        layout.label(text="The AO map provided with some material must not be used")
        layout.label(text="in a standard surface shader. Nevertheless, you can enable")
        layout.label(text="using it as a multiplicator over base color.")
        layout.prop(self, "use_ao")

        layout.separator()
        layout.label(text="Ground HDRI projects the environment maps so that it creates a proper ground.")
        layout.prop(self, "use_ground_hdri")

        layout.separator()
        layout.label(text="Use the energy value on IES library to determine the strength of lamp")
        layout.prop(self, "use_strength")
        if bool(self.use_strength):
            layout.label(text="Put the energy value in the strength socket of the ies map instead of the lamp energy")
            layout.prop(self, "light_strength")
        layout.label(text="Load map internally rather then linking to the file")
        layout.prop(self, "load_map")

# -----------------------------------------------------------------------------

classes = (LilySurfaceScrapperPreferences,)

register, unregister = bpy.utils.register_classes_factory(classes)
