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

import os
from os import path

from .AbstractScrapper import AbstractScrapper


class LocalDirectoryScrapper(AbstractScrapper):
    """
    This scrapper does not actually scrap a website, it links textures from a
    local directory, trying to guess the meaning of textures from their names.
    """
    source_name = "Local Directory"
    home_url = None
    home_dir = ""

    _texture_cache = None

    @classmethod
    def canHandleUrl(cls, url):
        """Return true if the URL can be scrapped by this scrapper."""
        print(f"test: {url}")
        return path.isdir(url)

    def fetchVariantList(self, url):
        """Get a list of available variants.
        The list may be empty, and must be None in case of error."""
        self._directory = url
        return [url]

    def fetchVariant(self, variant_index, material_data, reinstall=False):
        d = self._directory

        # todo implement reinstall  create metadata file containing link to page

        material_data.name = path.basename(path.dirname(d)) + "/" + path.basename(d)

        namelist = [f for f in os.listdir(d) if path.isfile(path.join(d, f))]
        
        # TODO: Find a more exhaustive list of prefix/suffix
        maps_tr = {
            'baseColor': 'baseColor',
            'metallic': 'metallic',
            'height': 'height',
            'normalInvertedY': 'normalInvertedY',
            'opacity': 'opacity',
            'roughness': 'roughness',
            'ambientOcclusion': 'ambientOcclusion',
            'normal': 'normal',

            'Base Color': 'baseColor',
            'Metallic': 'metallic',
            'Height': 'height',
            'col': 'baseColor',
            'nrm': 'normalInvertedY',
            'mask': 'opacity',
            'rgh': 'roughness',
            'met': 'metallic',
            'AO': 'ambientOcclusion',
            'disp': 'height',
            'Color': 'baseColor',
            'Normal': 'normalInvertedY',
            'Opacity': 'opacity',
            'Roughness': 'roughness',
            'Metalness': 'metallic',
            'AmbientOcclusion': 'ambientOcclusion',
            'Displacement': 'height'
        }
        for name in namelist:
            base = os.path.splitext(name)[0]
            map_type = base.split('_')[-1]
            for k, map_name in maps_tr.items():
                if k in base:
                    map_name = maps_tr[k]
                    material_data.maps[map_name] = path.join(d, name)
        return True

    def isDownloaded(self, variantName):
        return True  # False?  todo this needs impovment
