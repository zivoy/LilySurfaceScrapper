import bpy

from .LightData import LightData
from .cycles_utils import autoAlignNodes
from .preferences import getPreferences
import os


class CyclesLightData(LightData):
    def createLights(self):
        pref = getPreferences()
        light = bpy.context.object.data

        light.use_nodes = True
        light.type = "POINT"
        light.shadow_soft_size = 0

        nodes = light.node_tree.nodes
        links = light.node_tree.links

        nodes.clear()

        ies = self.maps['ies']
        energyPath = self.maps['energy']
        with open(energyPath, "r") as f:
            energy = float(f.read())

        out = nodes.new(type="ShaderNodeOutputLight")
        emmision = nodes.new(type="ShaderNodeEmission")
        links.new(out.inputs['Surface'], emmision.outputs['Emission'])

        iesNode = nodes.new(type="ShaderNodeTexIES")
        if pref.load_map:
            bpy.ops.text.open(filepath=ies, internal=True)
            name = f"{os.path.basename(os.path.dirname(ies))}.ies"
            bpy.data.texts["lightData.ies"].name = name
            iesNode.ies = bpy.data.texts[name]
        else:
            iesNode.mode = "EXTERNAL"
            iesNode.filepath = ies
        links.new(iesNode.outputs['Fac'], emmision.inputs["Strength"])

        if pref.use_strength:
            if pref.light_strength:
                value = nodes.new(type="ShaderNodeValue")
                value.outputs['Value'].default_value = energy
                links.new(value.outputs["Value"], iesNode.inputs["Strength"])
            else:
                light.energy = energy

        autoAlignNodes(out)
