from typing import List
from garmin_fit_sdk import Decoder, Stream

from .base import Parser
from .protocol import Record, Location


class FitParser(Parser):

    def __init__(self, file):
        super().__init__(file)

    """
        timestamp

        speed： unit Km/h
        distance: unit m

        position_lat
        position_long

        altitude
        grade
        temperature

        enhanced_altitude
        enhanced_speed
    """
    def parser(self) -> List[Record]:
        stream = Stream.from_file(self._file)
        decoder = Decoder(stream)
        messages, _ = decoder.read()
        raw_records = messages['record_mesgs']
        res = []
        for raw_record in raw_records:
            record = Record(
                date_time=raw_record['timestamp'],
                timestamp=int(raw_record['timestamp'].timestamp()),
                speed=round(raw_record['speed'] * 3.6, 1) if 'speed' in raw_record else None,
                distance=raw_record['distance'] if 'distance' in raw_record else None,
                location=self._convert_to_location(raw_record['position_lat'], raw_record['position_long']) if 'position_lat' in raw_record and 'position_long' in raw_record else None
            )
            res.append(record)
        return res

    def _convert_to_location(self, position_lat: int, position_long: int) -> Location:
        # 圆度转经纬度
        latitude = position_lat * (180 / pow(2, 31))
        longitude = position_long * (180 / pow(2, 31))
        return Location(latitude=latitude, longitude=longitude)