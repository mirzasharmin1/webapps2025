import datetime
from timestamp_service.thrift_gen.timestamp import TimestampService


class TimestampHandler(TimestampService.Iface):
    def getTimestamp(self):
        """Return the current timestamp as a formatted string"""
        current_time = datetime.datetime.now()
        return current_time.strftime("%Y-%m-%d %H:%M:%S.%f")
