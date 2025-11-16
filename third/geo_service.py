from abc import ABC, abstractmethod
from parser import Location, GeoInfo


class GeoService(ABC):

    @abstractmethod
    def regeo(self, location: Location) -> GeoInfo:
        pass
