from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class Location(BaseModel):
    latitude: float
    longitude: float

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"


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
