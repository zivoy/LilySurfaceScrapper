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

import os
import string

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "site-packages"))
from lxml import etree

import requests
import shutil
import json

from ..settings import TEXTURE_DIR
from ..preferences import getPreferences

class AbstractScrapper():
    # Can be 'MATERIAL', 'WORLD', 'LIGHT'
    scrapped_type = {'MATERIAL'}
    # The name of the scrapped source, displayed in UI
    source_name = "<Abstract>"
    # The URL of the source's home, used for the list of availabel sources in panels
    home_url = None
    # The home directory of the scraper
    home_dir = "Abstract"

    metadataFilename = ".metadata"
    savedVariants = None

    @classmethod
    def canHandleUrl(cls, url):
        raise NotImplementedError

    def __init__(self, texture_root=""):
        self._base_name = None
        self._thumbnailUrl = None
        self.error = None
        self.texture_root = texture_root

    @classmethod
    def _fetch(cls, url):
        headers = {"User-Agent":"Mozilla/5.0"}  # fake user agent
        r = requests.get(url if "https://" in url else "https://" + url, headers=headers)
        if r.status_code != 200:
            return None
        else:
            return r

    def fetchHtml(self, url):
        """Get a lxml.etree object representing the scrapped page.
        Use xpath queries to browse it."""
        r = __class__._fetch(url)
        if r is not None:
            return etree.HTML(r.text)
        else:
            self.error = "URL not found: {}".format(url)

    def fetchJson(self, url):
        r = __class__._fetch(url)
        if r is not None:
            return r.json()
        else:
            self.error = "URL not found: {}".format(url)

    def fetchXml(self, url):
        """Get a lxml.etree object representing the scrapped page.
        Use xpath queries to browse it."""
        r = __class__._fetch(url)
        if r is not None:
            return etree.fromstring(r.text)
        else:
            self.error = "URL not found: {}".format(url)

    def getRedirection(self, url):
        headers = {"User-Agent":"Mozilla/5.0"}  # fake user agent
        url = url if "https://" in url else "https://" + url
        r = requests.get(url, headers=headers, allow_redirects=False)
        if r.status_code == 302:
            return r.headers.get("Location")
        else:
            return None

    def getTextureDirectory(self, material_name):
        """Return the texture dir, relative to the blend file, dependent on material's name"""
        texture_dir = getPreferences().texture_dir
        if texture_dir == "":
            texture_dir = TEXTURE_DIR
        if texture_dir.startswith("//"):
            texture_dir = texture_dir[2:]
        if not os.path.isabs(texture_dir):
            texture_dir = os.path.realpath(os.path.join(self.texture_root, texture_dir))
        name_path = material_name.replace('/',os.path.sep)
        dirpath = os.path.join(texture_dir, name_path)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        return dirpath

    def fetchImage(self, url, material_name, map_name, force_ext=False, reinstall=False):
        """Utility helper for download textures"""
        root = self.getTextureDirectory(material_name)
        if not force_ext:
            ext = os.path.splitext(url)[1]
            map_name = map_name + ext
        path = os.path.join(root, map_name)
        if os.path.isfile(path) and not reinstall:
            print("Using cached {}.".format(url))
        else:
            print("Downloading {}...".format(url))
            headers = {"User-Agent":"Mozilla/5.0"}  # fake user agent
            r = requests.get(url, stream=True, headers=headers)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            else:
                self.error = "URL not found: {}".format(url)
                return None
        return path

    def fetchZip(self, url, material_name, zip_name):
        """Utility helper for download textures"""
        root = self.getTextureDirectory(material_name)
        path = os.path.join(root, zip_name)
        if os.path.isfile(path):
            print("Using cached {}.".format(url))
        else:
            print("Downloading {}...".format(url))
            headers = {"User-Agent":"Mozilla/5.0"}  # fake user agent
            r = requests.get(url, stream=True, headers=headers)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            else:
                self.error = "URL not found: {}".format(url)
                return None
        return path

    def fetchText(self, url, material_name, filename):
        root = self.getTextureDirectory(material_name)
        path = os.path.join(root, filename)
        if os.path.isfile(path):
            return path
        data = self._fetch(url)
        with open(path, "wb") as f:
            f.write(data.content)
        data.close()
        return path

    def clearString(self, s):
        """Remove non printable characters"""
        printable = set(string.printable)
        return ''.join(filter(lambda x: x in printable, s))

    def fetchVariantList(self, url):
        """Get a list of available variants.
        The list may be empty, and must be None in case of error."""
        raise NotImplementedError

    def fetchVariant(self, variant_index, material_data, reinstall):
        """Fill material_data with data from the selected variant.
        Must fill material_data.name and material_data.maps.
        Return a boolean status, and fill self.error to add error messages.
        should be used to specify if to force redownload or use existing textures"""
        raise NotImplementedError


    def isDownloaded(self, variantName):
        """Return True or False based on if the given variant name is present on the system
        this should be done by checking against savedVariants which should be a dict, and should be populated if None.
        """
        raise NotImplementedError

    def createMetadetaFile(self, url, matName, variants: list):
        """create a metadata file with the link of the item so that it can be called upon for thumbnails"""
        directory = self.getTextureDirectory(os.path.join(self.home_dir, matName))
        metadataPath = os.path.join(directory, self.metadataFilename)
        if not os.path.isfile(metadataPath):
            with open(metadataPath, "w") as metadata:
                json.dump({"url": url, "variants": variants}, metadata)

        return metadataPath

    def saveThumbnail(self, url, matName):
        """save the thumbnail given the material name and url"""
        directory = os.path.join(self.home_dir, matName)
        if self._thumbnailUrl is None or self._base_name is None:
            return None
        return self.fetchImage(url, directory, "thumbnail")

    def getAndSaveThumbnail(self, itemUrl):
        if self.canHandleUrl(itemUrl):
            self.fetchVariantList(itemUrl)
        else:
            print(f"'{itemUrl}' is a bad url -- {self.source_name}")
            return None
        return self.saveThumbnail(self._thumbnailUrl, self._base_name)

