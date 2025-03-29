from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class TimestampServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timestamp_service'

    def ready(self):
        """Start the Thrift server when Django is ready"""
        import sys
        if 'runserver' in sys.argv or 'runserver_plus' in sys.argv:
            try:
                from timestamp_service.server import ThriftServer
                # Start the server
                thrift_server = ThriftServer(port=10000)
                thrift_server.start()
                logger.info("Thrift timestamp server initialized")
            except Exception as e:
                logger.error(f"Failed to start Thrift server: {e}")
