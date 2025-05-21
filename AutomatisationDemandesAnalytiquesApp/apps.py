# AutomatisationDemandesAnalytiquesApp/apps.py
from django.apps import AppConfig
from django import dispatch
from django.core.signals import request_finished


import atexit
import logging

logger = logging.getLogger(__name__)

class AutomatisationDemandesAnalytiquesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AutomatisationDemandesAnalytiquesApp'
