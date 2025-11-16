from __future__ import annotations

import numpy as np
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import math


class GeoInfo(BaseModel):
    province: str
    city: str
    district: str
    township: str
    street: str

    def getSimpleInfo(self):
        if self.street is not None and len(self.street) > 0:
            return f"{self.district}{self.street}"
        else:
            return f"{self.province}{self.city}{self.district}"

    def __str__(self):
        return f"{self.province}{self.city}{self.district}{self.township}{self.street}"


class Location(BaseModel):
    latitude: float
    longitude: float

    def getAngle(self, to_position: Location) -> float:
        """
        计算目标坐标相较于当前坐标的方位，返回角度值
        :param to_position:
        :return: 角度
        """
        delta_latitude = to_position.latitude - self.latitude
        delta_longitude = to_position.longitude - self.longitude
        if delta_longitude == 0:
            return 90.0 if delta_latitude > 0 else -90.0  # 正北或正南
        return math.degrees(math.atan2(delta_latitude, delta_longitude))

    def getNpArray(self):
        return np.array([self.longitude, self.latitude])

    def __str__(self):
        return f"{self.longitude:.6f}, {self.latitude:.6f}"


class Record(BaseModel):
    timestamp: int  # unit: second
    date_time: datetime
    speed: Optional[float]
    location: Optional[Location]
    distance: Optional[float]

    def __str__(self):
        return (f"record info:\n"
                f"timestamp: {self.timestamp}\n"
                f"date time: {self.date_time.astimezone()}\n"
                f"speed: {round(self.speed / 3.6, 2) if self.speed is not None else '--'} m/s\n"
                f"location: {self.location if self.location is not None else '--'}\n"
                f"distance: {self.distance}m\n")
