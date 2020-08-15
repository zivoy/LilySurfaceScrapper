from .ScrappersManager import ScrappersManager
from .ScrappedData import ScrappedData

class LightData(ScrappedData):
    """Internal representation of world, responsible on one side for
    scrapping texture providers and on the other side to build blender materials.
    This class must not use the Blender API. Put Blender related stuff in subclasses
    like CyclesMaterialData."""
    
    def reset(self):
        self.name = "Lily World"
        self.maps = {
            'ies': None,
            'energy': None
        }

    @classmethod
    def makeScrapper(cls, url):
        for S in ScrappersManager.getScrappersList():
            if 'LIGHT' in S.scrapped_type and S.canHandleUrl(url):
                return S()
        return None
    
    def loadImages(self):
        """Implement this in derived classes"""
        raise NotImplementedError

    def createLights(self):
        """Implement this in derived classes"""
        raise NotImplementedError
