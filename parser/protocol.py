from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class Location(BaseModel):
    latitude: float
    longitude: float


class Record(BaseModel):
    timestamp: int  # unit: second
    date_time: datetime
    speed: Optional[float]
    location: Optional[Location]
    distance: Optional[float]
