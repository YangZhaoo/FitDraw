from __future__ import annotations
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import math


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

    def __str__(self):
        return f"{self.longitude}, {self.latitude}"


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
