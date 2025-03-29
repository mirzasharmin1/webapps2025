import logging
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from timestamp_service.thrift_gen.timestamp import TimestampService

logger = logging.getLogger(__name__)


def get_timestamp(host='127.0.0.1', port=10000):
    """
    Get a timestamp from the Thrift timestamp service

    Returns:
        str: Current timestamp in format 'YYYY-MM-DD HH:MM:SS.ffffff'
        None: If an error occurs
    """
    try:
        transport = TSocket.TSocket(host, port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = TimestampService.Client(protocol)

        transport.open()

        timestamp = client.getTimestamp()

        transport.close()

        return timestamp

    except Exception as e:
        logger.error(f"Error getting timestamp from Thrift service: {e}")
        return None
