# AutomatisationDemandesAnalytiquesApp/apps.py
from django.apps import AppConfig
from django import dispatch
from django.core.signals import request_finished
from Db_handler import EmailDatabase_instance
import atexit
import logging

logger = logging.getLogger(__name__)

class AutomatisationDemandesAnalytiquesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AutomatisationDemandesAnalytiquesApp'

    def ready(self):
        # Close pool on server shutdown
        def close_db_pool():
            logger.debug("Closing database connection pool on shutdown")
            EmailDatabase_instance.close()
        atexit.register(close_db_pool)

        # Optional: Close pool after each request (use with caution)
        def close_db_pool_request(sender, **kwargs):
            logger.debug("Closing database connection pool after request")
            EmailDatabase_instance.close()
        dispatch.receiver(request_finished)(close_db_pool_request)