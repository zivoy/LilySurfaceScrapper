import bpy

from .LightData import LightData
from .cycles_utils import autoAlignNodes


class CyclesLightData(LightData):
    def createLights(self):
        light = bpy.context.object.data

        light.use_nodes = True
        light.type = "POINT"

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
        iesNode.mode = "EXTERNAL"
        iesNode.filepath = ies

        links.new(iesNode.outputs['Fac'], emmision.inputs["Strength"])

        value = nodes.new(type="ShaderNodeValue")
        value.outputs['Value'].default_value = energy
        links.new(value.outputs["Value"], iesNode.inputs["Strength"])

        autoAlignNodes(out)
