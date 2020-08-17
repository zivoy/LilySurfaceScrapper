import os
import re
from .AbstractScrapper import AbstractScrapper


class IesLibraryScrapper(AbstractScrapper):
    scrapped_type = {'LIGHT'}
    source_name = "IES Library"
    home_url = "https://ieslibrary.com"
    home_dir = "ieslibrary"

    pattern = r"https://ieslibrary\.com/en/browse#ies-(.+)"

    @classmethod
    def canHandleUrl(cls, url):
        """Return true if the URL can be scrapped by this scrapper."""
        return re.match(cls.pattern, url) is not None

    def fetchVariantList(self, url):
        """Get a list of available variants.
        The list may be empty, and must be None in case of error."""

        asset_id = re.match(self.pattern, url).group(1)

        api_url = f"https://ieslibrary.com/en/browse/data.json?ies={asset_id}"

        data = self.fetchJson(api_url)
        if data is None:
            return None


        self._download_url = data["downloadUrlIes"]
        self._blender_energy = data["energy"]
        self._base_name = asset_id
        self._variant = data["lumcat"]

        self.createMetadetaFile(url, asset_id, [self._variant,])
        try:
            self._thumbnailUrl = data["preview"]
        except:
            pass
        return [self._variant,]

    def fetchVariant(self, variant_index, material_data, reinstall=False):
        """Fill material_data with data from the selected variant.
        Must fill material_data.name and material_data.maps.
        Return a boolean status, and fill self.error to add error messages."""
        # Get data saved in fetchVariantList
        download_url = self._download_url
        blender_energy = self._blender_energy
        variant = self._variant

        if variant_index < 0 or variant_index >= len([variant]):
            self.error = "Invalid variant index: {}".format(variant_index)
            return False

        material_data.name = os.path.join(self.home_dir, self._base_name, variant)

        self.saveThumbnail(self._thumbnailUrl, self._base_name)

        if reinstall or not self.isDownloaded(variant):

            data_file = self.fetchText(download_url, material_data.name, "lightData.ies")
            data_dir = os.path.dirname(data_file)
            with open(os.path.join(data_dir, "lightEnergy"), "w+") as f:
                f.write(str(blender_energy))

            if self.savedVariants is not None:
                self.savedVariants[variant] = True
        else:
            data_dir = self.getTextureDirectory(material_data.name)

        material_data.maps["ies"] = os.path.join(data_dir, "lightData.ies")
        material_data.maps["energy"] = os.path.join(data_dir, "lightEnergy")
        return True

    def isDownloaded(self, variantName):
        if self.savedVariants is None:
            self.savedVariants = {self._variant: False, }
            for i in os.listdir(self.getTextureDirectory(os.path.join(self.home_dir, self._base_name))):
                if i in self.savedVariants:
                    self.savedVariants[i] = True

        return self.savedVariants[variantName]
