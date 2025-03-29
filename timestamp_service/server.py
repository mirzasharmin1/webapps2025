import threading
import logging
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from timestamp_service.thrift_gen.timestamp import TimestampService
from timestamp_service.thrift_handler import TimestampHandler

logger = logging.getLogger(__name__)


class ThriftServer:
    def __init__(self, port=10000):
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False

    def start(self):
        if self.is_running:
            logger.warning("Thrift server is already running")
            return

        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True  # Make thread exit when main thread exits
        self.server_thread.start()
        self.is_running = True
        logger.info(f"Thrift timestamp server started on port {self.port}")

    def _run_server(self):
        handler = TimestampHandler()
        processor = TimestampService.Processor(handler)

        transport = TSocket.TServerSocket(host='127.0.0.1', port=self.port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        self.server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

        try:
            logger.info("Starting the Thrift timestamp server...")
            self.server.serve()
        except Exception as e:
            logger.error(f"Error in Thrift server: {e}")
            self.is_running = False

    def stop(self):
        if self.server and self.is_running:
            logger.info("Stopping Thrift timestamp server...")
            self.server.stop()
            self.is_running = False
