# Copyright (c) 2019 Elie Michel
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

from .AbstractScrapper import AbstractScrapper
import os

class TextureHavenScrapper(AbstractScrapper):
    source_name = "Texture Haven"
    home_url = "https://texturehaven.com/textures/"
    home_dir ="texturehaven"

    @classmethod
    def canHandleUrl(cls, url):
        """Return true if the URL can be scrapped by this scrapper."""
        return url.startswith("https://texturehaven.com/tex")
    
    def fetchVariantList(self, url):
        """Get a list of available variants.
        The list may be empty, and must be None in case of error."""
        html = self.fetchHtml(url)
        if html is None:
            return None

        maps = html.xpath("//div[@class='download-buttons']//div[@class='map-type']")

        variants = maps[0].xpath(".//div[@class='res-item']/a/div/text()")
        variants = [self.clearString(s) for s in variants]

        try:
            self._thumbnailUrl = "https://texturehaven.com"+html.xpath("//div[@id='item-preview']/img")[0].attrib["src"]
        except:
            pass

        self._html = html
        self._maps = maps
        self._variants = variants
        self._base_name = html.xpath("//title/text()")[0].split('|')[0].strip().replace("_", " ").title()

        self.createMetadetaFile(url, self._base_name, variants)
        return variants
    
    def fetchVariant(self, variant_index, material_data, reinstall=False):
        """Fill material_data with data from the selected variant.
        Must fill material_data.name and material_data.maps.
        Return a boolean status, and fill self.error to add error messages."""
        # Get data saved in fetchVariantList
        maps = self._maps
        variants = self._variants
        
        if variant_index < 0 or variant_index >= len(variants):
            self.error = "Invalid variant index: {}".format(variant_index)
            return False
        
        var_name = variants[variant_index]
        material_data.name = os.path.join(self.home_dir, self._base_name, var_name)

        if self.savedVariants is not None:
            self.savedVariants[var_name] = True

        self.saveThumbnail(self._thumbnailUrl, self._base_name)

        # Translate TextureHaven map names into our internal map names
        maps_tr = {
            'Albedo': 'baseColor',
            'Col 1': 'baseColor',
            'Col 01': 'baseColor',
            'Col 2': 'baseColor_02',
            'Col 02': 'baseColor_02',
            'Col 3': 'baseColor_03',
            'Col 03': 'baseColor_03',
            'Diffuse': 'diffuse',
            'Diff Png': 'diffuse',
            'Normal': 'normal',
            'Specular': 'specular',
            'Roughness': 'roughness',
            'Metallic': 'metallic',
            'AO': 'ambientOcclusion',
            'Rough Ao': 'ambientOcclusionRough',
            'Displacement': 'height',
        }

        for m in maps:
            map_name = m.xpath("div[@class='map-download']//text()")[0]
            map_url = "https://texturehaven.com" + m.xpath(".//div[@class='res-item']/a/@href")[variant_index]
            if map_name in maps_tr:
                map_name = maps_tr[map_name]
                material_data.maps[map_name] = self.fetchImage(map_url, material_data.name, map_name,
                                                               reinstall=reinstall)
        
        return True

    def isDownloaded(self, variantName):
        if self.savedVariants is None:
            self.savedVariants = {i: False for i in self._variants}
            for i in os.listdir(self.getTextureDirectory(os.path.join(self.home_dir, self._base_name))):
                if i in self.savedVariants:
                    self.savedVariants[i] = True

        return self.savedVariants[variantName]
